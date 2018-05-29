
.. image:: ../artwork/samlab.png
    :width: 200px
    :align: right

.. _getting-started:

Getting Started
===============

Let's explore how to integrate Samlab into your workflow. For this
example, we will be training a simple neural network model to smooth
waveforms. That is, if we feed our trained model the noisy green curve
in the following plot as input, we want the model to produce a smoothed
version of it (the smooth orange curve) as output:

.. code:: python

    import toyplot
    toyplot.plot(example, width=600, height=250);



.. raw:: html

    <div class="toyplot" id="t77292b7d1b52473c8c5df7dd760d50e2" style="text-align:center"><svg class="toyplot-canvas-Canvas" height="250.0px" id="t333e35d7e3e54b16b2c6ff54806a381d" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" viewBox="0 0 600.0 250.0" width="600.0px" xmlns="http://www.w3.org/2000/svg" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink"><g class="toyplot-coordinates-Cartesian" id="ta5a4e79d7c7a4c28b9c23dd9dfc5edeb"><clipPath id="t2ba8e6643fea4b38a4ec9467b1c93dd7"><rect height="170.0" width="520.0" x="40.0" y="40.0"></rect></clipPath><g clip-path="url(#t2ba8e6643fea4b38a4ec9467b1c93dd7)"><g class="toyplot-mark-Plot" id="t5769736b10e6485da52177b0c17a1877" style="fill:none"><g class="toyplot-Series"><path d="M 50.0 154.71606163984544 L 55.0 176.53822826552323 L 60.0 150.28683595774845 L 65.0 156.01553537846084 L 70.0 169.21883371441308 L 75.0 152.96340751758098 L 80.0 137.21322749542128 L 85.0 148.87620436077137 L 90.0 148.58860080242664 L 95.0 189.68116463614672 L 100.0 168.6091382951697 L 105.0 150.4337788151634 L 110.0 132.96608567548444 L 115.0 170.00140022917083 L 120.00000000000001 176.12267707380758 L 125.0 176.0838624218357 L 130.0 168.6547671467932 L 135.0 163.35775518068266 L 140.0 139.1502635117343 L 145.0 167.4941087193183 L 150.0 171.2071835383885 L 155.0 183.226465201953 L 160.0 179.6824184803745 L 165.0 169.5417949683151 L 170.0 145.38939372195318 L 175.0 153.98844252427773 L 180.0 141.61031098412795 L 185.0 174.90357723488654 L 190.00000000000003 178.25866255873575 L 195.0 158.8552421821915 L 200.0 166.1448416163073 L 205.0 159.9619944468218 L 210.0 140.76728352806617 L 215.0 121.60262803095863 L 220.0 105.77679485871143 L 225.0 108.01387047810432 L 230.0 105.72876351109673 L 235.0 111.64331077280525 L 240.0 96.22136227019686 L 245.0 52.41195541516402 L 250.0 51.01575555148673 L 255.0 61.39470579705825 L 260.0 60.73247955012472 L 265.0 98.75215295577482 L 270.0 94.21187333840717 L 275.0 110.65041606133464 L 280.0 113.15689848430017 L 285.0 112.82178687551968 L 290.0 98.98038787088095 L 295.0 95.03603630764758 L 300.0 79.62628937643362 L 305.0 106.1177690519455 L 310.0 131.80603010516552 L 315.0 133.65514741682608 L 320.0 143.7005565134189 L 325.0 146.35040992603462 L 330.00000000000006 139.8637194650394 L 335.0 140.5144222110702 L 340.0 130.14843771927968 L 345.0 101.82743660153805 L 350.0 119.67830266266256 L 355.0 120.96722705990385 L 360.0 115.32433467854428 L 365.0 119.14464332965039 L 370.0 100.20238284201372 L 375.0 144.1857314586926 L 380.0 106.97911946685807 L 385.0 127.91547483632121 L 390.0 124.03314995595031 L 394.99999999999994 111.12060190249069 L 400.0 125.51207785028107 L 405.0 117.04578872264923 L 410.0 104.14226285990809 L 415.0 94.55006198122905 L 420.0 111.52175675002213 L 425.0 74.73218696718186 L 430.0 70.57356775395371 L 435.0 91.69366219121184 L 440.0 80.1139458025836 L 445.0 79.38995753255989 L 450.0 70.88092855573908 L 455.00000000000006 136.17500188332124 L 460.0 111.96847357292195 L 465.0 109.17183434914882 L 470.0 106.1571707278208 L 475.0 114.03778481004689 L 480.0 99.97733967304339 L 485.0 81.9307204190784 L 490.0 76.96821358743219 L 495.0 51.462945269158716 L 500.0 50.0 L 505.0 57.32852380037872 L 510.0 76.16175965695162 L 515.0 86.87551166038445 L 520.0 71.91311670148856 L 525.0 73.41462695681355 L 530.0 79.7317511797306 L 535.0 70.05196343570665 L 540.0 89.6389721864046 L 545.0 99.01813858751959" style="stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0;stroke-width:2.0"></path></g><g class="toyplot-Series"><path d="M 50.0 162.24355991540665 L 55.0 161.08903452061932 L 60.0 158.18448912336976 L 65.0 156.57583004449242 L 70.0 154.93521501468794 L 75.0 158.8202264587214 L 80.0 157.93921646201542 L 85.0 157.95554344617267 L 90.0 155.3944934791753 L 95.0 155.48144531414837 L 100.0 158.05469748706244 L 105.0 162.3736569233307 L 110.0 164.57127501066645 L 115.0 166.21229216380604 L 120.00000000000001 160.5977475944269 L 125.0 160.47385541933227 L 130.0 162.7820114996906 L 135.0 168.3664981137427 L 140.0 169.44216680832085 L 145.0 168.71095768548835 L 150.0 165.30046116327918 L 155.0 163.67086953855528 L 160.0 161.25448685004915 L 165.0 165.22707726373275 L 170.0 166.42313880144582 L 175.0 165.0507008729795 L 180.0 163.1527426967966 L 185.0 160.96158447084633 L 190.00000000000003 157.76441653304087 L 195.0 155.12144256737486 L 200.0 149.76459282675634 L 205.0 146.03165499275372 L 210.0 138.34556457899927 L 215.0 130.94385882500703 L 220.0 123.9845388347854 L 225.0 111.3475514791028 L 230.0 99.24241382406558 L 235.0 90.42323852062026 L 240.0 83.65988868941649 L 245.0 82.87937292242353 L 250.0 81.34581768467939 L 255.0 81.89266796803915 L 260.0 82.0608443804275 L 265.0 83.90533600324113 L 270.0 89.07960627609859 L 275.0 93.97074858233867 L 280.0 95.99648009115816 L 285.0 101.0392900358049 L 290.0 104.71194305240388 L 295.0 109.0945290611171 L 300.0 112.76676688912644 L 305.0 116.45493482709693 L 310.0 119.45959400371024 L 315.0 124.07448670817573 L 320.0 127.97586464280151 L 325.0 130.44265877892423 L 330.00000000000006 131.94938473567055 L 335.0 130.74507328619706 L 340.0 128.70831631527685 L 345.0 125.97988151708034 L 350.0 120.85232295218913 L 355.0 121.3325465070395 L 360.0 117.60640175768258 L 365.0 117.35829477068718 L 370.0 119.82559625451078 L 375.0 118.87474061449169 L 380.0 119.3797240356447 L 385.0 119.57099670721192 L 390.0 117.90406554390725 L 394.99999999999994 117.27602989270893 L 400.0 113.64669936952332 L 405.0 110.0637068695593 L 410.0 103.69238386040735 L 415.0 100.09910744210308 L 420.0 96.6539234310023 L 425.0 91.52924339569995 L 430.0 86.39981448826546 L 435.0 89.95900771308915 L 440.0 91.89438677883282 L 445.0 91.63328428984687 L 450.0 95.12494915214009 L 455.00000000000006 99.95430660281713 L 460.0 100.87471521190952 L 465.0 101.07657905818671 L 470.0 100.80749639761697 L 475.0 98.64994269910804 L 480.0 89.07494248985013 L 485.0 83.00383695956755 L 490.0 79.33605088265674 L 495.0 77.19364431960825 L 500.0 72.51312564087957 L 505.0 69.56171311685402 L 510.0 69.31738320137096 L 515.0 68.54891096229032 L 520.0 72.79069173087319 L 525.0 78.23715157393094 L 530.0 90.01777515951852 L 535.0 99.70581698326473 L 540.0 108.20344191774059 L 545.0 118.36355518098266" style="stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-width:2.0"></path></g></g></g><g class="toyplot-coordinates-Axis" id="tc410167f3f3b438cb802e322958dc1fc" transform="translate(50.0,200.0)translate(0,10.0)"><line style="" x1="0" x2="495.0" y1="0" y2="0"></line><g><g transform="translate(0.0,6)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-2.78" y="8.555">0</text></g><g transform="translate(250.0,6)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-5.56" y="8.555">50</text></g><g transform="translate(500.0,6)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-8.34" y="8.555">100</text></g></g><g class="toyplot-coordinates-Axis-coordinates" style="visibility:hidden" transform=""><line style="stroke:rgb(43.9%,50.2%,56.5%);stroke-opacity:1.0;stroke-width:1.0" x1="0" x2="0" y1="-3.0" y2="4.5"></line><text style="alignment-baseline:alphabetic;fill:rgb(43.9%,50.2%,56.5%);fill-opacity:1.0;font-size:10px;font-weight:normal;stroke:none;text-anchor:middle" x="0" y="-6"></text></g></g><g class="toyplot-coordinates-Axis" id="teaf0d28be57c494e94ee9537e51fda5a" transform="translate(50.0,200.0)rotate(-90.0)translate(0,-10.0)"><line style="" x1="10.318835363853266" x2="150.0" y1="0" y2="0"></line><g><g transform="translate(0.0,-6)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-4.445" y="-4.440892098500626e-16">-2</text></g><g transform="translate(36.64586392933276,-6)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-2.78" y="-4.440892098500626e-16">0</text></g><g transform="translate(73.29172785866552,-6)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-2.78" y="-4.440892098500626e-16">2</text></g><g transform="translate(109.93759178799829,-6)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-2.78" y="-4.440892098500626e-16">4</text></g><g transform="translate(146.58345571733105,-6)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-2.78" y="-4.440892098500626e-16">6</text></g></g><g class="toyplot-coordinates-Axis-coordinates" style="visibility:hidden" transform=""><line style="stroke:rgb(43.9%,50.2%,56.5%);stroke-opacity:1.0;stroke-width:1.0" x1="0" x2="0" y1="3.0" y2="-4.5"></line><text style="alignment-baseline:hanging;fill:rgb(43.9%,50.2%,56.5%);fill-opacity:1.0;font-size:10px;font-weight:normal;stroke:none;text-anchor:middle" x="0" y="6"></text></g></g></g></svg><div class="toyplot-behavior"><script>(function()
    {
    var modules={};
    modules["toyplot/tables"] = (function()
        {
            var tables = [];
    
            var module = {};
    
            module.set = function(owner, key, names, columns)
            {
                tables.push({owner: owner, key: key, names: names, columns: columns});
            }
    
            module.get = function(owner, key)
            {
                for(var i = 0; i != tables.length; ++i)
                {
                    var table = tables[i];
                    if(table.owner != owner)
                        continue;
                    if(table.key != key)
                        continue;
                    return {names: table.names, columns: table.columns};
                }
            }
    
            module.get_csv = function(owner, key)
            {
                var table = module.get(owner, key);
                if(table != undefined)
                {
                    var csv = "";
                    csv += table.names.join(",") + "\n";
                    for(var i = 0; i != table.columns[0].length; ++i)
                    {
                      for(var j = 0; j != table.columns.length; ++j)
                      {
                        if(j)
                          csv += ",";
                        csv += table.columns[j][i];
                      }
                      csv += "\n";
                    }
                    return csv;
                }
            }
    
            return module;
        })();
    modules["toyplot/root/id"] = "t77292b7d1b52473c8c5df7dd760d50e2";
    modules["toyplot/root"] = (function(root_id)
        {
            return document.querySelector("#" + root_id);
        })(modules["toyplot/root/id"]);
    modules["toyplot/canvas/id"] = "t333e35d7e3e54b16b2c6ff54806a381d";
    modules["toyplot/canvas"] = (function(canvas_id)
        {
            return document.querySelector("#" + canvas_id);
        })(modules["toyplot/canvas/id"]);
    modules["toyplot/menus/context"] = (function(root, canvas)
        {
            var wrapper = document.createElement("div");
            wrapper.innerHTML = "<ul class='toyplot-context-menu' style='background:#eee; border:1px solid #b8b8b8; border-radius:5px; box-shadow: 0px 0px 8px rgba(0%,0%,0%,0.25); margin:0; padding:3px 0; position:fixed; visibility:hidden;'></ul>"
            var menu = wrapper.firstChild;
    
            root.appendChild(menu);
    
            var items = [];
    
            var ignore_mouseup = null;
            function open_menu(e)
            {
                var show_menu = false;
                for(var index=0; index != items.length; ++index)
                {
                    var item = items[index];
                    if(item.show(e))
                    {
                        item.item.style.display = "block";
                        show_menu = true;
                    }
                    else
                    {
                        item.item.style.display = "none";
                    }
                }
    
                if(show_menu)
                {
                    ignore_mouseup = true;
                    menu.style.left = (e.clientX + 1) + "px";
                    menu.style.top = (e.clientY - 5) + "px";
                    menu.style.visibility = "visible";
                    e.stopPropagation();
                    e.preventDefault();
                }
            }
    
            function close_menu()
            {
                menu.style.visibility = "hidden";
            }
    
            function contextmenu(e)
            {
                open_menu(e);
            }
    
            function mousemove(e)
            {
                ignore_mouseup = false;
            }
    
            function mouseup(e)
            {
                if(ignore_mouseup)
                {
                    ignore_mouseup = false;
                    return;
                }
                close_menu();
            }
    
            function keydown(e)
            {
                if(e.key == "Escape" || e.key == "Esc" || e.keyCode == 27)
                {
                    close_menu();
                }
            }
    
            canvas.addEventListener("contextmenu", contextmenu);
            canvas.addEventListener("mousemove", mousemove);
            document.addEventListener("mouseup", mouseup);
            document.addEventListener("keydown", keydown);
    
            var module = {};
            module.add_item = function(label, show, activate)
            {
                var wrapper = document.createElement("div");
                wrapper.innerHTML = "<li class='toyplot-context-menu-item' style='background:#eee; color:#333; padding:2px 20px; list-style:none; margin:0; text-align:left;'>" + label + "</li>"
                var item = wrapper.firstChild;
    
                items.push({item: item, show: show});
    
                function mouseover()
                {
                    this.style.background = "steelblue";
                    this.style.color = "white";
                }
    
                function mouseout()
                {
                    this.style.background = "#eee";
                    this.style.color = "#333";
                }
    
                function choose_item(e)
                {
                    close_menu();
                    activate();
    
                    e.stopPropagation();
                    e.preventDefault();
                }
    
                item.addEventListener("mouseover", mouseover);
                item.addEventListener("mouseout", mouseout);
                item.addEventListener("mouseup", choose_item);
                item.addEventListener("contextmenu", choose_item);
    
                menu.appendChild(item);
            };
            return module;
        })(modules["toyplot/root"],modules["toyplot/canvas"]);
    modules["toyplot/io"] = (function()
        {
            var module = {};
            module.save_file = function(mime_type, charset, data, filename)
            {
                var uri = "data:" + mime_type + ";charset=" + charset + "," + data;
                uri = encodeURI(uri);
    
                var link = document.createElement("a");
                if(typeof link.download != "undefined")
                {
                  link.href = uri;
                  link.style = "visibility:hidden";
                  link.download = filename;
    
                  document.body.appendChild(link);
                  link.click();
                  document.body.removeChild(link);
                }
                else
                {
                  window.open(uri);
                }
            };
            return module;
        })();
    modules["toyplot.coordinates.Axis"] = (
            function(canvas)
            {
                function sign(x)
                {
                    return x < 0 ? -1 : x > 0 ? 1 : 0;
                }
    
                function mix(a, b, amount)
                {
                    return ((1.0 - amount) * a) + (amount * b);
                }
    
                function log(x, base)
                {
                    return Math.log(Math.abs(x)) / Math.log(base);
                }
    
                function in_range(a, x, b)
                {
                    var left = Math.min(a, b);
                    var right = Math.max(a, b);
                    return left <= x && x <= right;
                }
    
                function inside(range, projection)
                {
                    for(var i = 0; i != projection.length; ++i)
                    {
                        var segment = projection[i];
                        if(in_range(segment.range.min, range, segment.range.max))
                            return true;
                    }
                    return false;
                }
    
                function to_domain(range, projection)
                {
                    for(var i = 0; i != projection.length; ++i)
                    {
                        var segment = projection[i];
                        if(in_range(segment.range.bounds.min, range, segment.range.bounds.max))
                        {
                            if(segment.scale == "linear")
                            {
                                var amount = (range - segment.range.min) / (segment.range.max - segment.range.min);
                                return mix(segment.domain.min, segment.domain.max, amount)
                            }
                            else if(segment.scale[0] == "log")
                            {
                                var amount = (range - segment.range.min) / (segment.range.max - segment.range.min);
                                var base = segment.scale[1];
                                return sign(segment.domain.min) * Math.pow(base, mix(log(segment.domain.min, base), log(segment.domain.max, base), amount));
                            }
                        }
                    }
                }
    
                var axes = {};
    
                function display_coordinates(e)
                {
                    var current = canvas.createSVGPoint();
                    current.x = e.clientX;
                    current.y = e.clientY;
    
                    for(var axis_id in axes)
                    {
                        var axis = document.querySelector("#" + axis_id);
                        var coordinates = axis.querySelector(".toyplot-coordinates-Axis-coordinates");
                        if(coordinates)
                        {
                            var projection = axes[axis_id];
                            var local = current.matrixTransform(axis.getScreenCTM().inverse());
                            if(inside(local.x, projection))
                            {
                                var domain = to_domain(local.x, projection);
                                coordinates.style.visibility = "visible";
                                coordinates.setAttribute("transform", "translate(" + local.x + ")");
                                var text = coordinates.querySelector("text");
                                text.textContent = domain.toFixed(2);
                            }
                            else
                            {
                                coordinates.style.visibility= "hidden";
                            }
                        }
                    }
                }
    
                canvas.addEventListener("click", display_coordinates);
    
                var module = {};
                module.show_coordinates = function(axis_id, projection)
                {
                    axes[axis_id] = projection;
                }
    
                return module;
            })(modules["toyplot/canvas"]);
    (function(tables, context_menu, io, owner_id, key, label, names, columns, filename)
            {
                tables.set(owner_id, key, names, columns);
    
                var owner = document.querySelector("#" + owner_id);
                function show_item(e)
                {
                    return owner.contains(e.target);
                }
    
                function choose_item()
                {
                    io.save_file("text/csv", "utf-8", tables.get_csv(owner_id, key), filename + ".csv");
                }
    
                context_menu.add_item("Save " + label + " as CSV", show_item, choose_item);
            })(modules["toyplot/tables"],modules["toyplot/menus/context"],modules["toyplot/io"],"t5769736b10e6485da52177b0c17a1877","data","plot data",["x", "y0", "y1"],[[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99], [0.47143516373249306, -0.7195405309739714, 0.7131664374521259, 0.40051454136041303, -0.3200741920045986, 0.5670887483031399, 1.4266771620205563, 0.7901536576032072, 0.8058500297176361, -1.4368349244677694, -0.2867991997479513, 0.7051468225947265, 1.6584709507071569, -0.3627838694878136, -0.6968612352959106, -0.6947428706124241, -0.28928945904223313, -0.0001975180621978101, 1.3209606740671878, -0.22594487916205241, -0.4285912037912343, -1.084560547930168, -0.8911391714598098, -0.3377002605030679, 0.9804512936770688, 0.5111460089711692, 1.18670009409355, -0.6303271324966468, -0.8134356726756455, 0.2455335148955049, -0.15230671330448647, 0.1851309403094859, 1.2327095132022077, 2.278647768829873, 3.1423650605147118, 3.0202734856670377, 3.1449864394352534, 2.8221916338269577, 3.663866346823099, 6.0548268622861325, 6.131026450123369, 5.564580519658413, 5.600722456342485, 3.5257448556524555, 3.773537055401002, 2.8763802709613033, 2.7395854376999558, 2.757874629049175, 3.5132886114473107, 3.728557192416754, 4.569565987348145, 3.123755910303839, 1.7217826288029952, 1.6208644288540812, 1.0726219796672263, 0.9280024712978419, 1.2820228034970798, 1.2465097782189396, 1.8122480842815347, 3.357906888907092, 2.3836705551397768, 2.3133256780356746, 2.621294533251709, 2.412795770145829, 3.446596502701328, 1.0461428688890324, 3.076746489727832, 1.9341152007050686, 2.1459985874827696, 2.8507192117998783, 2.0652840000366814, 2.52734373719873, 3.2315719626609045, 3.755079930554714, 2.828825617024488, 4.836668567802489, 5.063631109673384, 3.910972000422432, 4.542951446231561, 4.582464132924928, 5.0468564579758235, 1.4833397973510882, 2.804445412821294, 2.9570759650258283, 3.1216055079582268, 2.691509817081739, 3.4588785528341504, 4.443798394744047, 4.714634243570852, 6.106620437017259, 6.186462750025888, 5.786498169329366, 4.75864761064746, 4.1739293993866715, 4.990523325934514, 4.9085762741078485, 4.563810259853204, 5.092098405150598, 4.023109621670466, 3.511228312543651], [0.060611268840718, 0.1236211297632891, 0.2821408144322398, 0.3699356652770406, 0.459474557467889, 0.24744454766785987, 0.2955269178040843, 0.29463584948659555, 0.43440878385845594, 0.42966326413809874, 0.2892243770715376, 0.053511040112317526, -0.06642708395939809, -0.1559879226016018, 0.15043381056894894, 0.15719540174515995, 0.03122450992449765, -0.2735567677018718, -0.33226291236542693, -0.2923561373884444, -0.10622345246738968, -0.017286178243678306, 0.11459133421807147, -0.10221842206679906, -0.1674951769016427, -0.0925924303808939, 0.010991329021959605, 0.13057689699632574, 0.3050668718524675, 0.4493109246472235, 0.7416685970409505, 0.9453989738824491, 1.36487825965266, 1.7688368492640605, 2.1486516083671265, 2.8383331167660844, 3.498988173412071, 3.9803071741294276, 4.349426583853051, 4.392024338868356, 4.475720291061018, 4.44587516123058, 4.436696694994246, 4.336030948574921, 4.053637809592829, 3.786696780958761, 3.6761396107020645, 3.4009211055866597, 3.200480858158942, 2.96129501076484, 2.760877422843276, 2.5595904265763747, 2.3956068904039194, 2.1437425756007666, 1.9308193413635202, 1.7961905526478477, 1.7139588465185074, 1.7796858519888052, 1.8908447524774303, 2.0397529514194974, 2.319596732686551, 2.293387851063435, 2.496747485675534, 2.51028827638926, 2.3756317984532243, 2.42752609363768, 2.3999659071933475, 2.3895269298541275, 2.4805020623558023, 2.5147779987839565, 2.7128538596878964, 2.908400757251747, 3.256124747137116, 3.452232904130411, 3.640258707956154, 3.919945389388181, 4.199891247252303, 4.005643228884545, 3.9000171713586096, 3.914267210025425, 3.7237046478205076, 3.4601356153103247, 3.4099030100227377, 3.398886004301903, 3.41357157215145, 3.531323125378276, 4.0538923423421425, 4.385231537509706, 4.5854061648009985, 4.7023310416263815, 4.957776987054467, 5.118854511640434, 5.132189163319228, 5.174129625716978, 4.9426284240117795, 4.645380153180419, 4.002435912143824, 3.47369728873855, 3.0099273554733643, 2.455424763702863]],"toyplot");
    (function(axis, axis_id, projection)
            {
                axis.show_coordinates(axis_id, projection);
            })(modules["toyplot.coordinates.Axis"],"tc410167f3f3b438cb802e322958dc1fc",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 100.0, "min": 0.0}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 500.0, "min": 0.0}, "scale": "linear"}]);
    (function(axis, axis_id, projection)
            {
                axis.show_coordinates(axis_id, projection);
            })(modules["toyplot.coordinates.Axis"],"teaf0d28be57c494e94ee9537e51fda5a",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 6.186462750025888, "min": -2.0}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 150.0, "min": 0.0}, "scale": "linear"}]);
    })();</script></div></div>


Preliminaries
-------------

It's a good idea to turn-on Python's standard logging, as Samlab uses it
extensively for informational and debugging output:

.. code:: python

    import logging
    logging.basicConfig(level=logging.INFO)

In addition, we need to have a running instance of MongoDB that Samlab
will use to store the generated observations. For production use, you
will likely want to setup and administer a shared instance of MongoDB on
your own, but for tutorials and quick tests, Samlab provides a simple
way to quickly startup a MongoDB server that stores data in a temporary
location:

.. code:: python

    import samlab.database
    db_server = samlab.database.Server()


.. parsed-literal::

    INFO:samlab.database:Starting database server: mongod --dbpath /var/folders/tl/h2xygzzn1154jzjn_n01x860001l4n/T/tmpmug3yx1a --directoryperdb --replSet samlab --bind_ip 127.0.0.1 --port 56626


... note that the data is effectively lost once the temporary server is
stopped, so you would not want to use it for real work!

Now, we can create a database connection to the server:

.. code:: python

    database, fs = samlab.database.connect("example", db_server.uri)

Note that the "example" database is automatically created if it doesn't
already exist on the given server.

Data Ingestion
--------------

Before we can create a model, we'll need to generate some training data
and put it in the Samlab database. For this tutorial, we'll start with a
function that creates :ref:`observations` at random:

.. code:: python

    import numpy
    import samlab.serialize
    
    def generate_observation():
        kernel = numpy.ones(9)
        kernel /= numpy.sum(kernel)
    
        input_features = numpy.cumsum(numpy.random.normal(size=(100,)))
        output_features = numpy.convolve(input_features, kernel, mode="same")
    
        attributes = {"filter-width": 9, "acknowledgements": "For Bev, and all she does to make life great."}
        content = {
            "input": samlab.serialize.array(input_features),
            "output": samlab.serialize.array(output_features),
            }
        tags = ["example", "smoothing"]
        
        return attributes, content, tags

We'll use :func:`samlab.observation.create_many` with our function to
generate observations and store them in the database:

.. code:: python

    import samlab.observation
    with samlab.observation.create_many(database, fs) as observations:
        for i in range(1000):
            attributes, content, tags = generate_observation()
            observations.create(attributes=attributes, content=content, tags=tags)


.. parsed-literal::

    INFO:samlab.observation:Ingested 850 observations in 5.0s (169.91 observations/s).
    INFO:samlab.observation:Ingested 1000 observations in 5.9s (170.22 observations/s).


Typically, we would load training data from disk or a database, but in
this case we are generating input and output feature vectors on the fly
using random walks and convolution. Note that we create one set of input
and output feature vectors at a time, and pass them (along with
attributes and tags) to Samlab. This design ensures that we can ingest
large numbers of observations even if they don't all fit into memory at
once. In addition, the observation *contents* must all be serializable
to the MongoDB database, which is why we use
:func:`samlab.serialize.array` to convert our :class:`numpy.ndarray`
content to a serializable representation. There are many functions in
:mod:`samlab.serialize` to handle various content data types.

Training
--------

With our observations stored in the database, we're ready to train our
model, which will consist of the following steps:

-  Loading observations.
-  Extracting features and weights.
-  Partitioning the data.
-  Training models.
-  Storing results.

Loading Observations
~~~~~~~~~~~~~~~~~~~~

First, we'll load observations from the database using
:func:`samlab.static.load`:

.. code:: python

    import samlab.static
    observations, inputs, outputs, weights = samlab.static.load(database)


.. parsed-literal::

    INFO:samlab.static:Loading 1000 observations.


The set of four arrays returned - observations, inputs, outputs, and
weights - are known in Samlab as :ref:`static-data`. Collectively,
they store the observations retrieved from the database and the input
feature vectors, output feature vectors, and weights extracted from
those observations, respectively. For this reason, the lengths of the
four arrays are always the same:

.. code:: python

    print(len(observations), len(inputs), len(outputs), len(weights))


.. parsed-literal::

    1000 1000 1000 1000


If you examine a subset of the observations array, you will see that it
contains observation records from the database:

.. code:: python

    observations[0]




.. parsed-literal::

    {'_id': ObjectId('5b0d744418b5352931f531f4'),
     'attributes': {'filter-width': 9,
      'acknowledgements': 'For Bev, and all she does to make life great.'},
     'content': {'input': {'data': ObjectId('5b0d744418b5352931f531f0'),
       'content-type': 'application/x-numpy-array',
       'filename': None},
      'output': {'data': ObjectId('5b0d744418b5352931f531f2'),
       'content-type': 'application/x-numpy-array',
       'filename': None}},
     'created': datetime.datetime(2018, 5, 29, 15, 39, 48, 631000),
     'tags': ['example', 'smoothing']}



Each record is a subset of the observation that contains its metadata,
but not the raw content data. This ensures that the observation data
will fit in memory, while providing the information you will use to
extract features from each observation.

The input and output arrays default to empty values, and the weights
array defaults to uniform weights for all observations:

.. code:: python

    inputs[0]

.. code:: python

    outputs[0]

.. code:: python

    weights[0]




.. parsed-literal::

    1.0



We'll substitute real inputs and outputs in the next section.

Extracting Features and Weights
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Because you can (within reason) store any data you like in an
observation, it's up to you to extract the input and output feature
vectors that will be used for training. For an image classification
problem, you might store both an original image and a resampled
fixed-size image, and use observation tags to store the class. Or you
might use observation attribues to store a regression value.

In our case, since we explicitly stored the input and output vectors in
the observation content, we just need to pull them back out again, using
a custom callback function and :func:`samlab.static.map`:

.. code:: python

    import samlab.deserialize
    
    def extract_features(observation, input, output, weight):
        input = samlab.deserialize.array(fs, observation["content"]["input"])
        output = samlab.deserialize.array(fs, observation["content"]["output"])
        return input, output, weight

Our callback function receives one observation (and corresponding input,
output, and weight) at a time, returning new input, output, and weight
values that may-or-may-not differ from the inputs. Note that in this
case our function overwrites the input and output feature vectors with
data from the database, while leaving the weight values unchanged. Now,
we use our callback with :func:`samlab.static.map` to update our
static data arrays:

.. code:: python

    observations, inputs, outputs, weights = samlab.static.map(
            observations,
            inputs,
            outputs,
            weights,
            extract_features,
        )

This way of working may seem roundabout to you for our toy problem;
however, this approach to feature extraction provides tremendous
flexibility: for example, we could have computed the smoothed version of
our curve in the ``extract_features`` callback instead of storing it in
the database. In later examples, we'll see how we can extend this
approach to streaming data and data augmentation when we can't fit even
our features into memory simultaneously.

Partitioning Data
~~~~~~~~~~~~~~~~~

For this problem, we will want to partition our observations into a
training set to be used for training our model, a validation set that we
can use to determine when training should stop, and a test set that we
will use to evaluate the performance of our trained model. To do this,
Samlab provides :ref:`partition-generators`, which are functions that
return one-or-more partitions for a given set of observations. Each
partition includes a label and three arrays of indices that you use to
access subsets of your static data, for training, validation, and
testing:

.. code:: python

    import samlab.train
    
    for partition in samlab.train.random(
            inputs,
            outputs,
            validation_split=0.2,
            test_split=0.5,
            n=1,
        ):
        partition_label, training, validation, testing = partition
        print(partition_label, len(training), len(validation), len(testing))


.. parsed-literal::

    Random-0 400 100 500


Notice in this example that for our 1000 observations we used
:func:`samlab.train.random` to generate one partition (``n=1``) that
set aside 500 observations (``test_split=0.5``) for testing and 100 of
the remaining 500 observations (``validation_split=0.2``) for
validation, leaving 400 observations for training.

Training Models
~~~~~~~~~~~~~~~

Now that we have our feature vectors and partitions, we're ready to
train a model. For this example, we'll use a simple Keras neural network
to train using our input and output features:

.. code:: python

    from tensorflow.contrib import keras
    
    model = keras.models.Sequential()
    model.add(keras.layers.Dense(outputs.shape[1], input_shape=(inputs.shape[1],)))
    model.compile(loss="mse", optimizer="adam")
    
    history = model.fit(
        inputs[training],
        outputs[training],
        epochs=2000,
        validation_data=(inputs[validation], outputs[validation]),
        verbose=0,
    )


.. parsed-literal::

    /Users/tshead/miniconda3/lib/python3.6/site-packages/h5py/__init__.py:36: FutureWarning: Conversion of the second argument of issubdtype from `float` to `np.floating` is deprecated. In future, it will be treated as `np.float64 == np.dtype(float).type`.
      from ._conv import register_converters as _register_converters


And we can make predictions using our test partition:

.. code:: python

    predictions = model.predict(inputs[testing])

When we spot-check one of our predictions against the ground truth, we
see that the blue prediction plot obscures the orange ground truth plot,
indicating that our network is performing well:

.. code:: python

    canvas, axes, mark = toyplot.plot(inputs[testing][0], width=600, height=300)
    axes.plot(outputs[testing][0])
    axes.plot(predictions[0]);



.. raw:: html

    <div class="toyplot" id="tcf3013e3c3374df7b06ae87f8cc84028" style="text-align:center"><svg class="toyplot-canvas-Canvas" height="300.0px" id="t96148faef9dc47909ea1ff5f2f95e55c" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" viewBox="0 0 600.0 300.0" width="600.0px" xmlns="http://www.w3.org/2000/svg" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink"><g class="toyplot-coordinates-Cartesian" id="tb75553632d294e7094372cf1e25df4c5"><clipPath id="t7250a476e0a4486aa607336eb751f426"><rect height="220.0" width="520.0" x="40.0" y="40.0"></rect></clipPath><g clip-path="url(#t7250a476e0a4486aa607336eb751f426)"><g class="toyplot-mark-Plot" id="ta176548313dc4c4ba99431dc0ded0575" style="fill:none"><g class="toyplot-Series"><path d="M 50.0 66.69315096593988 L 55.0 83.11459077163326 L 60.0 87.76047132650659 L 65.0 79.16105662650146 L 70.0 91.44812424932856 L 75.0 107.13977702452802 L 80.0 93.09550354507303 L 85.0 79.99767821967446 L 90.0 93.12464187737422 L 95.0 92.84677294926243 L 100.0 74.71530206661188 L 105.0 90.53467879560664 L 110.0 85.9233944173578 L 115.0 96.02296926623441 L 120.00000000000001 105.62207121880718 L 125.0 122.47325091510854 L 130.0 132.49333547556324 L 135.0 148.74471611439756 L 140.0 120.4498046930393 L 145.0 104.85601803736944 L 150.0 105.51075218335365 L 155.0 118.90885482987461 L 160.0 134.21724261394567 L 165.0 133.43553601753848 L 170.0 137.15259969709334 L 175.0 139.98602400178873 L 180.0 137.2683559793537 L 185.0 133.91904420518216 L 190.00000000000003 118.11856356833073 L 195.0 118.32531131189465 L 200.0 126.85159460806975 L 205.0 121.40101918195856 L 210.0 101.47527421889436 L 215.0 83.76414409441337 L 220.0 83.93299579430065 L 225.0 79.95848544825384 L 230.0 65.96832657295404 L 235.0 59.99382588702731 L 240.0 55.62721369423098 L 245.0 65.06356029859204 L 250.0 80.51890800093923 L 255.0 78.05561259358367 L 260.0 111.13726609911541 L 265.0 114.66820134608079 L 270.0 116.87027410381421 L 275.0 108.50187550848803 L 280.0 100.59052858671174 L 285.0 81.69177483011899 L 290.0 68.76951330976027 L 295.0 70.80645968080472 L 300.0 65.713631233778 L 305.0 62.51962344580599 L 310.0 52.783662819812506 L 315.0 60.02330976048209 L 320.0 72.80766003855557 L 325.0 94.02418634903434 L 330.00000000000006 92.18376093440459 L 335.0 93.56263929129977 L 340.0 92.44813943291331 L 345.0 113.65100761161423 L 350.0 114.83736301401709 L 355.0 112.83769794340515 L 360.0 111.00170532113074 L 365.0 105.47503287261253 L 370.0 112.52181285236409 L 375.0 95.48617378511855 L 380.0 110.82927713569381 L 385.0 104.0164144551533 L 390.0 97.10918964585274 L 394.99999999999994 100.30698020723614 L 400.0 92.12083008922436 L 405.0 86.67292171013024 L 410.0 127.10168701677722 L 415.0 120.69097068498266 L 420.0 130.17222672859822 L 425.0 142.15032156030736 L 430.0 151.55334849977464 L 435.0 167.90226443963655 L 440.0 181.99107057906696 L 445.0 181.08560960007802 L 450.0 186.71325631168347 L 455.00000000000006 187.0482781674936 L 460.0 208.96815574472083 L 465.0 197.6299337290231 L 470.0 206.23780701170017 L 475.0 206.08362044989175 L 480.0 212.82241482259715 L 485.0 211.26575405306752 L 490.0 206.92963083396717 L 495.0 215.92620364352737 L 500.0 212.56594011113046 L 505.0 213.74179012178553 L 510.0 250.0 L 515.0 236.6067235648496 L 520.0 227.8214584418323 L 525.0 221.19806511226395 L 530.0 226.59213826679908 L 535.0 230.58146151548675 L 540.0 240.81713163032353 L 545.0 241.0694828271739" style="stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0;stroke-width:2.0"></path></g></g><g class="toyplot-mark-Plot" id="tc271d3fa858e4e57a667c936263429e6" style="fill:none"><g class="toyplot-Series"><path d="M 50.0 67.57526599332331 L 55.0 73.92413010715974 L 60.0 78.71251938994564 L 65.0 82.04559474768725 L 70.0 86.83722162295105 L 75.0 89.743179621098 L 80.0 88.80992532054006 L 85.0 89.11817059488452 L 90.0 89.8695414605352 L 95.0 90.37785757352476 L 100.0 90.20922359511134 L 105.0 93.4734177473375 L 110.0 99.30626855354737 L 115.0 105.48627680210552 L 120.00000000000001 108.55328032919184 L 125.0 111.9022487703871 L 130.0 113.56625692458121 L 135.0 117.23130808152754 L 140.0 121.47511623127323 L 145.0 124.56550120891005 L 150.0 126.19653996246392 L 155.0 127.02906090982233 L 160.0 125.7539097837063 L 165.0 127.2504919517222 L 170.0 128.72410812182903 L 175.0 130.14794802500023 L 180.0 131.03047466702193 L 185.0 129.60644984124556 L 190.00000000000003 126.05530964139622 L 195.0 120.12325901887621 L 200.0 113.89514477359978 L 205.0 107.52738138125535 L 210.0 99.97730164434108 L 215.0 93.51899745752962 L 220.0 86.5525421666781 L 225.0 79.68720502118059 L 230.0 75.14474822328951 L 235.0 72.54256359825501 L 240.0 75.58402159877744 L 245.0 78.99904443786414 L 250.0 83.10035428848197 L 255.0 87.82630417020796 L 260.0 92.33704891461734 L 265.0 95.23311126304934 L 270.0 95.64488381984582 L 275.0 94.5657228953864 L 280.0 93.19439163318579 L 285.0 87.79243133837365 L 290.0 80.9163715021216 L 295.0 74.60004213064025 L 300.0 70.63401818953665 L 305.0 69.9044246075725 L 310.0 71.070200841382 L 315.0 73.82499261710862 L 320.0 76.22962370067626 L 325.0 81.55599885376917 L 330.00000000000006 87.36908102801485 L 335.0 94.04175159730292 L 340.0 99.70601777070833 L 345.0 103.33572586338131 L 350.0 105.3910176970846 L 355.0 105.75795245827507 L 360.0 107.67646777431882 L 365.0 108.96183166567883 L 370.0 107.12385189170533 L 375.0 105.50936491317412 L 380.0 103.20749070715402 L 385.0 100.50429252815398 L 390.0 102.90725409972782 L 394.99999999999994 103.81493830335211 L 400.0 107.66894418596095 L 405.0 111.14906023314025 L 410.0 116.43094179365372 L 415.0 124.29683899296305 L 420.0 133.37284903427755 L 425.0 143.2578245354835 L 430.0 154.37341726898947 L 435.0 161.03414961906904 L 440.0 170.84272573681773 L 445.0 178.33802651464268 L 450.0 185.45885823146418 L 455.00000000000006 191.5177773370327 L 460.0 196.50890515736168 L 465.0 199.76164776558394 L 470.0 202.63320568046052 L 475.0 205.87908871733205 L 480.0 208.7143844888473 L 485.0 209.24478830852112 L 490.0 215.0636845608519 L 495.0 218.4380086223129 L 500.0 220.8533239547508 L 505.0 221.78395176471375 L 510.0 223.48688334401723 L 515.0 226.1148645308528 L 520.0 228.88052319605234 L 525.0 232.04758349783495 L 530.0 213.854051262081 L 535.0 191.6318290398588 L 540.0 170.89774864376437 L 545.0 151.13980881689412" style="stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-width:2.0"></path></g></g><g class="toyplot-mark-Plot" id="t4da7c39a8e0b49dbbd7e6bbc514c2cb0" style="fill:none"><g class="toyplot-Series"><path d="M 50.0 69.02763832505414 L 55.0 73.17508090225206 L 60.0 78.6877662445738 L 65.0 82.12695266037468 L 70.0 86.82534807255804 L 75.0 89.69317924640173 L 80.0 88.73796940815204 L 85.0 89.24588557278 L 90.0 93.6281177975932 L 95.0 91.34984535879475 L 100.0 89.51831206102814 L 105.0 95.94425767473516 L 110.0 99.34296870189341 L 115.0 105.45744818397958 L 120.00000000000001 110.07683642815323 L 125.0 111.91589160362474 L 130.0 113.42425868116536 L 135.0 117.33343342861215 L 140.0 120.40587340208297 L 145.0 124.72111973716008 L 150.0 126.5658245565428 L 155.0 126.90486358585265 L 160.0 127.64845335598676 L 165.0 127.22570735770704 L 170.0 128.7418543627716 L 175.0 130.13042592962393 L 180.0 131.0885758886845 L 185.0 129.45192510853465 L 190.00000000000003 125.79361321817835 L 195.0 120.28673674199659 L 200.0 113.96543307513443 L 205.0 107.56463359273279 L 210.0 99.65628510562124 L 215.0 93.51936627011908 L 220.0 86.23006008248724 L 225.0 79.02669821066084 L 230.0 74.97879972377565 L 235.0 72.61840430266273 L 240.0 75.63368075078722 L 245.0 78.96416779811999 L 250.0 83.83695272899057 L 255.0 87.59635700857407 L 260.0 92.36473059031044 L 265.0 95.28576120504573 L 270.0 94.67764209950313 L 275.0 94.72608958042863 L 280.0 93.198396218566 L 285.0 87.57440630268782 L 290.0 80.95411348747805 L 295.0 74.54912481333275 L 300.0 70.4947448836515 L 305.0 68.91077744475508 L 310.0 71.12014097362317 L 315.0 73.79485342781553 L 320.0 76.31046856031159 L 325.0 81.55203138953473 L 330.00000000000006 87.17655936673778 L 335.0 93.98014990981447 L 340.0 99.73534717784779 L 345.0 103.75520882641179 L 350.0 105.3768433032603 L 355.0 106.35812989929052 L 360.0 107.59146528349464 L 365.0 108.84250727762455 L 370.0 106.11693018436101 L 375.0 105.40261534263746 L 380.0 103.35676892492005 L 385.0 102.51503786721304 L 390.0 102.91457585304127 L 394.99999999999994 102.8088138601732 L 400.0 106.70701874509861 L 405.0 111.14388341086254 L 410.0 116.48805673090806 L 415.0 124.17939630102276 L 420.0 133.41535620304694 L 425.0 142.65518136193555 L 430.0 155.44610694698824 L 435.0 160.78387294493038 L 440.0 170.70258325442603 L 445.0 178.12910331553354 L 450.0 184.75830433992303 L 455.00000000000006 191.50468194385826 L 460.0 197.7202016561656 L 465.0 199.77928548055928 L 470.0 202.87982543220065 L 475.0 205.54355841563364 L 480.0 208.6984974653042 L 485.0 209.2961628079635 L 490.0 214.9921788206822 L 495.0 218.48805109514302 L 500.0 220.64164703837758 L 505.0 221.7958983886684 L 510.0 223.38259731235183 L 515.0 226.39026129081367 L 520.0 228.8792231712525 L 525.0 230.65287095322162 L 530.0 211.21203447319346 L 535.0 191.1610474316002 L 540.0 171.87877432975975 L 545.0 151.16499456351062" style="stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-width:2.0"></path></g></g></g><g class="toyplot-coordinates-Axis" id="tafe7877429204e0196de0b9f4e30fff4" transform="translate(50.0,250.0)translate(0,10.0)"><line style="" x1="0" x2="495.0" y1="0" y2="0"></line><g><g transform="translate(0.0,6)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-2.78" y="8.555">0</text></g><g transform="translate(250.0,6)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-5.56" y="8.555">50</text></g><g transform="translate(500.0,6)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-8.34" y="8.555">100</text></g></g><g class="toyplot-coordinates-Axis-coordinates" style="visibility:hidden" transform=""><line style="stroke:rgb(43.9%,50.2%,56.5%);stroke-opacity:1.0;stroke-width:1.0" x1="0" x2="0" y1="-3.0" y2="4.5"></line><text style="alignment-baseline:alphabetic;fill:rgb(43.9%,50.2%,56.5%);fill-opacity:1.0;font-size:10px;font-weight:normal;stroke:none;text-anchor:middle" x="0" y="-6"></text></g></g><g class="toyplot-coordinates-Axis" id="t801d2ded10be4e5981d7b2ef583df363" transform="translate(50.0,250.0)rotate(-90.0)translate(0,-10.0)"><line style="" x1="0" x2="197.2163371801875" y1="0" y2="0"></line><g><g transform="translate(27.286267818684834,-6)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-7.2250000000000005" y="-4.440892098500626e-16">-15</text></g><g transform="translate(84.85751187912322,-6)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-7.2250000000000005" y="-4.440892098500626e-16">-10</text></g><g transform="translate(142.42875593956163,-6)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-4.445" y="-4.440892098500626e-16">-5</text></g><g transform="translate(200.0,-6)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-2.78" y="-4.440892098500626e-16">0</text></g></g><g class="toyplot-coordinates-Axis-coordinates" style="visibility:hidden" transform=""><line style="stroke:rgb(43.9%,50.2%,56.5%);stroke-opacity:1.0;stroke-width:1.0" x1="0" x2="0" y1="3.0" y2="-4.5"></line><text style="alignment-baseline:hanging;fill:rgb(43.9%,50.2%,56.5%);fill-opacity:1.0;font-size:10px;font-weight:normal;stroke:none;text-anchor:middle" x="0" y="6"></text></g></g></g></svg><div class="toyplot-behavior"><script>(function()
    {
    var modules={};
    modules["toyplot/tables"] = (function()
        {
            var tables = [];
    
            var module = {};
    
            module.set = function(owner, key, names, columns)
            {
                tables.push({owner: owner, key: key, names: names, columns: columns});
            }
    
            module.get = function(owner, key)
            {
                for(var i = 0; i != tables.length; ++i)
                {
                    var table = tables[i];
                    if(table.owner != owner)
                        continue;
                    if(table.key != key)
                        continue;
                    return {names: table.names, columns: table.columns};
                }
            }
    
            module.get_csv = function(owner, key)
            {
                var table = module.get(owner, key);
                if(table != undefined)
                {
                    var csv = "";
                    csv += table.names.join(",") + "\n";
                    for(var i = 0; i != table.columns[0].length; ++i)
                    {
                      for(var j = 0; j != table.columns.length; ++j)
                      {
                        if(j)
                          csv += ",";
                        csv += table.columns[j][i];
                      }
                      csv += "\n";
                    }
                    return csv;
                }
            }
    
            return module;
        })();
    modules["toyplot/root/id"] = "tcf3013e3c3374df7b06ae87f8cc84028";
    modules["toyplot/root"] = (function(root_id)
        {
            return document.querySelector("#" + root_id);
        })(modules["toyplot/root/id"]);
    modules["toyplot/canvas/id"] = "t96148faef9dc47909ea1ff5f2f95e55c";
    modules["toyplot/canvas"] = (function(canvas_id)
        {
            return document.querySelector("#" + canvas_id);
        })(modules["toyplot/canvas/id"]);
    modules["toyplot/menus/context"] = (function(root, canvas)
        {
            var wrapper = document.createElement("div");
            wrapper.innerHTML = "<ul class='toyplot-context-menu' style='background:#eee; border:1px solid #b8b8b8; border-radius:5px; box-shadow: 0px 0px 8px rgba(0%,0%,0%,0.25); margin:0; padding:3px 0; position:fixed; visibility:hidden;'></ul>"
            var menu = wrapper.firstChild;
    
            root.appendChild(menu);
    
            var items = [];
    
            var ignore_mouseup = null;
            function open_menu(e)
            {
                var show_menu = false;
                for(var index=0; index != items.length; ++index)
                {
                    var item = items[index];
                    if(item.show(e))
                    {
                        item.item.style.display = "block";
                        show_menu = true;
                    }
                    else
                    {
                        item.item.style.display = "none";
                    }
                }
    
                if(show_menu)
                {
                    ignore_mouseup = true;
                    menu.style.left = (e.clientX + 1) + "px";
                    menu.style.top = (e.clientY - 5) + "px";
                    menu.style.visibility = "visible";
                    e.stopPropagation();
                    e.preventDefault();
                }
            }
    
            function close_menu()
            {
                menu.style.visibility = "hidden";
            }
    
            function contextmenu(e)
            {
                open_menu(e);
            }
    
            function mousemove(e)
            {
                ignore_mouseup = false;
            }
    
            function mouseup(e)
            {
                if(ignore_mouseup)
                {
                    ignore_mouseup = false;
                    return;
                }
                close_menu();
            }
    
            function keydown(e)
            {
                if(e.key == "Escape" || e.key == "Esc" || e.keyCode == 27)
                {
                    close_menu();
                }
            }
    
            canvas.addEventListener("contextmenu", contextmenu);
            canvas.addEventListener("mousemove", mousemove);
            document.addEventListener("mouseup", mouseup);
            document.addEventListener("keydown", keydown);
    
            var module = {};
            module.add_item = function(label, show, activate)
            {
                var wrapper = document.createElement("div");
                wrapper.innerHTML = "<li class='toyplot-context-menu-item' style='background:#eee; color:#333; padding:2px 20px; list-style:none; margin:0; text-align:left;'>" + label + "</li>"
                var item = wrapper.firstChild;
    
                items.push({item: item, show: show});
    
                function mouseover()
                {
                    this.style.background = "steelblue";
                    this.style.color = "white";
                }
    
                function mouseout()
                {
                    this.style.background = "#eee";
                    this.style.color = "#333";
                }
    
                function choose_item(e)
                {
                    close_menu();
                    activate();
    
                    e.stopPropagation();
                    e.preventDefault();
                }
    
                item.addEventListener("mouseover", mouseover);
                item.addEventListener("mouseout", mouseout);
                item.addEventListener("mouseup", choose_item);
                item.addEventListener("contextmenu", choose_item);
    
                menu.appendChild(item);
            };
            return module;
        })(modules["toyplot/root"],modules["toyplot/canvas"]);
    modules["toyplot/io"] = (function()
        {
            var module = {};
            module.save_file = function(mime_type, charset, data, filename)
            {
                var uri = "data:" + mime_type + ";charset=" + charset + "," + data;
                uri = encodeURI(uri);
    
                var link = document.createElement("a");
                if(typeof link.download != "undefined")
                {
                  link.href = uri;
                  link.style = "visibility:hidden";
                  link.download = filename;
    
                  document.body.appendChild(link);
                  link.click();
                  document.body.removeChild(link);
                }
                else
                {
                  window.open(uri);
                }
            };
            return module;
        })();
    modules["toyplot.coordinates.Axis"] = (
            function(canvas)
            {
                function sign(x)
                {
                    return x < 0 ? -1 : x > 0 ? 1 : 0;
                }
    
                function mix(a, b, amount)
                {
                    return ((1.0 - amount) * a) + (amount * b);
                }
    
                function log(x, base)
                {
                    return Math.log(Math.abs(x)) / Math.log(base);
                }
    
                function in_range(a, x, b)
                {
                    var left = Math.min(a, b);
                    var right = Math.max(a, b);
                    return left <= x && x <= right;
                }
    
                function inside(range, projection)
                {
                    for(var i = 0; i != projection.length; ++i)
                    {
                        var segment = projection[i];
                        if(in_range(segment.range.min, range, segment.range.max))
                            return true;
                    }
                    return false;
                }
    
                function to_domain(range, projection)
                {
                    for(var i = 0; i != projection.length; ++i)
                    {
                        var segment = projection[i];
                        if(in_range(segment.range.bounds.min, range, segment.range.bounds.max))
                        {
                            if(segment.scale == "linear")
                            {
                                var amount = (range - segment.range.min) / (segment.range.max - segment.range.min);
                                return mix(segment.domain.min, segment.domain.max, amount)
                            }
                            else if(segment.scale[0] == "log")
                            {
                                var amount = (range - segment.range.min) / (segment.range.max - segment.range.min);
                                var base = segment.scale[1];
                                return sign(segment.domain.min) * Math.pow(base, mix(log(segment.domain.min, base), log(segment.domain.max, base), amount));
                            }
                        }
                    }
                }
    
                var axes = {};
    
                function display_coordinates(e)
                {
                    var current = canvas.createSVGPoint();
                    current.x = e.clientX;
                    current.y = e.clientY;
    
                    for(var axis_id in axes)
                    {
                        var axis = document.querySelector("#" + axis_id);
                        var coordinates = axis.querySelector(".toyplot-coordinates-Axis-coordinates");
                        if(coordinates)
                        {
                            var projection = axes[axis_id];
                            var local = current.matrixTransform(axis.getScreenCTM().inverse());
                            if(inside(local.x, projection))
                            {
                                var domain = to_domain(local.x, projection);
                                coordinates.style.visibility = "visible";
                                coordinates.setAttribute("transform", "translate(" + local.x + ")");
                                var text = coordinates.querySelector("text");
                                text.textContent = domain.toFixed(2);
                            }
                            else
                            {
                                coordinates.style.visibility= "hidden";
                            }
                        }
                    }
                }
    
                canvas.addEventListener("click", display_coordinates);
    
                var module = {};
                module.show_coordinates = function(axis_id, projection)
                {
                    axes[axis_id] = projection;
                }
    
                return module;
            })(modules["toyplot/canvas"]);
    (function(tables, context_menu, io, owner_id, key, label, names, columns, filename)
            {
                tables.set(owner_id, key, names, columns);
    
                var owner = document.querySelector("#" + owner_id);
                function show_item(e)
                {
                    return owner.contains(e.target);
                }
    
                function choose_item()
                {
                    io.save_file("text/csv", "utf-8", tables.get_csv(owner_id, key), filename + ".csv");
                }
    
                context_menu.add_item("Save " + label + " as CSV", show_item, choose_item);
            })(modules["toyplot/tables"],modules["toyplot/menus/context"],modules["toyplot/io"],"ta176548313dc4c4ba99431dc0ded0575","data","plot data",["x", "y0"],[[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99], [-1.449782025590361, -2.8759662321062143, -3.2794559109114934, -2.5326060868068208, -3.599724560912411, -4.962527556686337, -3.7427976629991964, -2.6052657632500393, -3.745328295503038, -3.7211956809793634, -2.1464971332446536, -3.520392815643628, -3.1199077771921457, -3.9970448804197654, -4.830716456328008, -6.2942231054644235, -7.164456563502572, -8.575871316132686, -6.118488999393602, -4.764185569776944, -4.821048519038287, -5.984659177899124, -7.314176025580954, -7.246285656946002, -7.569108599216685, -7.8151884217858205, -7.57916190657086, -7.2882778177490675, -5.916023240423617, -5.9339790573369084, -6.674477498470487, -6.201100944336174, -4.470571642055843, -2.93237923250084, -2.947043819191899, -2.6018619136320345, -1.3868318145244924, -0.867952920778972, -0.48871739581686957, -1.3082538465538702, -2.6505340034775386, -2.4365994735263006, -5.3097051398553585, -5.616363029969615, -5.807610656599124, -5.080824330204907, -4.39373244510764, -2.7523962133638196, -1.6301118393460465, -1.8070184186885094, -1.3647118010235983, -1.0873156946776135, -0.24175809166901308, -0.8705135631565979, -1.9808204956116677, -3.823452755582082, -3.663613807799603, -3.7833678950525766, -3.686574793168547, -5.528020859232546, -5.631054537048975, -5.45738579814586, -5.2979318335635615, -4.8179463357066545, -5.429951521173365, -3.950424776071112, -5.282956632988089, -4.691266910825029, -4.091381940296219, -4.369106576403299, -3.658148332265136, -3.1850034082667156, -6.69619775246091, -6.139434003785914, -6.9628707905315785, -8.003155313403319, -8.819797987443504, -10.239683575003394, -11.463281081828153, -11.38464277951542, -11.873397782420827, -11.90249406662292, -13.806211619974357, -12.821499356001492, -13.569083798821636, -13.555692863440203, -14.1409498335372, -14.005755536893599, -13.629167946173107, -14.41051052061145, -14.118675283486011, -14.220796579442432, -17.3697827156592, -16.206591208012593, -15.443600476581246, -14.868365961706504, -15.336835354939732, -15.683303745000892, -16.572260574220298, -16.59417700150694]],"toyplot");
    (function(tables, context_menu, io, owner_id, key, label, names, columns, filename)
            {
                tables.set(owner_id, key, names, columns);
    
                var owner = document.querySelector("#" + owner_id);
                function show_item(e)
                {
                    return owner.contains(e.target);
                }
    
                function choose_item()
                {
                    io.save_file("text/csv", "utf-8", tables.get_csv(owner_id, key), filename + ".csv");
                }
    
                context_menu.add_item("Save " + label + " as CSV", show_item, choose_item);
            })(modules["toyplot/tables"],modules["toyplot/menus/context"],modules["toyplot/io"],"tc271d3fa858e4e57a667c936263429e6","data","plot data",["x", "y0"],[[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99], [-1.5263927573697, -2.077784708112626, -2.4936511151125367, -2.7831250888069854, -3.1992726771962117, -3.4516519722394343, -3.370599850143705, -3.397370617336165, -3.4626263607123122, -3.506773062879796, -3.4921273850622043, -3.7756191008916744, -4.282195856475289, -4.818922858767471, -5.08528878303572, -5.376143053761529, -5.520660354138714, -5.8389660653283775, -6.20753619256851, -6.475932770414955, -6.617586714165206, -6.689890253974457, -6.579144764023141, -6.709121299395971, -6.837103262801157, -6.960762211501004, -7.037408691564489, -6.913733682537291, -6.6053210142161625, -6.0901288623588465, -5.549223906515077, -4.996190573966319, -4.34047435138581, -3.7795776492030724, -3.174548575700846, -2.578301503265666, -2.183794065392484, -1.9577971577780906, -2.2219444808174815, -2.518535504237228, -2.874729809011349, -3.285173421864728, -3.6769267023456913, -3.928446570962019, -3.9642085701611496, -3.870484616295702, -3.7513859860176244, -3.282231603220097, -2.6850532767422526, -2.136486933026416, -1.792042062516056, -1.7286776525687717, -1.8299240519505258, -2.069174724806807, -2.2780143219712556, -2.740604217327805, -3.2454640887024, -3.82497827831094, -4.316913641689491, -4.63214984614449, -4.810649708987965, -4.842517594351467, -5.00913856523319, -5.120771022750577, -4.9611444762020955, -4.820928036130354, -4.621012762143607, -4.386242937110625, -4.594937538972208, -4.673768925929158, -5.008485149758098, -5.3107294475820135, -5.769455122761844, -6.452599748840418, -7.24084136055429, -8.0993407435821, -9.064717896265892, -9.643195264506113, -10.495059444082607, -11.146018173579263, -11.764454671959077, -12.290665213736489, -12.724139242462467, -13.006636404136405, -13.256028089320592, -13.537929504675105, -13.784171862104339, -13.830236857600791, -14.335601675340534, -14.62865805413953, -14.83842556671076, -14.919249580951792, -15.067147338512473, -15.29538464949334, -15.53557909989432, -15.81063484634109, -14.230546337514154, -12.300570480218688, -10.499838123772845, -8.783882515263816]],"toyplot");
    (function(tables, context_menu, io, owner_id, key, label, names, columns, filename)
            {
                tables.set(owner_id, key, names, columns);
    
                var owner = document.querySelector("#" + owner_id);
                function show_item(e)
                {
                    return owner.contains(e.target);
                }
    
                function choose_item()
                {
                    io.save_file("text/csv", "utf-8", tables.get_csv(owner_id, key), filename + ".csv");
                }
    
                context_menu.add_item("Save " + label + " as CSV", show_item, choose_item);
            })(modules["toyplot/tables"],modules["toyplot/menus/context"],modules["toyplot/io"],"t4da7c39a8e0b49dbbd7e6bbc514c2cb0","data","plot data",["x", "y0"],[[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99], [-1.6525297164916992, -2.012730598449707, -2.4915013313293457, -2.7901909351348877, -3.1982414722442627, -3.4473094940185547, -3.3643505573272705, -3.4084625244140625, -3.7890546321868896, -3.59118914604187, -3.4321224689483643, -3.990208864212036, -4.285383224487305, -4.8164191246032715, -5.2176079750061035, -5.377327919006348, -5.508327960968018, -5.847835540771484, -6.114673614501953, -6.489448070526123, -6.649658679962158, -6.679103851318359, -6.743683815002441, -6.706968784332275, -6.838644504547119, -6.959240436553955, -7.042454719543457, -6.900313377380371, -6.582592964172363, -6.1043267250061035, -5.555328369140625, -4.999425888061523, -4.312594413757324, -3.7796096801757812, -3.1465413570404053, -2.520937204360962, -2.169381618499756, -1.964383840560913, -2.22625732421875, -2.5155065059661865, -2.9387025833129883, -3.265202760696411, -3.679330825805664, -3.9330191612243652, -3.880204677581787, -3.8844122886657715, -3.7517337799072266, -3.263296365737915, -2.688331127166748, -2.1320648193359375, -1.7799463272094727, -1.6423804759979248, -1.8342612981796265, -2.0665571689605713, -2.2850356101989746, -2.7402596473693848, -3.2287437915802, -3.8196282386779785, -4.319460868835449, -4.668581485748291, -4.809418678283691, -4.894642353057861, -5.001756191253662, -5.110407829284668, -4.87369441986084, -4.811656951904297, -4.63397741317749, -4.560873985290527, -4.595573425292969, -4.586388111114502, -4.924942970275879, -5.310279846191406, -5.774415493011475, -6.442399978637695, -7.244533061981201, -8.047001838684082, -9.157879829406738, -9.621459007263184, -10.482888221740723, -11.127873420715332, -11.703612327575684, -12.289527893066406, -12.829339027404785, -13.00816822052002, -13.277446746826172, -13.5087890625, -13.782792091369629, -13.834698677062988, -14.329391479492188, -14.633004188537598, -14.82004165649414, -14.920287132263184, -15.058090209960938, -15.319302558898926, -15.535466194152832, -15.689505577087402, -14.001090049743652, -12.259683609008789, -10.585039138793945, -8.786069869995117]],"toyplot");
    (function(axis, axis_id, projection)
            {
                axis.show_coordinates(axis_id, projection);
            })(modules["toyplot.coordinates.Axis"],"tafe7877429204e0196de0b9f4e30fff4",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 100.0, "min": 0.0}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 500.0, "min": 0.0}, "scale": "linear"}]);
    (function(axis, axis_id, projection)
            {
                axis.show_coordinates(axis_id, projection);
            })(modules["toyplot.coordinates.Axis"],"t801d2ded10be4e5981d7b2ef583df363",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 0.0, "min": -17.3697827156592}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 200.0, "min": 0.0}, "scale": "linear"}]);
    })();</script></div></div>


Storing Results
~~~~~~~~~~~~~~~

Now that our model has been trained, we're ready to save it to the
database for later analysis and re-use. We can store as much or as
little of our results as we like, but we will benefit from saving a few
standard artifacts:

.. code:: python

    content = {
        "model": samlab.serialize.keras_model(model),
        "observations": samlab.serialize.array([observation["_id"] for observation in observations]),
        "training-indices": samlab.serialize.array(training),
        "training-losses": samlab.serialize.array(history.history["loss"]),
        "validation-indices": samlab.serialize.array(validation),
        "validation-losses": samlab.serialize.array(history.history["val_loss"]),
        "test-indices": samlab.serialize.array(testing),
    }

... in this case saving ``model`` allows us to analyze it and use it in
the future to make new predictions, while ``observations``,
``training-indices``, ``validation-indices``, and ``test-indices`` can
be used to recreate the data used during training if necessary.
``training-losses`` and ``validation-losses`` are commonly used in
visualization to understand how successful the training process was and
whether there was overfitting.

By saving these standard artifacts, tools like the
:ref:`samlab-manager` can be used to perform sophisticated analysis
and post processing of experiment results.

Samlab requires that we explicitly store our experiment using a
:ref:`Samlab trial <trials>`, and the models we created as a
:ref:`Samlab model <models>`:

.. code:: python

    import samlab.trial
    trial = samlab.trial.create(
        database,
        fs,
        name="Example trial",
        attributes={"height":1.88, "location": "USA"},
        tags=["examples", "smoothing"],
    )

.. code:: python

    import samlab.model
    model = samlab.model.create(
        database,
        fs,
        trial,
        name=partition_label,
        content=content,
        attributes={"quality": 2.3},
        tags=["examples", "smoothing", "production"],
    )

Samlab Manager
--------------

Before we shut-down our temporary database server, let's take a quick
look through the database using the :ref:`samlab-manager`. Like the
temporary database server, Samlab provides an easy way to run the Samlab
Manager web server:

.. code:: python

    import samlab.manager
    manager = samlab.manager.Server(database=database.name, uri=db_server.uri)


.. parsed-literal::

    INFO:samlab.manager:Starting message queue: redis-server --bind 127.0.0.1 --save 
    INFO:samlab.manager:Starting generic task queue: huey_consumer samlab.tasks.generic.run.queue
    INFO:samlab.manager:Starting gpu task queue: huey_consumer samlab.tasks.gpu.run.queue
    INFO:samlab.manager:Starting Samlab manager: samlab-manager --database example --database-uri mongodb://127.0.0.1:56626 --host 127.0.0.1 --port 56658


This starts an instance of Samlab Manager, connected to the same
database we used to store our results.

Now, we can open a web browser to see the Samlab Manager user interface:

::

    manager.open_browser()

.. figure:: samlab-manager-1.png
   :alt: 

Samlab Manager provides a *dashboard* with *widgets* that you can add,
rearrange, resize, and delete in any way that you like. By default, the
*Database widget* is open, which represents the "example" database
created above. Use the Database widget operations menu to open an
*Observations widget*:

.. figure:: samlab-manager-2.png
   :alt: 

As you can see, the Observations widget displays the number of
observations that we created earlier (1000), provides controls for
choosing an observation, and displays the data ("input" and "output")
stored in the currently-visible observation (it also displays the
observation attributes and tags, though there aren't any in this
example):

.. figure:: samlab-manager-3.png
   :alt: 

If our observations contained image data, the images themselves would be
displayed. Note that you could use the Observations widget operations
menu to make changes to the current observation:

.. figure:: samlab-manager-4.png
   :alt: 

But for now, we will move-on to other things. Click the close button in
the upper-right-hand corner of the Observations widget to remove it, and
use the Database widget operations menu to open the trial that we just
created:

.. figure:: samlab-manager-5.png
   :alt: 

As you might expect, a *Trial widget* opens, displaying the trial's
name, attributes and tags (there are none in this example, of course).

.. figure:: samlab-manager-6.png
   :alt: 

Unsurprisingly, you can use the Trial widget operations menu to make
changes to the trial. You can also open the model we created as part of
the trial:

.. figure:: samlab-manager-7.png
   :alt: 

The *Model widget* opens as expected. As usual, it displays the
attributes and tags associated with the model, if any:

.. figure:: samlab-manager-8.png
   :alt: 

Using the Model widget operations menu, we can display a model-specific
visualization. In this case, let's see how the model's loss function
evolved during training:

.. figure:: samlab-manager-9.png
   :alt: 

As expected, the *Training Loss widget* opens, and provides an
interactive visualization. Note that storing standard artifacts with a
model is what makes this visualization possible:

.. figure:: samlab-manager-10.png
   :alt: 

Let's look directly at some of the model content. You should notice that
the Model widget operations menu includes entries for each of the
content roles we stored in the model. Let's open the *model* content:

.. figure:: samlab-manager-11.png
   :alt: 

The *Model Content widget* opens, and you can see that - because Samlab
knows that it is a Keras model - it can display a description of the
model layers:

.. figure:: samlab-manager-12.png
   :alt: 

Cleanup
-------

Now, we just need to cleanup the servers we started at the beginning of
this exercise. Stop the Samlab Manager server first:

.. code:: python

    manager.stop()


.. parsed-literal::

    INFO:samlab.manager:Stopping Samlab manager.
    INFO:samlab.manager:Samlab manager stopped.
    INFO:samlab.manager:Stopping gpu task queue.
    INFO:samlab.manager:GPU task queue stopped.
    INFO:samlab.manager:Stopping generic task queue.
    INFO:samlab.manager:Generic task queue stopped.
    INFO:samlab.manager:Stopping message queue.
    INFO:samlab.manager:Message queue stopped.


Finally, stop the temporary database server:

.. code:: python

    db_server.stop()


.. parsed-literal::

    INFO:samlab.database:Stopping database server.
    INFO:samlab.database:Database server stopped.

