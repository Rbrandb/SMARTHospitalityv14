odoo.define('kitchen_pos.PosDB', function (require) {

  const PosDB = require('point_of_sale.DB');
  const pos_db = PosDB.prototype;

  PosDB.include({
    init: function (options) {
      this._super(options);
      this.food_serve_as = {};
      this.food_doneness = {};
    },

    add_food_serve_as: function (dict) {
      for (var i = 0; i < dict.length; i++) {
        this.food_serve_as[dict[i].id] = dict[i].name;
      }
    },

    add_food_doneness: function (dict) {
      for (var i = 0; i < dict.length; i++) {
        this.food_doneness[dict[i].id] = dict[i].name;
      }
    },

    get_food_serve_as: function (index) {
      return this.food_serve_as[index];
    },

    get_food_doneness: function (index) {
      return this.food_doneness[index];
    }

  });

});