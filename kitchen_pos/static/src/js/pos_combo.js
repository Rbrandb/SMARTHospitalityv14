odoo.define('kitchen_pos.BiProductScreenNew', function(require) {
	"use strict";
    const Registries = require('point_of_sale.Registries');
    const ProductScreen = require('pos_combo.BiProductScreen');
    const BiProductScreenNew = (ProductScreen) =>
		class extends ProductScreen {
			constructor() {
				super(...arguments);
			}
			async _clickProduct(event) {
				var self = this;
				const product = event.detail;
				let order = this.env.pos.get_order();
				if(product.to_weight && this.env.pos.config.iface_electronic_scale){
					this.gui.show_screen('scale',{product: product});
				}else{
					if(product.is_pack || product.kitchen_option)
					{
						var required_products = [];
						var optional_products = [];
						var serve_as = [];
						if (event.detail.food_serve_as){
							serve_as.push(event.detail.food_serve_as[1])
							var serve_as_list = self.env.pos.product_serve_as;
							for (var sa = 0 ; sa < serve_as_list.length; sa++) {
								if (!(serve_as.includes(serve_as_list[sa].name))){
									serve_as.push(serve_as_list[sa].name)
								}
							}
						}

						var doneness = []
						if (event.detail.food_doneness){
							doneness.push(event.detail.food_doneness[1])
							var doneness_list = self.env.pos.product_food_doneness
							for (var dn = 0 ; dn < doneness_list.length; dn++) {
								if (!(doneness.includes(doneness_list[dn].name))){
									doneness.push(doneness_list[dn].name)
								}
							}
						}
						var combo_products = self.env.pos.pos_product_pack;
						if(product)
						{
							for (var i = 0; i < combo_products.length; i++) {
								if(combo_products[i]['bi_product_product'][0] == product['id'])
								{
									if(combo_products[i]['is_required'])
									{
										combo_products[i]['product_ids'].forEach(function (prod) {
											var sub_product = self.env.pos.db.get_product_by_id(prod);
											required_products.push(sub_product)
										});
									}
									else{
										combo_products[i]['product_ids'].forEach(function (prod) {
											var sub_product = self.env.pos.db.get_product_by_id(prod);
											optional_products.push(sub_product)
										});
									}
								}
							}
						}
						self.showPopup('SelectComboProductPopupWidget', {'product': product,'required_products':required_products,'optional_products':optional_products , 'update_line' : false, 'serve_as': serve_as, 'doneness': doneness }); 

					}
					else{
						this.env.pos.get_order().add_product(product);
					}
				}
			}

			_setValue(val){
				let self = this;
				let order = this.currentOrder;
				if(this.currentOrder.get_selected_orderline()){
					if(this.currentOrder.get_selected_orderline().product.is_pack){
						if(this.state.numpadMode==='quantity'){
							var orderline = order.get_selected_orderline()
	                    	orderline.set_quantity(val,'keep_price')

						}else{
							super._setValue(val)
						}
					}
					else{
						super._setValue(val)
					}
				}

			}
		};

	Registries.Component.extend(ProductScreen, BiProductScreenNew);

	return ProductScreen;

});