define(["debug", "gridstack-h5", "knockout"], function(debug, gridstack, ko)
{
    var component_name = "samlab-grid-control";
    var log = debug(component_name);

    ko.components.register(component_name,
    {
        viewModel:
        {
            createViewModel: function(controller, componentInfo)
            {
                let ViewModel = function(controller, componentInfo)
                {
                    let grid = null;

                    this.widgets = controller.widgets;

                    this.afterAddWidget = function(items)
                    {
                        if(!grid)
                        {
                            grid = gridstack.init({auto: false});
                        }

                        let item = items.find(function(i)
                        {
                            return i.nodeType == 1
                        });

                        grid.addWidget(item);
                        ko.utils.domNodeDisposal.addDisposeCallback(item, function()
                        {
                            grid.removeWidget(item);
                        });
                    };
                };

                return new ViewModel(controller, componentInfo);
            }
        },
        template:
        [
          '<div class="grid-stack" data-bind="foreach: {data: widgets, afterRender: afterAddWidget}">',
          '   <div class="grid-stack-item" data-bind="attr: {\'gs-x\': $data.x, \'gs-y\': $data.y, \'gs-w\': $data.w, \'gs-h\': $data.h, \'gs-auto-position\': $data.auto_position, \'gs-id\': $data.id}">',
          '     <div class="grid-stack-item-content"><button data-bind="click: $root.deleteWidget">Delete me</button></div>',
          '   </div>',
          '</div> '
        ].join('')
    });
});
