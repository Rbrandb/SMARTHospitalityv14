odoo.define('robert_kitchen.SelectComboProductPopupWidget', function(require){
	'use strict';

	const Popup = require('point_of_sale.ConfirmPopup');
	const Registries = require('point_of_sale.Registries');
	const PosComponent = require('point_of_sale.PosComponent');

	class SelectComboProductPopupWidget extends Popup {

		constructor() {
				super(...arguments);
			}

		go_back_screen() {
			this.showScreen('ProductScreen');
			this.trigger('close-popup');
		}

		get req_product() {
			let req_product = [];
			$.each(this.props.required_products, function( i, prd ){
				prd['product_image_url'] = `/web/image?model=product.product&field=image_128&id=${prd.id}&write_date=${prd.write_date}&unique=1`;
				req_product.push(prd)
			});
			return req_product;
		}

		get optional_product(){
			let optional_product = [];
			$.each(this.props.optional_products, function( i, prd ){
				prd['product_image_url'] = `/web/image?model=product.product&field=image_128&id=${prd.id}&write_date=${prd.write_date}&unique=1`;
				optional_product.push(prd)
			});
			return optional_product;
		}

		mounted(){
			var self = this;
			var order = self.env.pos.get_order();
			if(order){
				var orderlines = order.get_orderlines();
				this.product = self.props.product;
				this.update_line = self.props.update_line;
				this.required_products = self.props.required_products;
				this.optional_products = self.props.optional_products;
				this.combo_products = self.env.pos.pos_product_pack;
			}

			$('.optional-product').each(function(){
				$('.raghav').removeClass('raghav');
				$(this).on('click',function () {
					if ( $(this).hasClass('raghav') )
					{
						$(this).removeClass('raghav');
					}
					else{
						$(this).addClass('raghav');
					}
				});
			});
			$('.required-product').each(function(){
				$('.raghav').removeClass('raghav');
				$(this).on('click',function () {
					if ( $(this).hasClass('raghav') )
					{
						$(this).removeClass('raghav');
					}
					else{
						$(this).addClass('raghav');
					}
				});
			});


		}

		renderElement() {
			var self = this;
			var order = self.env.pos.get_order();
			if(order){
				var orderlines = order.get_orderlines();
				var final_products = this.required_products;

				$('.remove-product').click(function(ev){
					ev.stopPropagation();
					ev.preventDefault();
					var prod_id = parseInt(this.dataset.productId);
					$(this).closest(".optional-product").hide();
					for (var i = 0; i < self.optional_products.length; i++)
					{
						if(self.optional_products[i]['id'] == prod_id)
						{
							self.optional_products.splice(i, 1);
						}
					}
				});


			}
		}
		add_confirm(ev){
			var final_products = [];
			var required_count = 0
			var required_products = [];
			var order = this.env.pos.get_order();
			var orderlines = order.get_orderlines();
			ev.stopPropagation();
			ev.preventDefault();
			var self = this
			$('.raghav').each(function(){
				var prod_id = parseInt(this.dataset.productId);
				for (var i = 0; i < self.optional_products.length; i++)
				{
					if(self.optional_products[i]['id'] == prod_id)
					{
						final_products.push(self.optional_products[i]);
					}
				}

			});
			$('.raghav').each(function(){
				var prod_id = parseInt(this.dataset.productId);
				for (var i = 0; i < self.required_products.length; i++)
				{
					if(self.required_products[i]['id'] == prod_id)
					{
						final_products.push(self.required_products[i]);
						required_count = required_count + 1
						required_products.push(self.required_products[i])
					}
				}

			});
			if (self.required_products.length > 0 && required_count == 0) {
				alert("Please select atleast one required combo product")
				return false
			}
			var add = [];
			var new_prod = [self.props.product.id,final_products];
			if(self.env.pos.get('final_products'))
			{
				add.push(self.env.pos.get('final_products'))
				add.push(new_prod)
				self.env.pos.set({
					'final_products': add,
					'required_products' : required_products,
				});
			}
			else{
				add.push(new_prod)
				self.env.pos.set({
					'final_products': add,
					'required_products' : required_products,
				});
			}
			var selected_line = null;
			if(self.update_line){
				orderlines.forEach(function (line) {
				if(line.selected == true)
				{
					if(line.product.id == self.product.id)
					{
						selected_line = line;
						}
					}
				});
			if(selected_line != null)
				{
					selected_line.set_combo_products(final_products)
				}
				else{
                    // if (self.el.querySelector('#serves_as_selection').value){
                    //     self.product.food_serve_as[1] = self.el.querySelector('#serves_as_selection').value
                    // }
                    // if (self.el.querySelector('#doneness_selection').value){
                    //     self.product.food_doneness[1] = self.el.querySelector('#doneness_selection').value
                    // }
				    order.add_product(self.product,{food_serve_as :self.el.querySelector('#serves_as_selection').value ,food_doneness : self.el.querySelector('#doneness_selection').value});
				}
			}else{
                // if (self.el.querySelector('#serves_as_selection').value){
                //     self.product.food_serve_as[1] = self.el.querySelector('#serves_as_selection').value
                // }
                // if (self.el.querySelector('#doneness_selection').value){
                //     self.product.food_doneness[1] = self.el.querySelector('#doneness_selection').value
                // }
					order.add_product(self.product,{food_serve_as :self.el.querySelector('#serves_as_selection').value ,food_doneness : self.el.querySelector('#doneness_selection').value});
			}
			self.trigger('close-popup');
		}
	}

	SelectComboProductPopupWidget.template = 'SelectComboProductPopupWidget';

	Registries.Component.add(SelectComboProductPopupWidget);

	return SelectComboProductPopupWidget;

});