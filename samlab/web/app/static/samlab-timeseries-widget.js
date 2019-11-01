// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([
    "debug",
    "knockout",
    "knockout.mapping",
    "samlab-dashboard",
    "samlab-dialog",
    "samlab-timeseries-manager",
    ], function(debug, ko, mapping, dashboard, dialog, timeseries_manager)
{
    var component_name = "samlab-timeseries-widget";

    var log = debug(component_name);

    ko.components.register(component_name,
    {
        viewModel:
        {
            createViewModel: function(widget, component_info)
            {
                var component = mapping.fromJS({
                });

                component.experiments = timeseries_manager.experiments;
                component.keys = timeseries_manager.keys;
                component.timeseries = timeseries_manager.timeseries;

                component.icon = function(timeseries)
                {
                    var content_type = timeseries["content-type"]();
                    if(content_type == "application/x-scalar")
                        return "fa fa-fw fa-line-chart";
                    if(content_type == "text/plain")
                        return "fa fa-fw fa-file-text-o";
                    return "";
                }

                component.show = function(item)
                {
                    timeseries_manager.show(item);
                };

                component.hide = function(item)
                {
                    timeseries_manager.hide(item);
                }

                component.open_timeseries = function(timeseries)
                {
                    var key = timeseries.key();
                    var content_type = timeseries["content-type"]();

                    if(content_type == "application/x-scalar")
                        dashboard.add_widget("samlab-timeseries-plot-widget", {key: key});
                    if(content_type == "text/plain")
                        dashboard.add_widget("samlab-timeseries-text-widget", {key: key});
                    return "";
                }

                component.open_key = function(key)
                {
                    dashboard.add_widget("samlab-timeseries-plot-widget", {key: key});
                };

                component.delete_experiment = function(experiment)
                {
                    log(experiment);

                    dialog.dialog(
                    {
                        alert: "This operation is immediate and cannot be undone.",
                        buttons: [{label: "Delete", class_name: "btn-danger"}, {label: "Cancel", class_name: "btn-secondary"}],
                        callback: function(button)
                        {
                            if(button.label == "Delete")
                                timeseries_manager.delete_samples({experiment: experiment});
                        },
                        message: "This will delete its data across all trials and keys.",
                        title: "Delete " + experiment + "?",
                    });
                }

                component.delete_trial = function(experiment, trial)
                {
                    log(experiment, trial);

                    dialog.dialog(
                    {
                        alert: "This operation is immediate and cannot be undone.",
                        buttons: [{label: "Delete", class_name: "btn-danger"}, {label: "Cancel", class_name: "btn-secondary"}],
                        callback: function(button)
                        {
                            if(button.label == "Delete")
                                timeseries_manager.delete_samples({experiment: experiment, trial: trial});
                        },
                        message: "This will delete its data across all experiments and keys.",
                        title: "Delete " + experiment + " " + trial + "?",
                    });
                }

                component.delete_key = function(key)
                {
                    log(key);

                    dialog.dialog(
                    {
                        alert: "This operation is immediate and cannot be undone.",
                        buttons: [{label: "Delete", class_name: "btn-danger"}, {label: "Cancel", class_name: "btn-secondary"}],
                        callback: function(button)
                        {
                            if(button.label == "Delete")
                                timeseries_manager.delete_samples({key: key});
                        },
                        message: "This will delete its data across all experiments and trials.",
                        title: "Delete " + key + "?",
                    });
                };

                return component;
            }
        },
        template: { require: "text!" + component_name + ".html" }
    });

    var module =
    {
        widget: { },
    };

    return module;
});
