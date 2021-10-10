// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([
    "bootstrap",
    "debug",
    "knockout",
    "knockout.mapping",
    "lodash",
    "URI",
    "samlab-dashboard",
    "samlab-notify",
    "samlab-permissions",
    "samlab-server",
    "samlab-socket",
    "samlab-uuidv4",
    ], function(bootstrap, debug, ko, mapping, lodash, URI, dashboard, notify, permissions, server, socket, uuidv4)
{
    var component_name = "samlab-images-widget";
    var log = debug(component_name);

    ko.components.register(component_name,
    {
        viewModel:
        {
            createViewModel: function(widget, component_info)
            {
                var component = mapping.fromJS(
                {
                    bboxes: [],
                    bboxes_category: null,
                    bboxes_id: "w" + uuidv4(),
                    bboxes_mode: "view",
                    bboxes_svg_id: "w" + uuidv4(),
                    bboxes_visible: widget.params.bboxes,
                    collection: widget.params.collection,
                    color: "yellow",
                    count: null,
                    height: 0,
                    index: widget.params.index,
                    metadata: null,
                    metaid: "w" + uuidv4(),
                    mousex: null,
                    mousey: null,
                    new_bbox: null,
                    search: null,
                    size: [0, 0],
                    tags: [],
                    tags_category: null,
                    tags_id: "w" + uuidv4(),
                    tags_mode: "view",
                    tags_visible: widget.params.tags,
                    width: 0,
                    x1: null,
                    x2: null,
                    y1: null,
                    y2: null,
                });

                component.bboxes_reload = function()
                {
                    server.load_json(component, "/image-collection/" + component.collection() + "/" + component.index() + "/bboxes");
                }

                component.bboxes_auto_reload = ko.computed(function()
                {
                    component.bboxes_reload();
                });

                component.bboxes_clear = function()
                {
                    if(component.bboxes_mode() == "delete")
                    {
                        component.bboxes.removeAll();
                        component.bboxes_save();
                        event.stopPropagation();
                    }
                }

                component.bbox_delete = function(item, event)
                {
                    if(component.bboxes_mode() == "delete")
                    {
                        component.bboxes.remove(item);
                        component.bboxes_save();
                        event.stopPropagation();
                    }
                }

                component.bboxes_mode_add = function()
                {
                    component.bboxes_mode("add");
                }

                component.bboxes_mode_delete = function()
                {
                    component.bboxes_mode("delete");
                }

                component.bboxes_mode_items =
                [
                    {key: "add", label: "<span class='text-success bi-plus-square'/>&nbsp;Add"},
                    {key: "delete", label: "<span class='text-danger bi-x-square'/>&nbsp;Delete"},
                    {key: "view", label: "<span class='text-primary bi-eye'/>&nbsp;View"},
                ];

                component.bboxes_mode_view = function()
                {
                    component.bboxes_mode("view");
                }

                component.bboxes_save = function()
                {
                    var payload = {"bboxes": mapping.toJS(component.bboxes)};
                    server.put_json("/image-collection/" + component.collection() + "/" + component.index() + "/bboxes", payload,
                    {
                        error: function(request)
                        {
                            var body = JSON.parse(request.responseText);
                            notify.local({icon: "bi-exclamation-triangle", type: "bg-danger", message: body.message});
                        },
                        finished: function()
                        {
                            component.bboxes_reload();
                        }
                    });
                }

                component.bboxes_toggle = function()
                {
                    var visible = !component.bboxes_visible();
                    component.bboxes_visible(visible);
                }

                component.first_image = function()
                {
                    component.index(0);
                };

                component.last_image = function()
                {
                    component.index(component.count() - 1);
                }

                component.load_metadata = ko.computed(function()
                {
                    server.get_json("/image-collection/" + component.collection() + "/" + component.index() + "/metadata",
                    {
                        success: function(data)
                        {
                            component.metadata(JSON.stringify(data.metadata, null, 2));
                        },
                    });
                });

                component.next_image = function()
                {
                    component.index((component.index() + 1) % component.count());
                };

                component.on_imageloaded = function(item, e)
                {
                    component.width(e.target.naturalWidth);
                    component.height(e.target.naturalHeight);
                }

                component.on_mousedown = function(item, e)
                {
                    component.update_mouse(e);

                    if(component.bboxes_mode() == "add")
                    {
                        component.x1(component.mousex());
                        component.y1(component.mousey());
                        component.x2(component.mousex());
                        component.y2(component.mousey());

                        component.new_bbox(mapping.fromJS({
                            left: component.x1(),
                            top: component.y1(),
                            width: 0,
                            height: 0,
                            category: component.bboxes_category(),
                            color: "white", //component.color(),
                            username: null, //component.username(),
                        }));
                        component.bboxes.push(component.new_bbox());
                        event.stopPropagation();
                    }
                }

                component.on_mousemove = function(item, e)
                {
                    component.update_mouse(e);

                    if(component.new_bbox() != null)
                    {
                        component.x2(component.mousex());
                        component.y2(component.mousey());

                        component.new_bbox().left(Math.min(component.x1(), component.x2()));
                        component.new_bbox().top(Math.min(component.y1(), component.y2()));
                        component.new_bbox().width(Math.abs(component.x1() - component.x2()));
                        component.new_bbox().height(Math.abs(component.y1() - component.y2()));
                    }
                }

                component.on_mouseup = function(item, e)
                {
                    component.update_mouse(e);

                    if(component.new_bbox() != null)
                    {
                        component.new_bbox(null);
                        component.bboxes_save();
                    }
                }

                component.open_image = function()
                {
                    dashboard.add_widget("samlab-image-widget", {collection: component.collection(), index: component.index()});
                }

                component.previous_image = function()
                {
                    component.index((component.index() + component.count() - 1) % component.count());
                }

                component.random_image = function()
                {
                    var index = lodash.random(0, component.count() - 1);
                    if(index == component.index())
                        index = (index + 1) % component.count();
                    component.index(index);
                };

                component.reload = function()
                {
                    server.get_json("/image-collection/" + component.collection(),
                    {
                        success: function(data)
                        {
                            component.count(data.count);
                            if(component.index() >= data.count)
                                component.index(0);
                        },
                    });
                }

                var search_in_progress = false;

                component.search.subscribe(function(value)
                {
                    if(search_in_progress)
                        return;
                    search_in_progress = true;
                    component.index(Math.max(1, Math.min(parseInt(value), component.count())) - 1);
                    component.search("");
                    search_in_progress = false;
                });

                component.tag_add = function()
                {
                    if(component.tags_mode() == "edit")
                    {
                        component.tags.push(component.tags_category());
                        component.tags_save();
                    }
                }

                component.tag_delete = function(tag)
                {
                    if(component.tags_mode() == "edit")
                    {
                        component.tags.remove(tag);
                        component.tags_save();
                        event.stopPropagation();
                    }
                }

                component.tags_clear = function()
                {
                    if(component.tags_mode() == "edit")
                    {
                        component.tags.removeAll();
                        component.tags_save();
                    }
                }

                component.tags_reload = function()
                {
                    server.get_json("/image-collection/" + component.collection() + "/" + component.index() + "/tags",
                    {
                        success: function(data)
                        {
                            component.tags(data.tags);
                        },
                    });
                }

                component.tags_auto_reload = ko.computed(function()
                {
                    component.tags_reload();
                });

                component.tags_mode_items =
                [
                    {key: "edit", label: "<span class='text-success bi-pencil'/>&nbsp;Edit"},
                    {key: "view", label: "<span class='text-primary bi-eye'/>&nbsp;View"},
                ];

                component.tags_save = function()
                {
                    var payload = {"tags": mapping.toJS(component.tags)};
                    server.put_json("/image-collection/" + component.collection() + "/" + component.index() + "/tags", payload,
                    {
                        error: function(request)
                        {
                            var body = JSON.parse(request.responseText);
                            notify.local({icon: "bi-exclamation-triangle", type: "bg-danger", message: body.message});
                        },
                        finished: function()
                        {
                            component.tags_reload();
                        }
                    });
                }

                component.tags_toggle = function()
                {
                    var visible = !component.tags_visible();
                    component.tags_visible(visible);
                }

                component.update_mouse = function(e)
                {
                    var svg = document.getElementById(component.bboxes_svg_id());
                    var point = svg.createSVGPoint();
                    point.x = e.clientX;
                    point.y = e.clientY;
                    var transformed = point.matrixTransform(svg.getScreenCTM().inverse());

                    component.mousex(transformed.x);
                    component.mousey(transformed.y);
                }

                component.uri = ko.pureComputed(function()
                {
                    return "/image-collection/" + component.collection() + "/" + component.index();
                });

                component.viewbox = ko.computed(function()
                {
                    return "0 0 " + component.width() + " " + component.height();
                });

                dashboard.bind({widget: widget, keys: "left", callback: component.previous_image});
                dashboard.bind({widget: widget, keys: "right", callback: component.next_image});
                component.reload();

                return component;
            }
        },
        template: { require: "text!" + component_name + ".html" }
    });

    var module =
    {
        widget: { width: 4, height: 12, params: {bboxes: false, tags: false, collection: null, index: 0}},
    };

    return module
});
