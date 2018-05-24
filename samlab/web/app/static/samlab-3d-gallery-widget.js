// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define([
    "debug",
    "element-resize-event",
    "jquery",
    "knockout",
    "knockout.mapping",
    "samlab-dashboard",
    "samlab-object",
    "three",
    "OrbitControls",
    "OBJLoader",
    "STLLoader",
    ], function(debug, resize_event, jquery, ko, mapping, dashboard, object, THREE)
{
    var log = debug("samlab-3d-gallery-widget");

    var component_name = "samlab-3d-gallery-widget";
    ko.components.register(component_name,
    {
        viewModel:
        {
            createViewModel: function(widget, component_info)
            {
                var component = mapping.fromJS({
                    content: widget.params.content,
                    description: widget.params.description,
                    label: widget.params.label || "3D Gallery",
                });

                var auto_delete_subscription = dashboard.auto_delete(widget, widget.params.otype, widget.params.oid);

                component.dispose = function()
                {
                    auto_delete_subscription.dispose();
                    renderer.dispose();
                }

                var container = jquery(component_info.element.querySelector(".container3d"));

                var scene = new THREE.Scene();
                scene.background = new THREE.Color(0xccccbb);

                var camera = new THREE.PerspectiveCamera(75, container.innerWidth() / container.innerHeight(), 0.1, 1000);
                camera.position.z = 1;
                scene.add(camera);

                var renderer = new THREE.WebGLRenderer({antialias: true});
                renderer.setPixelRatio(window.devicePixelRatio);
                renderer.setSize(container.innerWidth(), container.innerHeight());
                container.append(renderer.domElement);

                var controls = new THREE.OrbitControls(camera, renderer.domElement);
                controls.addEventListener("change", render);
                controls.enableZoom = true;
                controls.saveState();

                var light = new THREE.HemisphereLight(0x8888ff, 0x558844, 0.25);
                scene.add(light);

                var light = new THREE.DirectionalLight(0xffffff, 1.0);
                light.position.set(5, 5, 5);
                camera.add(light);

                for(let content of component.content())
                {
                    content = mapping.toJS(content);

                    if(content["content-type"] == "model/stl")
                    {
                        var loader = new THREE.STLLoader();
                        loader.load("/" + content.otype + "/" + content.oid + "/content/" + content.role + "/data", function(geometry)
                        {
                            geometry.computeBoundingBox();
                            var center = geometry.boundingBox.getCenter();
                            var offset = center.negate();

                            var size = geometry.boundingBox.getSize(); // Axis aligned dimensions
                            var scale = 1 / Math.max(size.x, size.y, size.z);

                            geometry.translate(offset.x, offset.y, offset.z);
                            geometry.scale(scale, scale, scale);
                            geometry.translate(content.x || 0, content.y || 0, content.z || 0);

                            var material = new THREE.MeshPhongMaterial({
                                color: content.color || 0xff5533,
                                specular: 0x111111,
                                shininess: 200,
                                });
                            material.side = THREE.DoubleSide;
                            var mesh = new THREE.Mesh(geometry, material);

                            scene.add(mesh);
                            render();
                        });
                    }
                }

                function render()
                {
                    renderer.render(scene, camera);
                }

                resize_event(container[0], function()
                {
                    camera.aspect = container.innerWidth() / container.innerHeight();
                    camera.updateProjectionMatrix();
                    renderer.setSize(container.innerWidth(), container.innerHeight());
                    render();
                });

                component.reset_camera = function()
                {
                    controls.reset();
                }

                render();


                return component;
            }
        },
        template: { require: "text!" + component_name + ".html" }
    });
});
