// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([
    "knockout",
    "knockout.mapping",
    "samlab-content",
    "samlab-dialog",
    "samlab-object",
    ], function(ko, mapping, content, dialog, object)
{
    var component_name = "samlab-content-list-control";
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

                console.log(params);

                component.content = params.content;

                component.show_content = function(item)
                {
                    content.show(component.otype, component.oid, item.role, item["content-type"]);
                }

                component.download_content = function(item)
                {
                    window.open("/" + component.otype() + "/" + component.oid() + "/content/" + item.role() + "/data", "_blank");
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
                                object.delete_content(component.otype, component.oid, item.role);
                            }
                        },
                        message: "This will delete <b>" + item.role() + "</b>, and close any related dashboard widgets.",
                        title: "Delete Content?",
                    });
                }

                return component;
            }
        },
        template: { require: "text!" + component_name + ".html" }
    });
});
