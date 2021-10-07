// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([], function()
{
    var module = {};

    module.create = function(template, state, params)
    {
        require([
            "bootstrap",
            "knockout",
            "samlab-dom",
            "text!" + template,
            ], function(bootstrap, ko, dom, template)
        {
            params = params || {};

            var content = dom.parse(template);
            document.body.append(content);
            ko.applyBindings(state, content);

            var modal = new bootstrap.Modal(content);

            content.addEventListener("show.bs.modal", function()
            {
                if(params.show)
                    params.show(modal);
            });

            content.addEventListener("shown.bs.modal", function()
            {
                if(params.shown)
                    params.shown(modal);
            });

            content.addEventListener("hide.bs.modal", function()
            {
                if(params.hide)
                    params.hide(modal);
            });

            content.addEventListener("hidden.bs.modal", function()
            {
                content.remove();
                if(params.hidden)
                    params.hidden(modal);
            });

            modal.show();
        });
    }

    return module;
});

