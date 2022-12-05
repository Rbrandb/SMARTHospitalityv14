odoo.define('kitchen_pos.KitchenScreen', function (require) {
  'use strict';

  var core = require('web.core');
  var _t = core._t;
  var rpc = require('web.rpc');
  var Dialog = require('web.Dialog');
  var FormView = require('web.FormView');
  var FormRenderer = require('web.FormRenderer');
  var FormController = require('web.FormController');

  var KitchenController = FormController.extend({

    events: _.extend({}, FormController.prototype.events, {
      'click .btn-show-kitchen': 'showKitchen',
      'click .btn-show-bar': 'showBar',
      'click .kitchen-td-product': 'productSelect'
    }),

    showKitchen: function () {
      $('.kitchen-screen.d-none').toggleClass('d-none');
      $('.bar-screen:not(.d-none)').toggleClass('d-none');
    },

    showBar: function () {
      $('.bar-screen.d-none').toggleClass('d-none');
      $('.kitchen-screen:not(.d-none)').toggleClass('d-none');
    },

    productSelect: function (event) {
      var line_id = parseInt($(event.currentTarget).attr('kitchen-line-id'));
      var $product = $(event.currentTarget);
      var self = this;
      Dialog.confirm(self, _t("Are you sure you want to move this product to the ready products?"), {
        confirm_callback: function () {
          rpc.query({
            model: 'kitchen.pos.order',
            method: 'product_to_ready',
            args: [line_id]
          }).then(function (data) {
            var $readyProducts = $('.ready-products');
            $readyProducts.append(data);
            $product.empty();
            $product.removeAttr('kitchen-line-id');
            $product.removeClass('kitchen-td-product');
          });
        },
      });
    }

  });

  var KitchenRenderer = FormRenderer.extend({

    _renderView: function () {
      var self = this;

      // render the form and evaluate the modifiers
      var defs = [];
      this.defs = defs;
      this.inactiveNotebooks = [];
      var $form = this._renderNode(this.arch).addClass(this.className);
      delete this.defs;

      return Promise.all(defs).then(() => this.__renderView()).then(function () {
        self._updateView($form.contents());
        if (self.state.res_id in self.alertFields) {
          self.displayTranslationAlert();
        }
        self.$el.find('.kitchen-table').DataTable({
          'language': {
            'emptyTable': _t('There are no products available.')
          },
          'responsive': true
        });
      }).then(function () {
        if (self.lastActivatedFieldIndex >= 0) {
          self._activateNextFieldWidget(self.state, self.lastActivatedFieldIndex);
        }
      }).guardedCatch(function () {
        $form.remove();
      });
    },

  });

  var KitchenView = FormView.extend({
    config: _.extend({}, FormView.prototype.config, {
      Renderer: KitchenRenderer,
      Controller: KitchenController
    }),
  });

  var viewRegistry = require('web.view_registry');
  viewRegistry.add('kitchen_screen', KitchenView);
});