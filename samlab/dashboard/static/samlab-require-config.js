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
        "IPv6": "js/IPv6",
        "SecondLevelDomains": "js/SecondLevelDomains",
        "URI": "js/URI",
        "bootstrap": "js/bootstrap.bundle.min",
        "css": "js/css.min",
        "debug": "js/debug",
        "gridstack": "css/gridstack.min",
        "gridstack-h5": "js/gridstack-h5",
        "jquery": "js/jquery.min",
        "jquery.ui": "js/jquery-ui.min",
        "knockout": "js/knockout-3.5.1",
        "knockout-projections": "js/knockout-projections-1.1.0",
        "knockout.mapping": "js/knockout.mapping-2.4.1",
        "lodash": "js/lodash.min",
        "mousetrap": "js/mousetrap.min",
        "punycode": "js/punycode",
        "socket.io": "js/socket.io.min",
        "text": "js/text.min",
    },
    urlArgs: "bust=" + (new Date()).getTime(),
});
