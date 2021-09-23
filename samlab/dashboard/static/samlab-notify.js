// Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
// (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
// Government retains certain rights in this software.

define(["samlab-server", "samlab-socket", "bootstrap"], function(server, socket, bootstrap)
{
    var module = {};

    module.local = function(params)
    {
        var snack = document.createElement("div");
        snack.innerHTML = `<div class='toast text-white ${params.type || "bg-primary"} animate__animated animate__fadeInRight' role='alert'>
            <div class='d-flex'>
                <div class='toast-body'>
                    <span class='me-2 ${params.icon || ""}'></span>${params.message || ""}
                </div>
                <button type='button' class='btn-close btn-close-white me-2 m-auto' data-bs-dismiss='footoast'></button>
            </div>
        </div>`;
        snack = snack.firstChild;
        var toast = new bootstrap.Toast(snack, {"animation": false, "autohide": false});

        function close()
        {
            snack.classList.remove("animate__fadeInRight");
            snack.classList.add("animate__fadeOutRight");
            snack.addEventListener("animationend", function(e)
            {
                toast.hide();
            });
        }

        snack.querySelector("button").addEventListener("click", function(e)
        {
            close();
        });

        snack.addEventListener("hidden.bs.toast", function(e)
        {
            e.target.remove();
        });

        document.querySelector("#samlab-notify-container").appendChild(snack);
        toast.show();
        if(params.delay)
        {
            setTimeout(function()
            {
                close();
            }, params.delay * 1000);
        }
    }

    module.broadcast = function(params)
    {
        server.post_json("/notify", params);
    }

    socket.on("notify", function(params)
    {
        module.local(params);
    });

    return module;
});
