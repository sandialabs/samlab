// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define(["knockout", "jquery"], function(ko, jquery)
{
    ko.bindingHandlers["tooltip"] =
    {
        "init": function(element, valueAccessor)
        {
            ko.utils.domNodeDisposal.addDisposeCallback(element, function()
            {
                jquery(element).tooltip("dispose");
            });
        },

        "update": function(element, valueAccessor)
        {
            var options =
            {
                boundary: "window",
                container: "body",
                delay: {show: 1000, hide: 10},
                placement: "top",
                trigger: "hover",
            };
            ko.utils.extend(options, ko.bindingHandlers.tooltip.options);

            var user = ko.utils.unwrapObservable(valueAccessor());
            ko.utils.extend(options, user);

            jquery(element).tooltip(options);
        },
    };
});

