// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define(["knockout", "knockout.mapping", "samlab-socket"], function(ko, mapping, socket)
{
    var component_name = "samlab-socket-test-widget";
    ko.components.register(component_name,
    {
        viewModel:
        {
            createViewModel: function(widget, component_info)
            {
                var component = mapping.fromJS(
                {
                    last_test: null,
                });

                component.send_test = function()
                {
                    socket.emit("test");
                }

                component.receive_test = function()
                {
                    component.last_test(new Date().toLocaleString());
                }

                component.dispose = function()
                {
                    socket.off("test", component.receive_test);
                }

                socket.on("test", component.receive_test);

                return component;
            },
        },

        template: { require: "text!" + component_name + ".html" },
    });
});
