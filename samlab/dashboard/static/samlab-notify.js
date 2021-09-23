// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define(["samlab-server", "samlab-socket", "bootstrap"], function(server, socket, bootstrap)
{
    var module = {};

    module.show = function(params)
    {
        var snack = document.createElement("div");
        snack.innerHTML = `<div class='toast text-white ${params.type || "bg-primary"}' role='alert'>
            <div class='d-flex'>
                <div class='toast-body'>
                    <span class='me-2 ${params.icon || ""}'></span>${params.message || ""}
                </div>
                <button type='button' class='btn-close btn-close-white me-2 m-auto' data-bs-dismiss='toast'></button>
            </div>
        </div>`;
        snack = snack.firstChild;
        console.log(snack);

        document.querySelector("#samlab-notify-container").appendChild(snack);
        snack.addEventListener("hidden.bs.toast", function(e)
        {
            e.target.remove();
        });

        var toast = new bootstrap.Toast(snack, {"autohide": true, delay: params.delay * 1000 || 8000});
        toast.show();
    }

    module.broadcast = function(params)
    {
        server.post_json("/notify", params);
    }

    socket.on("notify", function(params)
    {
        module.show(params);
    });

    return module;
});
