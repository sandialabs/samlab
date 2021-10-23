// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([
    "bootstrap",
    "debug",
    "knockout",
    "knockout.mapping",
    "lodash",
    "samlab-dashboard",
    "samlab-notify",
    "samlab-permissions",
    "samlab-server",
    "samlab-socket",
    "samlab-uuidv4",
    ], function(bootstrap, debug, ko, mapping, lodash, dashboard, notify, permissions, server, socket, uuidv4)
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
                    cursorx: null,
                    cursory: null,
                    help_id: "w" + uuidv4(),
                    help_visible: false,
                    imageheight: 0,
                    imagewidth: 0,
                    imagex: 0,
                    imagey: 0,
                    imagezoom: 1,
                    index: widget.params.index,
                    lastx: null,
                    lasty: null,
                    metadata: null,
                    metadata_visible: widget.params.metadata,
                    metaid: "w" + uuidv4(),
                    new_bbox: null,
                    pan: false,
                    search: null,
                    size: [0, 0],
                    tags: [],
                    tags_category: null,
                    tags_id: "w" + uuidv4(),
                    tags_mode: "view",
                    tags_visible: widget.params.tags,
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
                    {icon: "bi-plus-square", key: "add", label: "Add", shortcut: "a", extraclass: "text-success"},
                    {icon: "bi-x-square", key: "delete", label: "Delete", shortcut: "d", extraclass: "text-danger"},
                    {icon: "bi-eye", key: "view", label: "View", shortcut: "v", extraclass: "text-primary"},
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
                    component.bboxes_visible(!component.bboxes_visible());
                }

                component.displaywidth = ko.computed(function()
                {
                    return component.imagezoom() * 100 + "%";
                });

                component.first_image = function()
                {
                    component.index(0);
                };

                component.help_toggle = function()
                {
                    component.help_visible(!component.help_visible());
                }

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

                component.metadata_toggle = function()
                {
                    component.metadata_visible(!component.metadata_visible());
                }

                component.next_image = function()
                {
                    component.index((component.index() + 1) % component.count());
                };

                component.on_imageloaded = function(item, event)
                {
                    component.imagewidth(event.target.naturalWidth);
                    component.imageheight(event.target.naturalHeight);
                }

                component.on_mousedown = function(data, event)
                {
                    component.update_cursor(event);

                    if(event.button == 0 && component.bboxes_mode() == "add")
                    {
                        component.x1(component.cursorx());
                        component.y1(component.cursory());
                        component.x2(component.cursorx());
                        component.y2(component.cursory());
/*
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
*/
                    }
                    else if(event.button == 1)
                    {
                        component.pan(true);
                    }

                    event.stopPropagation();
                    component.update_mouse(event);
                }

                component.on_mousemove = function(event)
                {
                    component.update_cursor(event);

                    if((event.buttons & 1) && component.bboxes_mode() == "add" && component.new_bbox() == null)
                    {
                        component.x2(component.cursorx());
                        component.y2(component.cursory());

                        if(Math.abs(component.x2() - component.x1()) > 10 && Math.abs(component.y2() - component.y1()) > 10)
                        {
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
                        }
                    }
                    else if(component.new_bbox() != null)
                    {
                        component.x2(component.cursorx());
                        component.y2(component.cursory());

                        var left = Math.max(0, Math.min(component.x1(), component.x2()));
                        var top = Math.max(0, Math.min(component.y1(), component.y2()));
                        var right = Math.min(component.imagewidth(), Math.max(component.x1(), component.x2()));
                        var bottom = Math.min(component.imageheight(), Math.max(component.y1(), component.y2()));

                        component.new_bbox().left(left);
                        component.new_bbox().top(top);
                        component.new_bbox().width(right - left);
                        component.new_bbox().height(bottom - top);
                    }
                    else if(component.pan())
                    {
                        component.imagex(component.imagex() + event.clientX - component.lastx());
                        component.imagey(component.imagey() + event.clientY - component.lasty());
                    }

                    component.update_mouse(event);
                }

                component.on_mouseup = function(event)
                {
                    component.update_cursor(event);

                    if(component.new_bbox() != null)
                    {
                        component.bboxes_save();
                    }

                    component.new_bbox(null);
                    component.pan(false);

                    component.update_mouse(event);
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
                    {icon: "bi-pencil", key: "edit", label: "Edit", shortcut: "e", extraclass: "text-success"},
                    {icon: "bi-eye", key: "view", label: "View", shortcut: "v", extraclass: "text-primary"},
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
                    component.tags_visible(!component.tags_visible());
                }

                component.update_cursor = function(e)
                {
                    var svg = document.getElementById(component.bboxes_svg_id());
                    var point = svg.createSVGPoint();
                    point.x = e.clientX;
                    point.y = e.clientY;
                    var transformed = point.matrixTransform(svg.getScreenCTM().inverse());

                    component.cursorx(transformed.x);
                    component.cursory(transformed.y);
                }

                component.update_mouse = function(e)
                {
                    component.lastx(e.clientX);
                    component.lasty(e.clientY);
                }

                component.uri = ko.pureComputed(function()
                {
                    return "/image-collection/" + component.collection() + "/" + component.index();
                });

                component.viewbox = ko.computed(function()
                {
                    return "0 0 " + component.imagewidth() + " " + component.imageheight();
                });

                component.zoom_in = function()
                {
                    component.imagezoom(component.imagezoom() * 1.25);
                }

                component.zoom_out = function()
                {
                    component.imagezoom(component.imagezoom() * (1/1.25));
                }

                component.zoom_reset = function()
                {
                    component.imagex(0);
                    component.imagey(0);
                    component.imagezoom(1.0);
                }

                // This must go last, or some callbacks may be undefined.
                component.menu_items =
                [
                    {icon: "bi-card-image", label: "Standalone image", click: component.open_image},
                    {icon: "bi-bounding-box", label: "Bounding boxes", click: component.bboxes_toggle, shortcut: "b"},
                    {icon: "bi-list-nested", label: "Metadata", click: component.metadata_toggle, shortcut: "m"},
                    {icon: "bi-tags", label: "Tags", click: component.tags_toggle, shortcut: "t"},
                    {divider: true},
                    {icon: "bi-zoom-in", label: "Zoom in", click: component.zoom_in, shortcut: "+"},
                    {icon: "bi-zoom-out", label: "Zoom out", click: component.zoom_out, shortcut: "-"},
                    {icon: "bi-aspect-ratio", label: "Reset pan & zoom", click: component.zoom_reset, shortcut: "0"},
                ];

                dashboard.bind({widget: widget, keys: "0", callback: component.zoom_reset});
                dashboard.bind({widget: widget, keys: "a", callback: function() {component.bboxes_mode("add");}});
                dashboard.bind({widget: widget, keys: "b", callback: component.bboxes_toggle});
                dashboard.bind({widget: widget, keys: "d", callback: function() {component.bboxes_mode("delete");}});
                dashboard.bind({widget: widget, keys: "e", callback: function() {component.tags_mode("edit");}});
                dashboard.bind({widget: widget, keys: "+", callback: component.zoom_in});
                dashboard.bind({widget: widget, keys: "-", callback: component.zoom_out});
                dashboard.bind({widget: widget, keys: "left", callback: component.previous_image});
                dashboard.bind({widget: widget, keys: "m", callback: component.metadata_toggle});
                dashboard.bind({widget: widget, keys: "right", callback: component.next_image});
                dashboard.bind({widget: widget, keys: "t", callback: component.tags_toggle});
                dashboard.bind({widget: widget, keys: "v", callback: function() {component.bboxes_mode("view"); component.tags_mode("view"); }});
                component.reload();

                document.querySelector("body").addEventListener("mousemove", component.on_mousemove);
                document.querySelector("body").addEventListener("mouseup", component.on_mouseup);

                return component;
            }
        },
        template: { require: "text!" + component_name + ".html" }
    });

    var module =
    {
        widget: { width: 4, height: 12, params: {bboxes: false, collection: null, index: 0, metadata: false, tags: false}},
    };

    return module
});
