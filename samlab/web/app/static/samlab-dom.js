// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([], function()
{
    var module = {};

    module.parse = function(template)
    {
        var container = document.createElement("div");
        container.innerHTML = template;
        return container.firstChild;
    };

    return module;
});
