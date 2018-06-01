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
    var component_name = "samlab-cluster-widget";
    ko.components.register(component_name,
    {
        viewModel:
        {
            createViewModel: function(widget, component_info)
            {
                var component = mapping.fromJS({
                    clusters: [],
                    key: null,
                    keys: [],
                    loading: false,
                    object_label: object.label(widget.params.otype, {singular: true, capitalize: true}),
                    otype: widget.params.otype,
                    title: "Cluster " + object.label(widget.params.otype, {singular: false, capitalize: true}),
                });

                component.key_items = component.keys.map(function(key)
                {
                    return {key: key, label: key};
                });

                component.preprocessor = widget.params.preprocessor;
                component.preprocessor_items =
                [
                    { key: "minmax", label: "Scale to [0, 1]" },
                    { key: "scale", label: "Zero mean, unit variance" },
                ];

                component.eps = widget.params.eps;

                component.metric = widget.params.metric;
                component.metric_items =
                [
                    { key: "cosine", label: "Cosine distance" },
                    { key: "euclidean", label: "Euclidean distance" },
                ];

                component.min_samples = widget.params["min-samples"];

                component.sort = widget.params.sort;
                component.sort_items =
                [
                    { key: "label", label: "Cluster labels" },
                    { key: "distance", label: "Centroid distances" },
                ];

                component.compute_clustering = ko.computed(function()
                {
                    var otype = component.otype();

                    var content = component.key();
                    if(content == null)
                        return;

                    var preprocessor = {
                        name: component.preprocessor(),
                        };

                    var algorithm = {
                        name: "dbscan",
                        params: {
                            eps: Number(component.eps()),
                            metric: component.metric(),
                            "min-samples": Number(component.min_samples()),
                            },
                        };

                    component.loading(true);
                    socket.emit("cluster-content", {
                        algorithm: algorithm,
                        content: content,
                        otype: otype,
                        preprocessor: preprocessor,
                        });
                });

                component.sort_results = ko.computed(function()
                {
                    var clusters = component.clusters();
                    var sort = component.sort();
                    if(sort == "label")
                    {
                        component.clusters.sort(function(lhs, rhs)
                        {
                            if(lhs.label() == rhs.label())
                            {
                                if(lhs.distance() == rhs.distance())
                                    return 0;
                                return lhs.distance() < rhs.distance() ? -1 : 1;
                            }
                            return lhs.label() < rhs.label() ? -1 : 1;
                        });
                    }
                    else if(sort == "distance")
                    {
                        component.clusters.sort(function(lhs, rhs)
                        {
                            if(lhs.distance() == rhs.distance())
                                return 0;
                            return lhs.distance() < rhs.distance() ? -1 : 1;
                        });
                    }
                });

                component.select_object = function(data)
                {
                    console.log("select_object", arguments);
                    if(component.otype() == "observations")
                    {
                        dashboard.add_widget("samlab-observation-widget", {"id": data.oid()});
                    }
                }

                component.cluster_content = function(result)
                {
                    if(result.otype == component.otype() && result.content == component.key())
                    {
                        component.loading(false);
                        mapping.fromJS({clusters: result.clusters}, component);
                    }
                }

                component.dispose = function()
                {
                    socket.off("cluster-content", component.cluster_content);
                }
                socket.on("cluster-content", component.cluster_content);

                server.load_json(component, "/" + component.otype() + "/content/keys", "GET", { success: function()
                {
                    if(component.keys().length)
                        component.key(component.keys()[0]);
                }});

                return component;
            }
        },
        template: { require: "text!" + component_name + ".html" }
    });

    var module =
    {
        widget: { params: {preprocessor: "minmax", sort: "label", "min-samples": 5, eps: 0.1, metric: "cosine"}},
    };

    return module;
});
