odoo.define('website_calendar_booking.models', function (require) {

    var models = require('point_of_sale.models');
    var rpc = require('web.rpc');
//models.load_fields('reservation.event', ['name','booking_email','phone','pax','description','start','stop_time','stop','duration','type','user_id','partner_ids','code','state']);

    models.load_models([{
        model:  'reservation.event',
        label: 'reservation_event',
        fields: ['name','booking_email','phone','pax','pax_person','description','start','date_str','stop_time','stop','duration','type','user_id','partner_ids','code','state','pos_table_id'],
        domain: function(self){ return [['inactive', '=', false],['state','!=','reject']]; },
        loaded: function(self, reservations) {
            var reservations_ids = _.pluck(reservations, 'id');
            self.prepare_reservations_data(reservations_ids);
//            self.sendMail(reservations_ids);
            self.reservations = reservations
        },
    },{
        model:  'restaurant.table',
        fields: ['name', 'seats'],
        loaded: function(self,tables){
            self.tables = tables;
        },
    },{
        model:  'time.slot.event',
        fields: ['name','complete_name','display_name'],
        loaded: function(self,times_slot){
            self.times_slot = times_slot;
        },
    }

    ]);

    var _super_posmodel = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        initialize: function(session,attributes)
        {
            var contact_model = _.find(this.models,function(model)
            {
                return model.model === 'reservation.event';
            });
            contact_model.fields.push('name','booking_email','phone','pax','description','start','stop_time','stop','duration','type','user_id','partner_ids','code','state','pos_table_id');
            return _super_posmodel.initialize.apply(this,arguments);
        },
        load_server_data: function () {
            var self = this;
            var args = arguments[0];
            return _super_posmodel.load_server_data.apply(this, arguments).then(function () {
                var reservations_ids = _.map(self.reservations, function(reservations){return reservations.id;});
                return rpc.query({
                    model: 'reservation.event',
                    method: 'get_whole_data',
                    args: [reservations_ids],
                });

            });
        },
        load_new_reservation: function(id){
            var self = this;
            return new Promise(function (resolve, reject) {
//                var fields = _.find(self.models, function(model){ return model.label === 'reservation_event'; }).fields;
//                var domain = [['id','=', id]];
                self.rpc({
                    model: 'reservation.event',
                    method: 'get_recent_data',
                    args: [id],
                }, {
                    timeout: 3000,
                    shadow: true,
                })
                .then(function (partners) {

                }, function (type, err) { reject(); });
            });
        },
        sendMail: function () {
            var self = this;
                var reservations_ids = _.map(self.reservations, function(reservations){return reservations.id;});
                return rpc.query({
                    model: 'reservation.event',
                    method: 'button_sendMail_action',
                    args: [reservations_ids],
                }).catch(function (data) {
                    $(".sendMail").css("color","red").html("Failed to Sent");
                }).then(function() {
                     $(".sendMail").html("Sent Successfully");
        });

        },

        button_validate_action: function (order) {
            var self = this;
                var reservations_ids = order['id'];
                rpc.query({
                    model: 'reservation.event',
                    method: 'button_validate_action',
                    args: [reservations_ids],
                }).catch(function (data) {
                    $('#'+order['id']).css("color","red").html("Failed to Validate");
                }).then(function(dataas) {
                     $('#'+order['id']+'.state.validate').hide();
                     $('#'+order['id']+'.state.free').show();
                     $('#'+order['id']+'.draft').html("Confirmed");

                });

        },
        OnchangeTable: function (order) {
            var self = this;

                var reservations_ids = event.target.selectedOptions[0].id;
                var table_id = event.target.value;
                rpc.query({
                    model: 'reservation.event',
                    method: 'OnchangeTable',
                    args: [reservations_ids,table_id],
                }).catch(function (data) {
                    $('#'+table_id).css("color","red").html("Table Already selected");

                });

        },
        button_available_action: function (order) {
            var self = this;
                var reservations_ids = order['id'];
                rpc.query({
                    model: 'reservation.event',
                    method: 'button_available_action',
                    args: [reservations_ids],
                }).catch(function (data) {
                    $('#'+order['id']).css("color","red").html("Failed to Free");
                }).then(function(dataas) {
                     $('#'+order['id']+'.state').hide();
                     $('#'+order['id']+'.draft').html("Freed");
                     $('#'+order['id']+'.confirm').html("Freed");

                });

        },
//        get_pos_table_records: function(order){
//            var self = this;
//            var reservations_ids = order['id'];
//            return rpc.query({
//                model: 'reservation.event',
//                method: 'get_pos_table_records',
//                args: [reservations_ids],
//            });
//        },
        prepare_reservations_data: function (data) {
            _.each(data, function (item) {
                for (var property in item) {
                    if (Object.prototype.hasOwnProperty.call(item, property)) {
                        if (item[property] === false) {
                            item[property] = " ";
                        }
                    }
                }
            });
        },
        destroy: function (){
            this.env.pos;
        },
    });
//    return models
});


