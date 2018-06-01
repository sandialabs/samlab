// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([
    "element-resize-event",
    "knockout",
    "knockout.mapping",
    "samlab-dashboard",
    "samlab-grid",
    "samlab-object",
    "samlab-server",
    "samlab-socket",
    "css!samlab-image-classification-widget.css",
    ], function(resize_event, ko, mapping, dashboard, grid, object, server, socket)
{
    var component_name = "samlab-image-classification-widget";

    ko.components.register(component_name,
    {
        viewModel:
        {
            createViewModel: function(widget, component_info)
            {
                var component = mapping.fromJS({
                    images: [],
                    loading: true,
                    error: false,
                    model_id: widget.params.id,
                });

                var auto_delete_subscription = dashboard.auto_delete(widget, "models", widget.params.id);

                component.dispose = function()
                {
                    auto_delete_subscription.dispose();
                    socket.off("keras-model-evaluate-images", keras_model_evaluate_images_ready);
                }

                component.selection = widget.params.selection;

                component.selections =
                [
                    {label: "Everything", key: "everything"},
                    {label: "Correct predictions", key: "correct-predictions"},
                    {label: "Incorrect predictions", key: "incorrect-predictions"},
                ];

                var selection_labels =
                {
                    "everything": "Everything",
                    "correct-predictions": "Correct predictions",
                    "incorrect-predictions": "Incorrect predictions",
                }

                component.selection_formatted = ko.pureComputed(function()
                {
                    return selection_labels[component.selection()];
                });

                component.set_selection = function(data)
                {
                    component.selection(data.key);
                }

                component.filtered_images = ko.computed(function()
                {
                    var key = component.selection();

                    if(key == "everything")
                    {
                        return ko.utils.arrayFilter(component.images(), function(image)
                        {
                            return true;
                        });
                    }
                    else if(key == "correct-predictions")
                    {
                        return ko.utils.arrayFilter(component.images(), function(image)
                        {
                            return image.match();
                        });
                    }
                    else if (key == "incorrect-predictions")
                    {
                        return ko.utils.arrayFilter(component.images(), function(image)
                        {
                            return !image.match();
                        });
                    }
                });

                component.filtered_images.subscribe(function(images)
                {
                    component.grid.row_count(images.length);
                });

                component.cell_template = function(cell)
                {
                    return cell.column == 0 ? "image-cell" : cell.column == 1 ? "truth-cell" : "prediction-cell";
                }

                component.show_observation = function(cell, event)
                {
                    dashboard.add_widget("samlab-observation-widget", {id: cell.observation});
                }

                function create_cell(row, column)
                {
                    var image = component.filtered_images()[row];

                    var cell = {
                        image_key: "224x224",
                        observation: image.observation(),
                        output: image.output(),
                        prediction: image.prediction(),
                        match: image.match(),
                        }

                    return cell;
                }

                var grid_container = component_info.element.firstElementChild;
                var grid_viewport = document.querySelector("#grid-viewport");

                component.grid = grid.create(grid_viewport, {
                    row_count: 0,
                    column_count: 3,
                    cell_height: 100,
                    viewport_width: grid_container.offsetWidth - 40,
                    viewport_height: grid_container.offsetHeight - 200,
                    create_cell: create_cell,
                    });

                resize_event(grid_container, function()
                {
                    component.grid.viewport_width(grid_container.offsetWidth - 40);
                    component.grid.viewport_height(grid_container.offsetHeight - 200);
                });

                function keras_model_evaluate_images_ready(message)
                {
                    component.loading(false);
                    mapping.fromJS({images: message.images}, component);
                }

                socket.on("keras-model-evaluate-images", keras_model_evaluate_images_ready);

                socket.emit("keras-model-evaluate-images", {mid: component.model_id(), key: "model"});

                return component;
            },
        },
        template: { require: "text!" + component_name + ".html" }
    });

    var module =
    {
        widget: { params: {selection: "everything"}},
    };

    return module;
});
