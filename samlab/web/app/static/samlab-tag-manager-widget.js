// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define(["knockout", "knockout.mapping", "samlab-tag-manager", "samlab-dashboard"], function(ko, mapping, manager, dashboard)
{
    var component_name = "samlab-tag-manager-widget";

    ko.components.register(component_name,
    {
        viewModel:
        {
            createViewModel: function(widget, component_info)
            {
                var component = mapping.fromJS({
                    new_tag: null,
                    title: "Tag Manager",
                });

                component.disabled = ko.pureComputed(function()
                {
                    return manager.otype() == null || manager.oid() == null;
                });

                component.tags = ko.pureComputed(function()
                {
                    var result = [];

                    var tags = manager.tags();
                    var count = 0;
                    for(var index = 0; index != tags.length; ++index)
                    {
                        var tag = tags[index];
                        if(tag.indexOf("dataset:") == 0)
                        {
                            result.push({tag: tag, shortcut: null});
                        }
                        else
                        {
                            var shortcut = null;
                            if(count < 10)
                                shortcut = "" + ((++count) % 10)
                            result.push({tag: tag, shortcut: shortcut});
                        }
                    }

                    return result;
                });

                component.set_shortcuts = ko.computed(function()
                {
                    dashboard.unbind({widget: widget});
                    for(let tag of component.tags())
                    {
                        if(tag.shortcut)
                        {
                            dashboard.bind(
                            {
                                widget: widget,
                                keys: tag.shortcut,
                                callback: function()
                                {
                                    manager.toggle_tag(tag.tag);
                                },
                            });
                        }
                    }
                });


                component.toggle_tag = function(item)
                {
                    manager.toggle_tag(ko.utils.unwrapObservable(item.tag));
                }

                component.add_tag = function()
                {
                    manager.add_tag(component.new_tag());
                }

                return component;
            }
        },
        template: { require: "text!" + component_name + ".html" }
    });

    var module =
    {
        widget: { },
    };

    return module;
});

