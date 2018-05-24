// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([
    "knockout",
    "knockout.mapping",
    "samlab-dialog",
    "samlab-favorite",
    ], function(ko, mapping, dialog, favorite)
{
    var component_name = "samlab-favorite-control";
    ko.components.register(component_name,
    {
        viewModel:
        {
            createViewModel: function(params, component_info)
            {
                var component = mapping.fromJS({
                    otype: params.otype,
                    oid: params.oid,
                    state: favorite.get(params.otype, params.oid),
                });

                component.update_state = ko.computed(function()
                {
                    var otype = component.otype();
                    var oid = component.oid();
                    component.state(favorite.get(component.otype, component.oid));
                });

                component.icon = ko.pureComputed(function()
                {
                    return component.state() ? "fa-heart" : "fa-heart-o";
                });

                component.toggle_favorite = function()
                {
                    if(component.state())
                    {
                        favorite.delete(component.otype, component.oid);
                    }
                    else
                    {
                        dialog.dialog(
                        {
                            buttons: [{label: "Favorite", class_name: "btn-success"}, {label: "Cancel", class_name: "btn-secondary"}],
                            callback: function(button, name)
                            {
                                if(button.label == "Favorite")
                                {
                                    favorite.create(component.otype, component.oid, name || component.oid);
                                }
                            },
                            message: "A link to this object will be saved to the Favorites dropdown menu.",
                            input: true,
                            placeholder: "Give this favorite a memorable name.",
                            title: "Mark favorite?",
                        });
                    }
                }

                return component;
            }
        },
        template: { require: "text!" + component_name + ".html" }
    });
});
