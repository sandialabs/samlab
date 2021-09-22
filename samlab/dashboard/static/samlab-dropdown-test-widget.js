// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define(["knockout", "knockout.mapping"], function(ko, mapping)
{
    var component_name = "samlab-dropdown-test-widget";
    ko.components.register(component_name,
    {
        viewModel:
        {
            createViewModel: function(widget, component_info)
            {
                var component = mapping.fromJS({
                });

                component.options = [
                    {type: "group", label: "Stuff"},
                    {type: "item", label: "Action"},
                    {type: "item", label: "Another action"},
                    {type: "item", label: "Something else"},
                    {type: "divider"},
                    {type: "item", label: "Action"},
                    {type: "item", label: "Another action"},
                    {type: "item", label: "Something else"},
                    {type: "group", label: "More stuff"},
                    {type: "item", label: "Action"},
                    {type: "item", label: "Another action"},
                    {type: "item", label: "Something else"},
                ];

                component.select_option = function(option)
                {
                    console.log("widget select option", option);
                }

                component.modal_test = function()
                {
                    require(["samlab-modal"], function(modal)
                    {
                        var state = mapping.fromJS({
                        });

                        state.options = [
                            {type: "group", label: "Stuff"},
                            {type: "item", label: "Action"},
                            {type: "item", label: "Another action"},
                            {type: "item", label: "Something else"},
                            {type: "divider"},
                            {type: "item", label: "Action"},
                            {type: "item", label: "Another action"},
                            {type: "item", label: "Something else"},
                            {type: "group", label: "More stuff"},
                            {type: "item", label: "Action"},
                            {type: "item", label: "Another action"},
                            {type: "item", label: "Something else"},
                        ];

                        state.select_option = function(option)
                        {
                            console.log("modal select option", option);
                        }

                        modal.create("samlab-dropdown-test-widget-dialog.html", state);
                    });
                }

                return component;
            },
        },

        template: { require: "text!" + component_name + ".html" },
    });

    var module =
    {
        widget: { },
    };

    return module;
});
