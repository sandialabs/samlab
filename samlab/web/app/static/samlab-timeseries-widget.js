// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([
    "debug",
    "knockout",
    "knockout.mapping",
    "samlab-dashboard",
    "samlab-dialog",
    "samlab-timeseries",
    ], function(debug, ko, mapping, dashboard, dialog, timeseries)
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

                component.experiments = timeseries.experiments;
                component.keys = timeseries.keys;

                component.open_experiment = function(item)
                {
                    item.keys().forEach(function(key)
                    {
                        dashboard.add_widget("samlab-timeseries-plot-widget", {experiment: item.experiment, key: key});
                    });
                }

                component.open_key = function(item)
                {
                    item.experiments().forEach(function(experiment)
                    {
                        dashboard.add_widget("samlab-timeseries-plot-widget", {experiment: experiment, key: item.key()});
                    });
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
                                timeseries.delete_samples({experiment: experiment});
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
                                timeseries.delete_samples({experiment: experiment, trial: trial});
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
                                timeseries.delete_samples({key: key});
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
