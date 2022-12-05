odoo.define('pos_restaurant.OrderLine', function (require) {
  'use strict';

  const PosComponent = require('point_of_sale.PosComponent');
  const ProductScreen = require('point_of_sale.ProductScreen');
  const { useListener } = require('web.custom_hooks');
  const Registries = require('point_of_sale.Registries');

  class OrderlineKitchenButton extends PosComponent {
    constructor() {
      super(...arguments);
      useListener('click', this.onClick);
    }
    get selectedOrderline() {
      return this.env.pos.get_order().get_selected_orderline();
    }
    async onClick() {
      if (!this.selectedOrderline) return;

      var self = this;
      var product = this.selectedOrderline.product;

      if (this.selectedOrderline.kitchen_option == true) {

        var productInfo = await this.rpc({
          model: 'product.product',
          method: 'search_read',
          args: [[['id', '=', product.id]], ['food_type', 'food_temperature', 'food_serve_as', 'food_doneness']],
        })
        productInfo = productInfo[0];

        var title_info = false;
        var foodServeAsDict = [];
        var foodDonenessDict = [];
        var foodServeAs = productInfo.food_serve_as;
        var foodDoneness = productInfo.food_doneness;

        if (productInfo.food_type) {
          title_info = productInfo.food_type.charAt(0).toUpperCase() + productInfo.food_type.slice(1);
        }

        if (productInfo.food_temperature) {
          title_info += ', ' + productInfo.food_temperature.charAt(0).toUpperCase() + productInfo.food_temperature.slice(1);
        }

        for (var i = 0; i < foodServeAs.length; i++) {
          foodServeAsDict.push({ id: foodServeAs[i], name: self.env.pos.db.get_food_serve_as(foodServeAs[i]) });
        }
        for (var i = 0; i < foodDoneness.length; i++) {
          foodDonenessDict.push({ id: foodDoneness[i], name: self.env.pos.db.get_food_doneness(foodDoneness[i]) });
        }

        var popupMaterial = {
          title: product.display_name,
          title_info: title_info,
          food_serve_as: foodServeAsDict,
          food_doneness: foodDonenessDict
        }

        const { confirmed, payload } = await this.showPopup('SaveProduct', popupMaterial);

        if (confirmed) {
          if (payload.food_type == null || payload.food_temperature == null) {
            await this.showPopup('ErrorPopup', {
              title: this.env._t('Invalid Entry'),
              body: this.env._t(
                'Please specify food type and temperature.'
              ),
            });
            return false;
          }

          this.selectedOrderline.set_kitchen_note(payload.kitchen_note);
          this.selectedOrderline.set_food_serve_as(payload.food_serve_as);
          this.selectedOrderline.set_food_doneness(payload.food_doneness);
          this.selectedOrderline.set_food_type(payload.food_type);
          this.selectedOrderline.set_food_temperature(payload.food_temperature);
          this.selectedOrderline.set_kitchen_option(this.selectedOrderline.kitchen_option);
        }
      }

    }

  }

  OrderlineKitchenButton.template = 'OrderLineKitchenButton';

  ProductScreen.addControlButton({
    component: OrderlineKitchenButton,
    condition: function () {
      return true;
    },
  });

  Registries.Component.add(OrderlineKitchenButton);

  return OrderlineKitchenButton;
});
