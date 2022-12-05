odoo.define('kitchen_pos.KitcheNotify', function (require) {
  'use strict';

  var rpc = require('web.rpc');
  var session = require('web.session');

  const interval = setInterval(() => {

    session.user_has_group('kitchen_pos.group_kitchen_notify').then(function (is_kitchen_notify) {
      if (is_kitchen_notify) {
        if ($('.kitchen_lo').length > 0) {
          try {
            rpc.query({
              model: 'kitchen.beep',
              method: 'check_beep',
              args: [session.uid]
            }).then(function (beep) {
              if (beep) {
                try {
                 document.getElementById('myAudio').muted = false;
                 document.getElementById('myAudio').play();
                }
                catch (err) { console.log(err); }
              }
            });

          }

          catch (err1) { console.log(err1) };

        }

      }

    });

  }, 10000);

});