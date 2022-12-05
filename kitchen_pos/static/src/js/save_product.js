odoo.define('kitchen_pos.SaveProduct', function (require) {
  'use strict';

  const { useState, useRef, useContext } = owl.hooks;
  const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
  const Registries = require('point_of_sale.Registries');

  class SaveProduct extends AbstractAwaitablePopup {
    constructor() {
      super(...arguments);
      this.state = useState({
        kitchen_note: this.props.startingValue,
        food_serve_as: null,
        food_doneness: null,
        food_type: null,
        food_temperature: null,
        kitchen_option: null
      });
    }

    getPayload() {
      return this.state;
    }

  }

  SaveProduct.template = 'KitchenProductPopUp';
  SaveProduct.defaultProps = {
    confirmText: 'OK',
    cancelText: 'Cancel'
  };

  Registries.Component.add(SaveProduct);

  return SaveProduct;
});
