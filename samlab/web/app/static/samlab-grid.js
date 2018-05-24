// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define(["knockout", "knockout.mapping"], function(ko, mapping)
{
    var module = {};

    module.create = function(viewport, params)
    {
        var grid = mapping.fromJS(
        {
            row_count: params.row_count || 0,
            column_count: params.column_count || 0,
            cell_width: params.cell_width || 150,
            cell_height: params.cell_height || 30,
            viewport_width: params.viewport_width || 500,
            viewport_height: params.viewport_height || 500,
        });
        grid.position = ko.observable([0, 0]).extend({rateLimit: {timeout: 100, method: "notifyWhenChangesStop"}});

        grid.row_count.subscribe(function(row_count)
        {
            grid.position([0, 0]);
            viewport.scrollLeft = 0;
            viewport.scrollTop = 0;
        });

        grid.height = ko.pureComputed(function()
        {
            var result = grid.row_count() * grid.cell_height();
            return result;
        });

        grid.width = ko.pureComputed(function()
        {
            var result = grid.column_count() * grid.cell_width();
            return result;
        });

        grid.visible_cells = ko.pureComputed(function()
        {
            var position = grid.position();
            var cell_width = grid.cell_width();
            var cell_height = grid.cell_height();
            var viewport_width = grid.viewport_width();
            var viewport_height = grid.viewport_height();
            var row_count = grid.row_count();
            var column_count = grid.column_count();

            var result = {
                column_begin: Math.floor(position[0] / cell_width),
                column_end: Math.min(column_count, Math.ceil((position[0] + viewport_width) / cell_width)),
                row_begin: Math.floor(position[1] / cell_height),
                row_end: Math.min(row_count, Math.ceil((position[1] + viewport_height) / cell_height)),
            };

            return result;
        });

        grid.cells = ko.pureComputed(function()
        {
            var visible_cells = grid.visible_cells();
            var cell_width = grid.cell_width();
            var cell_height = grid.cell_height();

            var cells = [];
            for(var row = visible_cells.row_begin; row != visible_cells.row_end; ++row)
            {
                for(var column = visible_cells.column_begin; column != visible_cells.column_end; ++column)
                {
                    var cell = grid.create_cell(row, column);

                    cell.column = column
                    cell.height = cell_height;
                    cell.left = column * cell_width;
                    cell.row = row
                    cell.top = row * cell_height;
                    cell.width = cell_width;

                    cells.push(cell);
                }
            }
            return cells;
        });

        grid.on_scroll = function(ignored, event)
        {
            grid.position([$(event.target).scrollLeft(), $(event.target).scrollTop()]);
        }

        grid.create_cell = params.create_cell || function(row, column)
        {
            return {
                html: "<span>" + row + "," + column + "</span>",
            };
        }

        return grid;
    }

    return module;
});
