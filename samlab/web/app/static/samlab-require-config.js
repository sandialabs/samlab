// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

require.config({
    baseUrl: "/static",
    map:
    {
        "*":
        {
            "jquery-ui/data": "jquery.ui",
            "jquery-ui/disable-selection": "jquery.ui",
            "jquery-ui/focusable": "jquery.ui",
            "jquery-ui/form": "jquery.ui",
            "jquery-ui/ie": "jquery.ui",
            "jquery-ui/keycode": "jquery.ui",
            "jquery-ui/labels": "jquery.ui",
            "jquery-ui/jquery-1-7": "jquery.ui",
            "jquery-ui/plugin": "jquery.ui",
            "jquery-ui/safe-active-element": "jquery.ui",
            "jquery-ui/safe-blur": "jquery.ui",
            "jquery-ui/scroll-parent": "jquery.ui",
            "jquery-ui/tabbable": "jquery.ui",
            "jquery-ui/unique-id": "jquery.ui",
            "jquery-ui/version": "jquery.ui",
            "jquery-ui/widget": "jquery.ui",
            "jquery-ui/widgets/mouse": "jquery.ui",
            "jquery-ui/widgets/draggable": "jquery.ui",
            "jquery-ui/widgets/droppable": "jquery.ui",
            "jquery-ui/widgets/resizable": "jquery.ui",
        },
    },
    paths:
    {
        "bootstrap": "bootstrap.bundle.min",
        "bootstrap-notify": "bootstrap-notify.min",
        "css": "css.min",
        "jquery": "jquery.min",
        "jquery.ui": "jquery-ui.min",
        "knockout": "knockout-min",
        "knockout.mapping": "knockout.mapping.min",
        "lodash": "lodash.min",
        "mousetrap": "mousetrap.min",
        "socket.io": "socket.io",
        "text": "text.min",
        "URI": "URI",
    },
    urlArgs: "bust=" + (new Date()).getTime(),
});
