odoo.define("kitchen_pos.kitchen", function (require) {
  "use strict";

  var rpc = require('web.rpc');
  var $btnKitchen = $('.btn-kitchen');

  rpc.query({
    'route': '/get_kitchen_view'
  }).then(function (path) {
    $btnKitchen.attr('href', path);
    $btnKitchen.attr('target', '_blank');
  });

});