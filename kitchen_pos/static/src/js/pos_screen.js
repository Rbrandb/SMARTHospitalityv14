odoo.define('kitchen_pos.PosScreen', function (require) {
  'use strict';

  const core = require('web.core');
  const _t = core._t;
  const Registries = require('point_of_sale.Registries');
  const ProductScreen = require('point_of_sale.ProductScreen');
  const NumberBuffer = require('point_of_sale.NumberBuffer');
  const models = require('point_of_sale.models');
  const _pos_model = models.PosModel.prototype;
  const pos_models = models.PosModel.prototype.models;
  const rpc = require('web.rpc');
  var utils = require('web.utils');
  var exports = {};
  var round_di = utils.round_decimals;
  models.load_fields('product.product', ['food_type', 'food_temperature', 'food_serve_as', 'food_doneness', 'kitchen_option']);

  pos_models.push({
    model: 'product.serve.as',
    label: 'load_product_serve_as',
    fields: ['name'],
    loaded: function (self, product_serve_as) {
      self.product_serve_as = product_serve_as;
      self.db.add_food_serve_as(product_serve_as);
    }
  },
    {
      model: 'product.food.doneness',
      label: 'load_product_food_doneness',
      fields: ['name'],
      loaded: function (self, product_food_doneness) {
        self.product_food_doneness = product_food_doneness;
        self.db.add_food_doneness(product_food_doneness);
      }
    });

  models.PosModel = models.PosModel.extend({

    initialize: function (attributes) {
      _pos_model.initialize.call(this, attributes);
      this.product_serve_as = [];
      this.product_food_doneness = [];
    },

  });

  var _super_orderline = models.Orderline.prototype;
  var orderline_id = 1;
  models.Orderline = models.Orderline.extend({
    initialize: function(attr,options){
      _super_orderline.initialize.apply(this, arguments);
      this.pos   = options.pos;
      this.order = options.order;
      if (options.json) {
          try {
              this.init_from_JSON(options.json);
          } catch(error) {
              console.error('ERROR: attempting to recover product ID', options.json.product_id,
                  'not available in the point of sale. Correct the product or clean the browser cache.');
          }
          return;
      }
      this.food_serve_as = options.food_serve_as;
      this.food_doneness = options.food_doneness;
    },

    init_from_JSON: function(json) {
      _super_orderline.init_from_JSON.apply(this,arguments);
      if (json.food_serve_as) {
          this.food_serve_as = json.food_serve_as[1];
      }
      if (json.food_doneness) {
          this.food_doneness = json.food_doneness[1];
      }
    },

    export_as_JSON: function() {
      var json = _super_orderline.export_as_JSON.apply(this,arguments);
      json.food_serve_as = this.food_serve_as;
      json.food_doneness = this.food_doneness;
      return json;
    },

    // when we add an new orderline we want to merge it with the last line to see reduce the number of items
    // in the orderline. This returns true if it makes sense to merge the two
    can_be_merged_with: function(orderline){
      var price = parseFloat(round_di(this.price || 0, this.pos.dp['Product Price']).toFixed(this.pos.dp['Product Price']));
      var order_line_price = orderline.get_product().get_price(orderline.order.pricelist, this.get_quantity());
      order_line_price = round_di(orderline.compute_fixed_price(order_line_price), this.pos.currency.decimals);
      if( this.get_product().id !== orderline.get_product().id){    //only orderline of the same product can be merged
          return false;
      }else if(!this.get_unit() || !this.get_unit().is_pos_groupable){
          return false;
      }else if(this.get_discount() > 0){             // we don't merge discounted orderlines
          return false;
      }else if(!utils.float_is_zero(price - order_line_price - orderline.get_price_extra(),
                  this.pos.currency.decimals)){
          return false;
      }else if(this.product.tracking == 'lot' && (this.pos.picking_type.use_create_lots || this.pos.picking_type.use_existing_lots)) {
          return false;
      }else if (this.description !== orderline.description) {
          return false;
      }else if (this.food_doneness && this.food_serve_as !== orderline.food_serve_as && this.food_doneness !== orderline.food_doneness) {
          return false;
      }else if(this.food_serve_as !== orderline.food_serve_as){
        return false;
      }else{
          return true;
      }
    },

    capitalize: function (string) {
      if (string === undefined || string === false || string === null) {
        return '';
      }
      else {
        return string.charAt(0).toUpperCase() + string.slice(1);
      }
    },

    get_food_main_info: function () {
      var food_type = this.capitalize(this.product.food_type);
      var food_temperature = this.capitalize(this.product.food_temperature);
      var response = food_type + ' ' + food_temperature;
      return response;
    },

    get_food_secondary_info: function () {
      var food_serve_as = this.food_serve_as
      var food_doneness = this.food_doneness
      var response = '';
      if (food_serve_as) {
        response += String(food_serve_as);
      }
      if (food_doneness) {
        response += ', ' + String(food_doneness);
      }
      return response;
    },

  });
  models.Order = models.Order.extend({
    add_product: function(product, options){
      if(this._printed){
          this.destroy();
          return this.pos.get_order().add_product(product, options);
      }
      this.assert_editable();
      options = options || {};
      var line = new models.Orderline({}, {pos: this.pos, order: this, product: product});
      this.fix_tax_included_price(line);

      if(options.quantity !== undefined){
          line.set_quantity(options.quantity);
      }

      if (options.price_extra !== undefined){
          line.price_extra = options.price_extra;
          line.set_unit_price(line.product.get_price(this.pricelist, line.get_quantity(), options.price_extra));
          this.fix_tax_included_price(line);
      }

      if(options.price !== undefined){
          line.set_unit_price(options.price);
          this.fix_tax_included_price(line);
      }

      if(options.lst_price !== undefined){
          line.set_lst_price(options.lst_price);
      }

      if(options.discount !== undefined){
          line.set_discount(options.discount);
      }

      if (options.description !== undefined){
          line.description += options.description;
      }

      if(options.extras !== undefined){
          for (var prop in options.extras) {
              line[prop] = options.extras[prop];
          }
      }
      if (options.is_tip) {
          this.is_tipped = true;
          this.tip_amount = options.price;
      }

      if (options.food_serve_as) {
          this.food_serve_as = options.food_serve_as
          line.food_serve_as = options.food_serve_as
      }
      if (options.food_doneness) {
          this.food_doneness = options.food_doneness
          line.food_doneness = options.food_doneness
      }
      var to_merge_orderline;
      for (var i = 0; i < this.orderlines.length; i++) {
          if(this.orderlines.at(i).can_be_merged_with(line) && options.merge !== false){
              to_merge_orderline = this.orderlines.at(i);
          }
      }
      if (to_merge_orderline){
          to_merge_orderline.merge(line);
          this.select_orderline(to_merge_orderline);
      } else {
          this.orderlines.add(line);
          this.select_orderline(this.get_last_orderline());
      }

      if (options.draftPackLotLines) {
          this.selected_orderline.setPackLotLines(options.draftPackLotLines);
      }
      if (this.pos.config.iface_customer_facing_display) {
          this.pos.send_current_order_to_customer_facing_display();
      }
  },
  });
  return ProductScreen;

});