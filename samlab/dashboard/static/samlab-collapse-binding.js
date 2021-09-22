// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define(["knockout", "jquery"], function(ko, jquery)
{
    ko.bindingHandlers["collapse"] =
    {
        "init": function(element)
        {
            jquery(element).collapse({toggle: false});
            ko.utils.domNodeDisposal.addDisposeCallback(element, function()
            {
                jquery(element).collapse("dispose");
            });
        },

        "update": function(element, valueAccessor)
        {
            var collapse = ko.unwrap(valueAccessor());

            if(collapse)
                jquery(element).collapse("hide");
            else
                jquery(element).collapse("show");
        },
    };
});

