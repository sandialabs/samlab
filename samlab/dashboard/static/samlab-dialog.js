// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([], function()
{
    var module = {};

    module.dialog = function(params)
    {
        require(["samlab-modal", "knockout", "knockout.mapping", "jquery"], function(modal, ko, mapping, jquery)
        {
            params = params || {};

            var state = mapping.fromJS(
            {
                alert: params.alert || "",
                input: params.input || false,
                message: params.message || "",
                placeholder: params.placeholder || "",
                title: params.title || "Alert",
                value: params.value || "",
            });

            var dialog = null;

            state.buttons = params.buttons || [{class_name: "btn-default", label:"OK"}],

            state.close = function(button)
            {
                state.result = button;
                jquery(dialog).modal("hide");
            };

            modal.create("samlab-dialog.html", state,
            {
                show: function(modal)
                {
                    dialog = modal;
                },
                hidden: function()
                {
                    if(params.callback)
                        params.callback(state.result, state.value);
                },
            });
        });
    }

    return module;
});

