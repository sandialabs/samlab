define(["debug", "gridstack-h5", "knockout", "knockout.mapping"], function(debug, gridstack, ko, mapping)
{
    var log = debug("samlab-gridstack-binding");

    ko.bindingHandlers.gridStack =
    {
        init: function(element, valueAccessor, allBindings, viewModel, bindingContext)
        {
            var template = element.firstElementChild;
            ko.virtualElements.emptyNode(element);

            var grid = gridstack.init({}, element);
            var grid_items = [];
            var updating = false;

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
