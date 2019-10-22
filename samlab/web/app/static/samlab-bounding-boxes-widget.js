// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([
    "debug",
    "knockout",
    "knockout.mapping",
    "samlab-dashboard",
    "samlab-identity",
    "samlab-server",
    ], function(debug, ko, mapping, dashboard, identity, server)
{
    var component_name = "samlab-bounding-boxes-widget";
    var log = debug(component_name);

    ko.components.register(component_name,
    {
        viewModel:
        {
            createViewModel: function(widget, component_info)
            {
                var component = mapping.fromJS({
                    annotations: [],
                    color: widget.params.color(),
                    current_annotation: null,
                    key: widget.params.key(),
                    metadata: {size: []},
                    mode: "add",
                    oid: widget.params.oid(),
                    otype: widget.params.otype(),
                    title: "Bounding Boxes Editor",
                    username: identity.username,
                });

                component.mode_items =
                [
                    {key: "add", label: "<span class='text-success fa fa-plus fa-fw'/>&nbsp;Add"},
                    //{key: "edit", label: "<span class='text-dark fa fa-pencil fa-fw'/>&nbsp;Edit"},
                    {key: "delete", label: "<span class='text-danger fa fa-trash fa-fw'/>&nbsp;Delete"},
                ];

                component.color_items =
                [
                    {key: "red", label: "<span style='color: red' class='fa fa-square fa-fw'></span>"},
                    {key: "orange", label: "<span style='color: orange' class='fa fa-square fa-fw'></span>"},
                    {key: "yellow", label: "<span style='color: yellow' class='fa fa-square fa-fw'></span>"},
                    {key: "green", label: "<span style='color: green' class='fa fa-square fa-fw'></span>"},
                    {key: "cyan", label: "<span style='color: cyan' class='fa fa-square fa-fw'></span>"},
                    {key: "blue", label: "<span style='color: blue' class='fa fa-square fa-fw'></span>"},
                    {key: "purple", label: "<span style='color: purple' class='fa fa-square fa-fw'></span>"},
                ];

                component.src = ko.pureComputed(function()
                {
                    return "/" + component.otype() + "/" + component.oid() + "/content/" + component.key() + "/data";
                });

                component.metadata.size_formatted = ko.pureComputed(function()
                {
                    return component.metadata.size().join(" \u00d7 ");
                });

                component.viewbox = ko.pureComputed(function()
                {
                    return "0 0 " + component.metadata.size()[0] + " " + component.metadata.size()[1];
                });

                component.clear = function()
                {
                    component.annotations([]);
                    component.save_annotations();
                }

                component.on_click_box = function(item, event)
                {
                    if(component.mode() == "delete")
                    {
                        component.annotations.remove(item);
                        component.save_annotations();
                        event.stopPropagation();
                    }
                }

                component.on_mousedown = function(parent, event)
                {
                    if(component.mode() == "add")
                    {
                        component.current_annotation(mapping.fromJS({
                            bbox: [event.offsetX, event.offsetY, 0, 0],
                            bbox_mode: "XYWH_ABS",
                            color: component.color(),
                            username: component.username(),
                            key: component.key(),
                        }));
                        component.annotations.push(component.current_annotation());
                        event.stopPropagation();
                    }
                }

                component.on_mousemove = function()
                {
                    if(component.current_annotation() != null)
                    {
                        var bbox = component.current_annotation().bbox();

                        var newx = event.offsetX;
                        var newy = event.offsetY;

                        bbox[0] = Math.min(bbox[0], newx);
                        bbox[1] = Math.min(bbox[1], newy);
                        bbox[2] = Math.max(0, newx - bbox[0]);
                        bbox[3] = Math.max(0, newy - bbox[1]);

                        component.current_annotation().bbox(bbox);
                    }
                }

                component.on_mouseup = function()
                {
                    if(component.current_annotation() != null)
                    {
                        component.current_annotation(null);
                        component.save_annotations();
                    }
                }

                component.load_annotations = ko.computed(function()
                {
                    server.get_json("/" + component.otype() + "/" + component.oid() + "/attributes",
                    {
                        success: function(attributes)
                        {
                            attributes = mapping.fromJS(attributes);
                            log("load_annotations", attributes);
                            if("samlab:annotations" in attributes.attributes)
                            {
                                component.annotations(attributes.attributes["samlab:annotations"]());
                            }
                        },
                    });
                });

                component.save_annotations = function()
                {
                    var payload = {"samlab:annotations": mapping.toJS(component.annotations())};
                    server.put_json("/" + component.otype() + "/" + component.oid() + "/attributes", payload);
                }

                //component.load_annotations();

                server.load_json(component, "/" + component.otype() + "/" + component.oid() + "/content/" + component.key() + "/image/metadata");

                log("component", component);

                return component;
            },
        },
        template: { require: "text!" + component_name + ".html" }
    });

    var module =
    {
        widget: { params: {otype: null, oid: null, key: null, color: "yellow"}},
    };

    return module;
});

