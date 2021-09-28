// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([], function()
{
    var module = {};

    module.dialog = function(params)
    {
        require(["knockout", "knockout.mapping", "samlab-modal"], function(ko, mapping, modal)
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
                dialog.hide();
            };

            modal.create("samlab-dialog.html", state,
            {
                show: function(m)
                {
                    dialog = m;
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

