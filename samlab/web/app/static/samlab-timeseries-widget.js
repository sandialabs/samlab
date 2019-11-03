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
                    experiments: timeseries_manager.experiments,
                    keys: timeseries_manager.keys,
                });

                component.icon = function(content_type)
                {
                    if(content_type == "application/x-scalar")
                        return "fa fa-fw fa-line-chart";
                    if(content_type == "text/plain")
                        return "fa fa-fw fa-file-text-o";
                    return "";
                }

                component.trial_checked = function(experiment_item, trial_item)
                {
                    log("trial_checked", experiment_item, trial_item);
                }

                component.open_key = function(item, content_type)
                {
                    var key = item.key();

                    if(content_type == "application/x-scalar")
                        dashboard.add_widget("samlab-timeseries-plot-widget", {key: key});
                    if(content_type == "text/plain")
                        dashboard.add_widget("samlab-timeseries-text-widget", {key: key});
                };

                component.delete_experiment = function(experiment_item)
                {
                    dialog.dialog(
                    {
                        alert: "This operation is immediate and cannot be undone.",
                        buttons: [{label: "Delete", class_name: "btn-danger"}, {label: "Cancel", class_name: "btn-secondary"}],
                        callback: function(button)
                        {
                            if(button.label == "Delete")
                                timeseries_manager.delete_samples({experiment: experiment_item.experiment});
                        },
                        message: "This will delete all its data including all trials and keys.",
                        title: "Delete " + experiment_item.experiment() + "?",
                    });
                }

                component.delete_trial = function(experiment_item, trial_item)
                {
                    dialog.dialog(
                    {
                        alert: "This operation is immediate and cannot be undone.",
                        buttons: [{label: "Delete", class_name: "btn-danger"}, {label: "Cancel", class_name: "btn-secondary"}],
                        callback: function(button)
                        {
                            if(button.label == "Delete")
                                timeseries_manager.delete_samples({experiment: experiment_item.experiment, trial: trial_item.trial});
                        },
                        message: "This will delete all its data including all keys.",
                        title: "Delete trial <span style='color:" + trial_item.color() + "'>" + trial_item.trial() + "</span>?",
                    });
                }

                component.delete_key = function(item)
                {
                    var key = item.key();

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
