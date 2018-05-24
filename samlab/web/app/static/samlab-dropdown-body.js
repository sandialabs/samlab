// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define(["jquery"], function(jquery)
{
    // Automatically reparents bootstrap dropdown menus to the document body, so
    // they can be used within grid widgets.

    // Keep track of the currently-reparented menu.
    var dropdown_menu = null;

    // If a dropdown is about to be shown ...
    jquery(window).on('show.bs.dropdown', function(e)
    {
        // And it isn't the child of a modal dialog ...
        if(!jquery(e.target).parents(".modal").length)
        {
            // Reparent the menu to the document body, and adjust its position.
            dropdown_menu = jquery(e.target).find('.dropdown-menu');
            jquery('body').append(dropdown_menu.detach());
            dropdown_menu.css('display', 'block');
            dropdown_menu.position({
              'my': 'right top',
              'at': 'right bottom',
              'of': jquery(e.relatedTarget)
            })
        }
    });

    // If a dropdown is about to be hidden ...
    jquery(window).on('hide.bs.dropdown', function(e)
    {
        // And it was previously reparented to the document body ...
        if(dropdown_menu)
        {
            // Reparent the menu back where it came from.
            jquery(e.target).append(dropdown_menu.detach());
            dropdown_menu.hide();
            dropdown_menu = null;
        }
    });
});
