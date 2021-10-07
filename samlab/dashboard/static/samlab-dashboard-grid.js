define(["debug", "gridstack-h5", "knockout", "knockout.mapping"], function(debug, gridstack, ko, mapping)
{
    var component_name = "samlab-dashboard-grid";
    var log = debug(component_name);

    ko.components.register(component_name,
    {
        viewModel:
        {
            createViewModel: function(params, component_info)
            {
                var grid = null;

                var component = mapping.fromJS({
                });

                component.widgets = params.widgets;

                component.afterAddWidget = function(elements)
                {
                    // Initialize the grid as-needed.
                    if(!grid)
                    {
                        grid = gridstack.init({auto: false});
                    }

                    // Knockout passes an array of elements, some of which are empty text nodes.
                    var element = elements.find(function(i)
                    {
                        return i.nodeType == 1
                    });

                    // Register the new element with the grid.
                    grid.addWidget(element);
                }

                component.beforeRemoveWidget = function(element, index, item)
                {
                    // Weirdly, knockout will call this multiple times with empty text nodes,
                    // so we need to find the actual element to delete.
                    if(element.nextElementSibling)
                        grid.removeWidget(element.nextElementSibling);
                }

                return component;
            }
        },
        template: { require: "text!" + component_name + ".html" }
    });
});
