odoo.define('kitchen_pos.reloadListView', function (require) {
  'use strict';

  var core = require('web.core');
  var _t = core._t;
  var rpc = require('web.rpc');
  var Dialog = require('web.Dialog');
  var ListView = require('web.ListView');
  var ListRenderer = require('web.ListRenderer');
  var viewRegistry = require('web.view_registry');
  var ListController = require('web.ListController');

  var KitchenReloadController = ListController.extend({

    events: _.extend({}, ListController.prototype.events, {
      'drop .ready-products': 'drop_in_ready',
      'drop .in_progress_items' : 'drop_in_progress',
      // 'click .kitchen-td-product': 'productSelect',
      'click .remove-from-kitchen': 'removeFromKitchenScreen',
      'click .remove-order': 'removeOrder'
    }),

    removeOrder: function (event) {
      event.preventDefault();
      var line_id = parseInt($(event.target).closest('td').attr('kitchen-line-id'));
      var order_receipt = $(event.target).closest('td').attr('order_name');
      if (order_receipt == undefined) {
        var order_receipt = $(event.target).closest('.remove-from-kitchen').attr('order_name');
        var line_id = $(event.target).closest('.remove-from-kitchen').attr('kitchen-line');
      }
      var self = this;
      Dialog.confirm(self, _t("Are you sure you want to remove " + order_receipt + " from the Kitchen Screen."), {
        confirm_callback: function () {
          rpc.query({
            model: 'kitchen.pos.order',
            method: 'remove_order',
            args: [line_id]
          }).then(function () {
            self.trigger_up('reload');
          });
        },
      });
    },

    removeFromKitchenScreen: function (event) {
      var self = this;
      Dialog.confirm(self, _t("Are you sure you want to procceed this order??"), {
        confirm_callback: function () {
          if ($(event.target).hasClass('.remove-order') || $(event.target).closest('.remove-order').length > 0) {
            return true;
          }
          var line = $(event.target).closest('td');
          var line_id = parseInt(line.attr('kitchen-line-id'));
          if (!line_id){
            var line = $(event.target).closest('div.remove-from-kitchen');
            var line_id = parseInt(line.attr('kitchen-line-id'));
          }
          rpc.query({
            model: 'kitchen.pos.order',
            method: 'remove_from_kitchen',
            args: [line_id]
          }).then(function () {
            line.remove();
            self.trigger_up('reload');
          });
        },
      });
    },

    drop_in_ready: function (event) {
      var line_id = ''
      if (event.originalEvent.dataTransfer.getData("text")){
        var line_id = parseInt(event.originalEvent.dataTransfer.getData("text"))
      }
      var self = this;
      if (line_id){
        rpc.query({
          model: 'kitchen.pos.order',
          method: 'product_to_ready',
          args: [line_id]
        }).then(function (data) {
          console.log("Product Ready")
          self.do_action({
            name: 'Kitchen Hot & Cold Orders',
            res_model: 'kitchen.pos.order',
            view_mode: 'tree',
            type: 'ir.actions.act_window',
            views: [[false, 'list']],
            context: {'type': self.initialState.context.type},
        });
        });
      }
    },

    drop_in_progress: function (event) {
      var line_id = ''
      if (event.originalEvent.dataTransfer.getData("text")){
        var line_id = parseInt(event.originalEvent.dataTransfer.getData("text"))
      }
      var self = this;
      if (line_id){
        rpc.query({
          model: 'kitchen.pos.order',
          method: 'product_to_inprogress',
          args: [line_id]
        }).then(function (data) {
          console.log("Product In Progress")
          self.do_action({
            name: 'Kitchen Hot & Cold Orders',
            res_model: 'kitchen.pos.order',
            view_mode: 'tree',
            type: 'ir.actions.act_window',
            views: [[false, 'list']],
            context: {'type': self.initialState.context.type},
        });
        });
      }
    },
  });

  var ListReloadRenderer = ListRenderer.extend({

    init: function (parent, state, params) {
      this._super.apply(this, arguments);
      var self = this;
      var kb_type = $('.kb_type').val();
      var interval1 = setInterval(() => {
        var oControlPanel = $('.o_control_panel');
        if (oControlPanel.length > 0) {
          oControlPanel.hide();
          clearInterval(interval1);
        }
      }, 100);
      var interval = setInterval(() => {
        var reloadClass = $('.list_reload');
        if (reloadClass.length > 0) {
          if ($('.kitchen_lo').length > 0 && $('.kb_type').length > 0) {
            var screenType = self.state.context.type;
            if (screenType != parseInt($('.kb_type').val())) {
              clearInterval(interval);
            }
            else {
              self._rpc({
                model: 'kitchen.pos.order',
                method: 'check_new_products'
              }).then(function (result) {
                if (result) {
                  self.trigger_up('reload');
                }
              });
            }
          }
        }
      }, 15000);
    },

    _onRowClicked: function (ev) {
      return;
    },

    async _renderView() {
      var self = this;
      await this._super.apply(this, arguments);
      self.$el.find('.kitchen-table').DataTable({
        'language': {
          'emptyTable': _t('There are no products available.')
        },
        'responsive': true,
        "paging": false,
        "searching": false,
        'bInfo': false
      });
    },
  });
  
  var ListReload = ListView.extend({
    config: _.extend({}, ListView.prototype.config, {
      Renderer: ListReloadRenderer,
      Controller: KitchenReloadController,
    }),

  });

  viewRegistry.add('list_reload', ListReload);
});
function drag(ev){
  ev.dataTransfer.setData("text", ev.target.id);
}
function allowDrop(ev) {
  ev.preventDefault();
}
function drop(ev) {
  ev.preventDefault();
  var data = ev.dataTransfer.getData("text");
  if (data){
    ev.currentTarget.appendChild(document.getElementById(data));
  }
}