// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define(
    [
        "debug",
        "knockout",
        "knockout.mapping",
        "lodash",
        "mousetrap",
        "samlab-dom",
        "samlab-favorites",
        "samlab-notify",
        "samlab-permissions",
        "samlab-server",
        "samlab-services",
        "text!samlab-dashboard.html",
        "URI",
        "css!gridstack.css",
        "css!samlab-dashboard.css",
        "knockout-projections",
        "samlab-combo-control",
        "samlab-dropdown",
        "samlab-favorite-control",
        "samlab-gridstack-binding",
    ], function(debug, ko, mapping, lodash, mousetrap, dom, favorites, notify, permissions, server, services, template, URI)
{
    var log = debug("samlab-dashboard");

    ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    // Private API

    document.querySelector("#samlab-dashboard").append(dom.parse(template));

    var bar = document.querySelector(".dashboard-bar");
    var bar_style = getComputedStyle(bar);
    var bar_height = bar.offsetHeight + parseInt(bar_style.marginTop) + parseInt(bar_style.marginBottom);

    var margin = 4;
    var rows = 12;
    var cell_height = (window.innerHeight - bar_height) / rows;

    // Setup private state.
    var state = mapping.fromJS(
    {
        active_widgets: [],
        lid: null,
        operations:
        [
            {
                label: "Lists",
                children:
                [
                    {label: "Favorites", icon: "bi-list-stars", component: "samlab-favorites-widget"},
                    {label: "Services", icon: "bi-card-list", component: "samlab-services-widget"},
                ],
            },
            {
                label: "Miscellaneous",
                children:
                [
                    {label: "About", icon: "bi-file-person", component: "samlab-markup-viewer-widget", params: {uri: "/static/samlab-about.html"}},
                    {label: "Acknowledgements", icon: "bi-file-person", component: "samlab-markup-viewer-widget", params: {uri: "/static/samlab-acknowledgements.html"}},
                ],
            },
            {
                label: "Development",
                children:
                [
                    { label: "Dropdown Test", icon: "bi-wrench", component: "samlab-dropdown-test-widget"},
                    { label: "Keyboard Test", icon: "bi-wrench", component: "samlab-keyboard-test-widget"},
                    { label: "Layout Test", icon: "bi-wrench", component: "samlab-layout-test-widget"},
                    { label: "Notification Test", icon: "bi-wrench", component: "samlab-notify-test-widget"},
                    { label: "Socket Test", icon: "bi-wrench", component: "samlab-socket-test-widget"},
                ],
            },
        ],
        options: {cellHeight: cell_height, margin: margin},
        server: {name: null, description: null},
        tabs: false,
        widgets: [],
    });

    state.favorite_groups = ko.computed(function()
    {
        var grouped = lodash.groupBy(favorites.favorites(), function(favorite)
        {
            return services.label(favorite.service());
        });

        var result = [];
        for(key in grouped)
            result.push({"label": key, "items": grouped[key]});

        result = lodash.sortBy(result, ["label"]);

        return result;
    });

    state.backends = services.backends.map(function(backend)
    {
        return { service: backend.service, name: backend.name};
    });

    state.show_service = function(item)
    {
        module.show_service(item.service(), item.name());
    };

    state.no_favorites = ko.pureComputed(function()
    {
        return state.favorite_groups().length == 0;
    });

    state.show_favorite = function(favorite)
    {
        module.show_service(favorite.service, favorite.name);
    };

    state.lid.subscribe(function(lid)
    {
        log("lid changed", lid);
    });

    state.active_widget = ko.pureComputed(function()
    {
        var active_widgets = state.active_widgets();
        if(active_widgets.length)
            return active_widgets[0];
        return null;
    });

    state.filtered_operations = state.operations.filter(function(group)
    {
        if(group.label() == "Development")
            return permissions.developer();
        return true;
    });

    state.set_active = function(widget)
    {
        var active_widgets = [widget];
        for(let active_widget of state.active_widgets())
        {
            if(active_widget != widget)
            {
                active_widgets.push(active_widget);
            }
        }
        state.active_widgets(active_widgets);
    }

    state.remove_active = function(widget)
    {
        var active_widgets = [];
        for(let active_widget of state.active_widgets())
        {
            if(active_widget != widget)
            {
                active_widgets.push(active_widget);
            }
        }
        state.active_widgets(active_widgets);
    }

    state.keyboard_keys = [];
    state.keyboard_callbacks = []
    state.keyboard_handler = function(event, keys)
    {
        for(let widget of state.active_widgets())
        {
            for(let item of state.keyboard_callbacks)
            {
                if(item.keys != keys)
                    continue;
                if(item.widget != widget)
                    continue;
                item.callback(event, keys);
                return;
            }
        }
    }

    state.mouse_enter = function(widget, event)
    {
        event.currentTarget.classList.add("grid-item-hover");
        state.set_active(widget);
    }

    state.mouse_leave = function(widget, event)
    {
        event.currentTarget.classList.remove("grid-item-hover");
    }

    state.close_widget = function(widget)
    {
        module.remove_widget(widget);
    }

    state.toggle_tabs = function(data, event)
    {
        state.tabs(!state.tabs());
    }

    state.default_layout = function()
    {
        module.default_layout();
    }

    state.empty_layout = function()
    {
        module.set_layout([]);
    }

    state.activate_operation = function(operation)
    {
        if(operation.component)
        {
            module.add_widget(operation.component, operation.params);
        }
    };

    state.widgets_changed = ko.computed(function()
    {
        ko.toJSON(state.widgets);
        return state.widgets;
    });

    state.widgets_changed.extend({rateLimit: {timeout: 250, method: "notifyWhenChangesStop"}});

    state.widgets_changed.subscribe(function(widgets)
    {
        log("widgets_changed", ko.toJS(widgets));

        server.post_json("/layouts", {layout: mapping.toJS(widgets)},
        {
            success: function(response)
            {
                var new_location = URI(window.location).query({"lid": response.lid});
                window.history.replaceState(null, null, new_location.toString());
                state.lid(response.lid);
            },
        });
    });

    server.load_json(state, "/server");

    ko.applyBindings(state, document.querySelector("#samlab-dashboard"));

    ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    // Public API

    var module = mapping.fromJS({
        active_widget: null,
    });

    state.active_widget.subscribe(function(active_widget)
    {
        module.active_widget(active_widget);
    });

    module.add_widget = function(component, params, x, y, width, height)
    {
        // We never propagate observables to new widgets.
        component = ko.unwrap(component);
        params = ko.toJS(params) || {};
        x = ko.unwrap(x);
        y = ko.unwrap(y);
        width = ko.unwrap(width);
        height = ko.unwrap(height);

        if(state.tabs())
        {
            state.tabs(false);
            var layout = [{component: component, params: params, x: x, y: y, width: width, height: height}];
            var uri = URI(window.location).search({layout: JSON.stringify(layout)});
            window.open(uri.toString(), "_blank");
        }
        else
        {
            require([component], function(module)
            {
                module = module || {};
                module.widget = module.widget || {};

                // Setup widget defaults.
                var widget = mapping.fromJS(
                {
                    component: component,
                    params: {},
                    x: null,
                    y: null,
                    width: 3,
                    height: 6,
                });

                // Allow widget modules to override the defaults.
                mapping.fromJS(module.widget, widget);

                // Allow serialized parameters to override the defaults.
                mapping.fromJS({params: params}, widget);

                // Allow serialized position / size to override the defaults.
                if(x != null)
                    widget.x(x);
                if(y != null)
                    widget.y(y);
                if(width != null)
                    widget.width(width);
                if(height != null)
                    widget.height(height);

                state.widgets.push(widget);
                state.set_active(widget);
            });
        }
    }

    module.default_layout = function()
    {
        server.get_json("/layouts",
        {
            success: function(result)
            {
                module.set_layout(result.layout);
            }
        });
    }

    module.set_layout = function(layout)
    {
        log("set_layout", layout);
        while(state.widgets().length)
        {
            module.remove_widget(state.widgets.pop());
        }

        for(let widget of layout)
        {
            module.add_widget(widget.component, widget.params, widget.x, widget.y, widget.width, widget.height);
        }
    }

    module.remove_widget = function(widget)
    {
        log("remove_widget", widget);
        module.unbind({widget: widget});
        state.remove_active(widget);
        state.widgets.remove(widget);
    }

    module.bind = function(params)
    {
        state.keyboard_callbacks.push({widget: params.widget, keys: params.keys, callback: params.callback});
        if(state.keyboard_keys.indexOf(params.keys) < 0)
        {
            state.keyboard_keys.push(params.keys);
            mousetrap.bind(params.keys, state.keyboard_handler);
        }
    }

    module.unbind = function(params)
    {
        state.keyboard_callbacks = state.keyboard_callbacks.filter(function(item)
        {
            if(params.widget)
            {
                if(item.widget != params.widget)
                    return true;
            }
            return false;
        });
    }

    module.set_layout_id = function(lid)
    {
        log("set_layout_id", lid);
        server.get_json("/layouts/" + lid,
        {
            success: function(result)
            {
                module.set_layout(result.layout);
            },
            error: function()
            {
                notify.local({icon: "bi-exclamation-triangle", type: "bg-danger", message: "Couldn't load the dashboard layout."});
            }
        });
    }

    module.show_service = function(service, name)
    {
        var service = ko.unwrap(service);
        var name = ko.unwrap(name);

        log("show_service", service, name);

        if(service == "favorites")
        {
            module.add_widget("samlab-favorites-widget");
        }
        else if(service == "layouts" && name)
        {
            module.set_layout_id(name);
        }
        else if(service == "document-collection")
        {
            module.add_widget("samlab-documents-widget", {collection: name, index: 0});
        }
        else if(service == "image-collection")
        {
            module.add_widget("samlab-images-widget", {collection: name, index: 0});
        }
        else if(service == "timeseries-collection")
        {
            module.add_widget("samlab-timeseries-widget", {collection: name, index: 0});
        }
        else
        {
            module.add_widget("samlab-generic-content-widget", {service: service, name: name});
        }
    }

/*
    module.auto_delete = function(widget, otype, oid)
    {
        var otype = ko.unwrap(otype);
        var oid = ko.unwrap(oid);
        return object.deleted.subscribe(function(object)
        {
            if(otype == object.otype && oid == object.oid)
            {
                log("auto_delete", widget);
                module.remove_widget(widget);
            }
        });
    }
*/

    // Setup the initial dashboard state
    var uri = URI(window.location);
    if(uri.hasSearch("lid"))
    {
        module.set_layout_id(uri.search(true).lid);
    }
    else if(uri.hasSearch("layout"))
    {
        module.set_layout(JSON.parse(uri.search(true).layout));
    }
    else if(!uri.hasSearch("empty"))
    {
        module.default_layout();
    }

    return module;
});
