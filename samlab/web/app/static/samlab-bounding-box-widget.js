// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([
    "debug",
    "element-resize-event",
    "jquery",
    "knockout",
    "knockout.mapping",
    "samlab-bounding-box-manager",
    "samlab-dashboard",
    "samlab-dialog",
    "samlab-identity-manager",
    "samlab-object-manager",
    "samlab-server",
    ], function(debug, element_resize, jquery, ko, mapping, bounding_box_manager, dashboard, dialog, identity_manager, object, server)
{
    var component_name = "samlab-bounding-box-widget";
    var log = debug(component_name);

    ko.components.register(component_name,
    {
        viewModel:
        {
            createViewModel: function(widget, component_info)
            {
                var container = jquery(component_info.element.querySelector(".img-overlay-wrap"));

                var component = mapping.fromJS({
                    attributes: {'samlab:annotations': []},
                    category: widget.params.category,
                    color: widget.params.color,
                    current_annotation: null,
                    display_height: container.innerHeight(),
                    display_width: container.innerWidth(),
                    key: widget.params.key() || bounding_box_manager.key,
                    metadata: {size: [0, 0]},
                    mode: "add",
                    mousex: 0,
                    mousey: 0,
                    oid: widget.params.oid() || bounding_box_manager.oid,
                    otype: widget.params.otype() || bounding_box_manager.otype,
                    username: identity_manager.username,
                    x1: null,
                    x2: null,
                    y1: null,
                    y2: null,
                });

                element_resize(container[0], function()
                {
                    component.display_width(container.innerWidth());
                    component.display_height(container.innerHeight());
                });

                var change_subscription = object.changed.subscribe(function(object)
                {
                    if(component.otype() == object.otype && component.oid() == object.oid)
                    {
                        component.load_annotations();
                    }
                });

                component.dispose = function()
                {
                    change_subscription.dispose();
                }

                component.image_loaded = function()
                {
                    component.display_width(container.innerWidth());
                    component.display_height(container.innerHeight());
                }

                component.mode_items =
                [
                    {key: "add", label: "<span class='text-success fa fa-plus fa-fw'/>&nbsp;Add"},
                    //{key: "edit", label: "<span class='text-dark fa fa-pencil fa-fw'/>&nbsp;Edit"},
                    {key: "delete", label: "<span class='text-danger fa fa-trash fa-fw'/>&nbsp;Delete"},
                ];

                component.delete_mode = ko.computed(function()
                {
                    return component.mode() == "delete";
                });

                component.color_items =
                [
                    {key: "red", label: "<span style='color: red' class='fa fa-square fa-fw'></span>"},
                    {key: "orange", label: "<span style='color: orange' class='fa fa-square fa-fw'></span>"},
                    {key: "yellow", label: "<span style='color: yellow' class='fa fa-square fa-fw'></span>"},
                    {key: "green", label: "<span style='color: green' class='fa fa-square fa-fw'></span>"},
                    {key: "cyan", label: "<span style='color: cyan' class='fa fa-square fa-fw'></span>"},
                    {key: "blue", label: "<span style='color: blue' class='fa fa-square fa-fw'></span>"},
                    {key: "purple", label: "<span style='color: purple' class='fa fa-square fa-fw'></span>"},
                    {key: "black", label: "<span style='color: black' class='fa fa-square fa-fw'></span>"},
                    {key: "white", label: "<span style='color: black' class='fa fa-square-o fa-fw'></span>"},
                ];

                component.src = ko.computed(function()
                {
                    var otype = component.otype();
                    var oid = component.oid();
                    var key = component.key();

                    if(otype != null && oid != null && key != null)
                    {
                        return "/" + otype + "/" + oid + "/content/" + key + "/data";
                    }

                    return "";
                });

                component.viewbox = ko.pureComputed(function()
                {
                    return "0 0 " + component.metadata.size()[0] + " " + component.metadata.size()[1];
                });

                component.load_metadata = ko.computed(function()
                {
                    var otype = component.otype();
                    var oid = component.oid();
                    var key = component.key();

                    if(otype != null && oid != null && key != null)
                    {
                        server.load_json(component, "/" + otype + "/" + oid + "/content/" + key + "/image/metadata");
                    }
                });

                component.load_annotations = function()
                {
                    var otype = component.otype();
                    var oid = component.oid();

                    component.attributes["samlab:annotations"]([]);

                    if(otype != null && oid != null)
                    {
                        server.load_json(component, "/" + otype + "/" + oid + "/attributes");
                    }
                };

                component.update_annotations = ko.computed(function()
                {
                    component.load_annotations();
                });

                component.save_annotations = function()
                {
                    var payload = {"samlab:annotations": mapping.toJS(component.attributes["samlab:annotations"]())};
                    server.put_json("/" + component.otype() + "/" + component.oid() + "/attributes", payload);
                }

                component.clear = function()
                {
                    component.attributes["samlab:annotations"]([]);
                    component.save_annotations();
                }

                component.on_click_box = function(item, event)
                {
                    if(component.mode() == "delete")
                    {
                        component.attributes["samlab:annotations"].remove(item);
                        component.save_annotations();
                        event.stopPropagation();
                    }
                }

                var update_mouse = function(e)
                {
                    component.mousex(e.offsetX / component.display_width() * component.metadata.size()[0]);
                    component.mousey(e.offsetY / component.display_height() * component.metadata.size()[1]);
                }

                component.on_mousedown = function(item, e)
                {
                    update_mouse(e);

                    if(component.mode() == "add")
                    {
                        if(!component.category())
                        {
                            dialog.dialog(
                            {
                                buttons: [{label: "Close", class_name: "btn-secondary"}],
                                message: "<span class=''>You must specify a category first.</span><br/><span class='text-muted small'>Ensure that you use consistent spelling and case for categories, and that you coordinate with your team members on category names.</span>",
                                title: "Add Bounding Box",
                            });

                            return;
                        }

                        component.x1(component.mousex());
                        component.y1(component.mousey());
                        component.x2(component.mousex());
                        component.y2(component.mousey());

                        component.current_annotation(mapping.fromJS({
                            bbox: [component.x1(), component.y1(), 0, 0],
                            bbox_mode: "XYWH_ABS",
                            category: component.category(),
                            color: component.color(),
                            username: component.username(),
                            key: component.key(),
                        }));
                        component.attributes["samlab:annotations"].push(component.current_annotation());
                        event.stopPropagation();
                    }
                }

                component.on_mousemove = function(item, e)
                {
                    update_mouse(e);

                    if(component.current_annotation() != null)
                    {
                        component.x2(component.mousex());
                        component.y2(component.mousey());

                        var bbox = [0, 0, 0, 0];

                        bbox[0] = Math.min(component.x1(), component.x2());
                        bbox[1] = Math.min(component.y1(), component.y2());
                        bbox[2] = Math.abs(component.x1() - component.x2());
                        bbox[3] = Math.abs(component.y1() - component.y2());

                        component.current_annotation().bbox(bbox);
                    }
                }

                component.on_mouseup = function(item, e)
                {
                    update_mouse(e);

                    if(component.current_annotation() != null)
                    {
                        component.current_annotation(null);
                        component.save_annotations();
                    }
                }

                return component;
            },
        },
        template: { require: "text!" + component_name + ".html" }
    });

    var module =
    {
        widget: { params: {otype: null, oid: null, key: null, category: "", color: "yellow"}},
    };

    return module;
});

