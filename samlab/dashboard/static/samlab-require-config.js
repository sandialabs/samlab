// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

require.config({
    baseUrl: "/static",
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
