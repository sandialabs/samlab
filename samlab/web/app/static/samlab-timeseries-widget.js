// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([
    "debug",
    "knockout",
    "knockout.mapping",
    "lodash",
    "samlab-dashboard",
    "samlab-dialog",
    "samlab-timeseries-manager",
    ], function(debug, ko, mapping, lodash, dashboard, dialog, timeseries_manager)
{
    var component_name = "samlab-timeseries-widget";

    var log = debug(component_name);

    ko.components.register(component_name,
    {
        viewModel:
        {
            createViewModel: function(widget, component_info)
            {
                var component = mapping.fromJS(
                {
                });

                component.experiments = timeseries_manager.experiments;
                component.keys = timeseries_manager.keys;
                component.exclude = widget.params.exclude;

                // We override the global list of exclusions
                timeseries_manager.exclude(component.exclude);

                component.visible_trials = ko.computed(
                {
                    // Translate the list of excluded trials into a list of visible trials.
                    read: function()
                    {
                        var exclude = mapping.toJS(component.exclude);

                        var visible_trials = [];
                        ko.utils.arrayForEach(component.experiments(), function(experiment)
                        {
                            ko.utils.arrayForEach(experiment.trials(), function(trial)
                            {
                                var predicate = {experiment: experiment.experiment(), trial: trial.trial()};
                                var index = lodash.findIndex(exclude, predicate);
                                if(index == -1)
                                {
                                    visible_trials.push(trial);
                                }
                            });
                        });
                        return visible_trials;
                    },
                    // Translate a list of visible trials into the list of excluded trials.
                    write: function(visible)
                    {
                        var exclude = [];
                        ko.utils.arrayForEach(component.experiments(), function(experiment)
                        {
                            ko.utils.arrayForEach(experiment.trials(), function(trial)
                            {
                                if(visible.indexOf(trial) == -1)
                                {
                                    exclude.push({experiment: experiment.experiment(), trial: trial.trial()});
                                }
                            });
                        });
                        component.exclude(exclude);
                    },
                });

                component.exclude.subscribe(function()
                {
                    timeseries_manager.exclude(component.exclude);
                });

                component.icon = function(content_type)
                {
                    if(content_type == "application/x-scalar")
                        return "fa fa-fw fa-line-chart";
                    if(content_type == "text/plain")
                        return "fa fa-fw fa-file-text-o";
                    return "";
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
        widget: {params: {exclude: []}},
    };

    return module;
});
