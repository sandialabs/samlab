// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([
    "debug",
    "knockout",
    "knockout.mapping",
    "samlab-content-manager",
    "samlab-dashboard",
    "samlab-dialog",
    "samlab-object-manager",
    ], function(debug, ko, mapping, content_manager, dashboard, dialog, object)
{
    var component_name = "samlab-content-list-control";
    var log = debug(component_name);

    ko.components.register(component_name,
    {
        viewModel:
        {
            createViewModel: function(params, component_info)
            {
                var component = mapping.fromJS({
                    otype: params.otype,
                    oid: params.oid,
                });

                component.content = params.content;

                component.is_image = function(item)
                {
                    return content_manager.is_image(item["content-type"]);;
                }

                component.bounding_boxes = function(item)
                {
                    dashboard.add_widget("samlab-bounding-box-widget", {otype: component.otype, oid: component.oid, key: item.key});
                }

                component.show_content = function(item)
                {
                    content_manager.show(component.otype, component.oid, item.key, item["content-type"]);
                }

                component.download_content = function(item)
                {
                    window.open("/" + component.otype() + "/" + component.oid() + "/content/" + item.key() + "/data", "_blank");
                }

                component.delete_content = function(item)
                {
                    dialog.dialog(
                    {
                        alert: "This operation is immediate and cannot be undone.",
                        buttons: [{label: "Delete", class_name: "btn-danger"}, {label: "Cancel", class_name: "btn-secondary"}],
                        callback: function(button)
                        {
                            if(button.label == "Delete")
                            {
                                object.delete_content(component.otype, component.oid, item.key);
                            }
                        },
                        message: "This will delete <b>" + item.key() + "</b>, and close any related dashboard widgets.",
                        title: "Delete Content?",
                    });
                }

                return component;
            }
        },
        template: { require: "text!" + component_name + ".html" }
    });
});
