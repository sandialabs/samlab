// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([], function()
{
    var module = {}

    module.compatible = function()
    {
        var compatible = true;

        if(window.navigator.userAgent.indexOf("MSIE ") > 0)
            compatible = false;
        if(window.navigator.userAgent.indexOf("Trident/") > 0)
            compatible = false;
        if(window.navigator.userAgent.indexOf("Edge/") > 0)
            compatible = false;

        var url = new URL(window.location);
        if(url.searchParams.has("incompatible"))
            compatible = false;

        return compatible;
    };

    module.complain = function()
    {
        require(["samlab-modal"], function(modal)
        {
            modal.create("samlab-browser-incompatible.html", {});
        });
    }

    return module;
});

