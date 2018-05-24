// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([], function()
{
    var module = {};

    module.create = function(template, state, params)
    {
        require(["samlab-dom", "knockout", "jquery", "text!" + template], function(dom, ko, jquery, template)
        {
            params = params || {};

            var modal = dom.parse(template);
            document.body.append(modal);

            jquery(modal).on("show.bs.modal", function()
            {
                if(params.show)
                    params.show(modal);
            });

            jquery(modal).on("shown.bs.modal", function()
            {
                if(params.shown)
                    params.shown(modal);
            });

            jquery(modal).on("hide.bs.modal", function()
            {
                if(params.hide)
                    params.hide(modal);
            });

            jquery(modal).on("hidden.bs.modal", function()
            {
                jquery(modal).remove();
                if(params.hidden)
                    params.hidden(modal);
            });

            ko.applyBindings(state, modal);

            if(params.draggable)
                jquery(modal).draggable(
                {
                    handle: ".modal-header",
                });

            jquery(modal).modal("show");
        });
    }

    return module;
});

