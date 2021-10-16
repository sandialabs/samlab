// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define(["debug"], function(debug)
{
    log = debug("samlab-dropdown");

    // Automatically reparents bootstrap dropdown menus to the document body, so
    // they can be used within grid widgets.

    var body = document.querySelector("body");
    var dropdown_menu = null;

    body.addEventListener("show.bs.dropdown", function(event)
    {
        var menu = event.target.parentElement.querySelector(".dropdown-menu");
        var parent_modal = menu.closest(".modal");
        if(!parent_modal)
        {
            body.appendChild(menu);
        }
    });
});
