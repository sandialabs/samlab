// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define(["debug", "gridstack-h5", "knockout", "knockout.mapping"], function(debug, gridstack, ko, mapping)
{
    var log = debug("samlab-gridstack-binding");

    ko.bindingHandlers.gridStack =
    {
        init: function(element, valueAccessor, allBindings, viewModel, bindingContext)
        {
            var template = element.firstElementChild;
            ko.virtualElements.emptyNode(element);

            var options = mapping.toJS(valueAccessor().options) || {};

            var grid = gridstack.init(options, element);
            var grid_items = [];

            var widgets = valueAccessor().widgets;
            widgets.subscribe(function(changes)
            {
                ko.utils.arrayForEach(changes, function(change)
                {
                    if(change.status == "added")
                    {
                        var widget = change.value;
                        var widget_context = bindingContext['createChildContext'](widget);
                        var widget_element = template.cloneNode(true);
                        element.appendChild(widget_element);
                        ko.applyBindings(widget_context, widget_element)
                        grid.makeWidget(widget_element);
                        log(widget_element);

                        // Sync ko state with gridstack state.
                        widget.x(widget_element.gridstackNode.x);
                        widget.y(widget_element.gridstackNode.y);
                        widget.width(widget_element.gridstackNode.w);
                        widget.height(widget_element.gridstackNode.h);
                    }
                    else if(change.status == "deleted")
                    {
                        var widget = change.value;
                        var widget_element = element.children[change.index];
                        grid.removeWidget(widget_element);
                    }
                });
            }, null, "arrayChange");

            grid.on("change", function(event, changes)
            {
                ko.utils.arrayForEach(changes, function(change)
                {
                    var index = Array.from(change.el.parentNode.children).indexOf(change.el);
                    var widget = widgets()[index];
                    // Sync ko state with gridstack state.
                    widget.x(change.x);
                    widget.y(change.y);
                    widget.width(change.w);
                    widget.height(change.h);
                });
            });

            ko.utils.domNodeDisposal.addDisposeCallback(element, function()
            {
                grid.destroy();
            });

            return {"controlsDescendantBindings": true};
        }
    };
});
