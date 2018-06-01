// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([
    "knockout",
    "knockout.mapping",
    "samlab-dashboard",
    "samlab-object",
    "samlab-server",
    "samlab-socket",
    ], function(ko, mapping, dashboard, object, server, socket)
{
    var component_name = "samlab-cnn-layer-widget";

    ko.components.register(component_name,
    {
        viewModel:
        {
            createViewModel: function(widget, component_info)
            {
                var component = mapping.fromJS({
                    model:
                    {
                        id: widget.params.id,
                        name: null,
                    },
                    summary: { layers: []},
                });

                var auto_delete_subscription = dashboard.auto_delete(widget, "models", widget.params.id);

                component.dispose = function()
                {
                    auto_delete_subscription.dispose();
                    socket.off("keras-model-summary", keras_model_summary_ready);
                    socket.off("keras-model-layer-filter-gradient-ascent", keras_model_layer_filter_gradient_ascent_ready);
                }

                component.loading = ko.pureComputed(function()
                {
                    return component.summary.layers().length == 0;
                });

                component.layers = component.summary.layers.filter(function(layer)
                {
                    return ["Conv2D"].indexOf(layer.class_name()) != -1;
                });

                component.layers = component.layers.map(function(layer)
                {
                    var filters = [];
                    for(var i = 0; i != 10; ++i)
                        filters.push({index: i, visible: ko.observable(false), loading: ko.observable(false), src: ko.observable(null)});

                    return Object.assign({filters: filters}, layer);
                });

                function load_next_image()
                {
                    for(let layer of component.layers())
                    {
                        for(let filter of layer.filters)
                        {
                            if(!filter.visible())
                            {
                                filter.visible(true);
                                filter.loading(true);
                                socket.emit("keras-model-layer-filter-gradient-ascent", {otype: "models", oid: component.model.id(), key: "model", layer: layer.name(), filter: filter.index})
                                return;
                            }
                        }
                    }
                }

                component.layers.subscribe(function()
                {
                    load_next_image();
                });

                component.uri = ko.pureComputed(function()
                {
                    return "/models/" + component.model.id() + "/content/model/keras-model/layers/";
                });

                function keras_model_summary_ready(message)
                {
                    if(message.otype == "models" && message.oid == component.model.id() && message.key == "model")
                    {
                        mapping.fromJS({summary: message.summary}, component);
                    }
                }

                function keras_model_layer_filter_gradient_ascent_ready(message)
                {
                    if(message.otype == "models" && message.oid == component.model.id() && message.key == "model")
                    {
                        for(let layer of component.layers())
                        {
                            if(message.layer != layer.name())
                                continue;

                            for(let filter of layer.filters)
                            {
                                if(message.filter != filter.index)
                                    continue;

                                filter.visible(true);
                                filter.loading(false);
                                filter.src(message.image);
                                load_next_image();
                                return;
                            }
                        }
                    }
                }

                server.load_json(component, "/models/" + component.model.id());

                socket.on("keras-model-summary", keras_model_summary_ready);
                socket.on("keras-model-layer-filter-gradient-ascent", keras_model_layer_filter_gradient_ascent_ready);

                socket.emit("keras-model-summary", {otype: "models", oid: component.model.id(), key: "model"});

                return component;
            },
        },
        template: { require: "text!" + component_name + ".html" }
    });

    var module =
    {
        widget: { params: {}},
    };

    return module;
});
