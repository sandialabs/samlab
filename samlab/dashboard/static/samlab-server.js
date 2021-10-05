// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define(["knockout.mapping"], function(mapping)
{
    var module =
    {
        load_json: function(model, url, method, params)
        {
            var request = new XMLHttpRequest();
            request.model = model;
            request.params = params || {};
            request.open(method || "GET", url, true);
            request.onload = function()
            {
                if(request.status >= 200 && request.status < 400)
                {
                    mapping.fromJSON(request.responseText, request.model);
                    if(request.params.success)
                        request.params.success();
                    if(request.params.finished)
                        request.params.finished();
                }
                else
                {
                    if(request.params.error)
                        request.params.error();
                    if(request.params.finished)
                        request.params.finished();
                }
            };
            request.send();
        },

        get_text: function(url, callback)
        {
            var request = new XMLHttpRequest();
            request.callback = callback;
            request.open("GET", url, true);
            request.onload = function()
            {
                if(request.status >= 200 && request.status < 400)
                {
                    if(request.callback)
                        request.callback(request.responseText);
                }
            };
            request.send();
        },

        get_json: function(url, params)
        {
            var request = new XMLHttpRequest();
            request.params = params || {};
            request.open("GET", url, true);
            request.onload = function()
            {
                if(request.status >= 200 && request.status < 400)
                {
                    if(request.params.success)
                        request.params.success(JSON.parse(request.responseText));
                    if(request.params.finished)
                        request.params.finished();
                }
                else
                {
                    if(request.params.error)
                        request.params.error();
                    if(request.params.finished)
                        request.params.finished();
                }
            };
            request.send();
        },

        post_json: function(url, data, params)
        {
            var request = new XMLHttpRequest();
            request.params = params || {};
            request.open("POST", url, true);
            request.setRequestHeader("Content-Type", "application/json");
            request.onload = function()
            {
                if(request.status >= 200 && request.status < 400)
                {
                    if(request.params.success)
                        request.params.success(JSON.parse(request.responseText));
                    if(request.params.finished)
                        request.params.finished();
                }
                else
                {
                    if(request.params.error)
                        request.params.error();
                    if(request.params.finished)
                        request.params.finished();
                }
            };
            request.send(JSON.stringify(data));
        },

        put_json: function(url, data, params)
        {
            var request = new XMLHttpRequest();
            request.params = params || {};
            request.open("PUT", url, true);
            request.setRequestHeader("Content-Type", "application/json");
            request.onload = function()
            {
                if(request.status >= 200 && request.status < 400)
                {
                    if(request.params.success)
                        request.params.success();
                }
                else
                {
                    if(request.params.error)
                        request.params.error(request);
                }
                if(request.params.finished)
                    request.params.finished();
            };
            request.send(JSON.stringify(data));
        },

        delete: function(url, params)
        {
            var request = new XMLHttpRequest();
            request.params = params || {};
            request.open("DELETE", url, true);
            request.onload = function()
            {
                if(request.status >= 200 && request.status < 400)
                {
                    if(request.params.success)
                        request.params.success();
                    if(request.params.finished)
                        request.params.finished();
                }
                else
                {
                    if(request.params.error)
                        request.params.error();
                    if(request.params.finished)
                        request.params.finished();
                }
            };
            request.send();
        },
    };

    return module;
});

