// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define(["knockout", "jquery", "jquery.gridster"], function(ko, jquery)
{
    ko.bindingHandlers.gridster =
    {
        helpers:
        {
            cloneNodes: function(nodesArray, shouldCleanNodes)
            {
                for(var i = 0, j = nodesArray.length, newNodesArray = []; i < j; i++)
                {
                    var clonedNode = nodesArray[i].cloneNode(true);
                    newNodesArray.push(shouldCleanNodes ? ko.cleanNode(clonedNode) : clonedNode);
                }
                return newNodesArray;
            }
        },
        init: function(element, valueAccessor, allBindings, viewModel, bindingContext)
        {
            var template = ko.bindingHandlers.gridster.helpers.cloneNodes(element.getElementsByClassName('grid-item'), true);
            ko.virtualElements.emptyNode(element);

            var params = ko.unwrap(valueAccessor());
            var options = ko.toJS(params.options || {})
            var gridster = jquery(element).gridster(options).data("gridster");
            var gridster_items = [];

            // Update gridster in response to knockout changes.
            params.widgets.subscribe(function(changes)
            {
                for(let change of changes)
                {
                    if(change.status == "added")
                    {
                        var inner_binding_context = bindingContext["createChildContext"](change.value);
                        var widget_element = ko.bindingHandlers.gridster.helpers.cloneNodes(template)[0];

                        var x = ko.unwrap(change.value.x);
                        var y = ko.unwrap(change.value.y);
                        var width = ko.unwrap(change.value.width);
                        var height = ko.unwrap(change.value.height);

                        // Knockout is zero-based, gridster is one-based.
                        if(x != null && x != undefined)
                            x += 1;
                        if(y != null && y != undefined)
                            y += 1;

                        gridster.add_widget(widget_element, width, height, x, y);
                        ko.applyBindings(inner_binding_context, widget_element)
                        gridster_items.push({widget: change.value, element: widget_element});

                        // If the caller didn't supply a default widget position, this will
                        // sync the actual position with knockout.
                        synchronize_widget_positions();

                        // Scroll the new widget into view
                        widget_element.scrollIntoView();
                    }
                    else if(change.status == "deleted")
                    {
                        var item = ko.utils.arrayFirst(gridster_items, function(item)
                        {
                            return item.widget == change.value;
                        });

                        gridster.remove_widget(item.element);
                        ko.cleanNode(item.element);
                    }
                    else
                    {
                        console.log("Unexpected change status:", change);
                    }

                    // TODO: Handle positioning / resizing from knockout (currently doesn't happen anywhere, but conceivable).
                }

            }, null, "arrayChange");


            // Update knockout in response to gridster changes.
            gridster.options.draggable.stop = function(event, ui)
            {
                synchronize_widget_positions();
            };

            gridster.options.resize.stop = function(event, ui)
            {
                var element = event.target.parentNode;
                var new_width = Number($(element).attr("data-sizex"));
                var new_height = Number($(element).attr("data-sizey"));

                var item = ko.utils.arrayFirst(gridster_items, function(item)
                {
                    return item.element == element;
                });

                item.widget.width(new_width);
                item.widget.height(new_height);

                synchronize_widget_positions();
            };

            function synchronize_widget_positions()
            {
                for(let item of gridster_items)
                {
                    var new_x = Number($(item.element).attr("data-col"));
                    var new_y = Number($(item.element).attr("data-row"));
                    item.widget.x(new_x-1); // Gridster is one-based, knockout is zero-based.
                    item.widget.y(new_y-1); // Gridster is one-based, knockout is zero-based.
                }
            }

            //console.log("gridster options:", gridster.options);

            return { controlsDescendantBindings: true };
        }
    };
});
