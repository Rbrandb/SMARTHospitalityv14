odoo.define('kitchen_pos.barcode', function (require) {
  "use strict";

  const { Gui } = require('point_of_sale.Gui');
  var models = require('point_of_sale.models');

  models.PosModel = models.PosModel.extend({

    scan_product: async function (parsed_code) {

      var selectedOrder = this.get_order();
      var product = this.db.get_product_by_barcode(parsed_code.base_code);

      if (!product) {
        return false;
      }

      if (product.kitchen_option == false) {

        if (parsed_code.type === 'price') {
          selectedOrder.add_product(product, { price: parsed_code.value, extras: { price_manually_set: true } });
        } else if (parsed_code.type === 'weight') {
          selectedOrder.add_product(product, { quantity: parsed_code.value, merge: false });
        } else if (parsed_code.type === 'discount') {
          selectedOrder.add_product(product, { discount: parsed_code.value, merge: false });
        } else {
          selectedOrder.add_product(product);
        }
        return true;

      }

      else {

        var options;

        if (parsed_code.type === 'price') {
          options = { price: parsed_code.value, extras: { price_manually_set: true } };
        } else if (parsed_code.type === 'weight') {
          options = { quantity: parsed_code.value, merge: false };
        } else if (parsed_code.type === 'discount') {
          options = { discount: parsed_code.value, merge: false };
        } else {
          options = {};
        }

        var self = this;

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

        const { confirmed, payload } = await Gui.showPopup('SaveProduct', popupMaterial);
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
          options.kitchen_note = payload.kitchen_note;
          options.food_serve_as = payload.food_serve_as;
          options.food_doneness = payload.food_doneness;
          options.food_type = payload.food_type;
          options.food_temperature = payload.food_temperature;
          selectedOrder.add_product(product, options);
        }

        return true;

      }

    },

  });

});
