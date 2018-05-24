// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([
    "knockout",
    "knockout.mapping",
    "samlab-dashboard",
    "samlab-trial",
    ], function(ko, mapping, dashboard, trial)
{
    var component_name = "samlab-trials-widget";
    ko.components.register(component_name,
    {
        viewModel:
        {
            createViewModel: function(widget, component_info)
            {
                var component = mapping.fromJS({
                });

                component.trials = trial.trials.map(function(trial)
                {
                    return { label: trial.name, id: trial.id};
                });

                component.open_trial = function(item)
                {
                    dashboard.add_widget("samlab-trial-widget", {id: item.id});
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
