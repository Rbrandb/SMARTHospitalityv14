odoo.define('website_calendar_booking.ReservationDetailsEdit', function(require) {
    'use strict';

    const { getDataURLFromFile } = require('web.utils');
    const PosComponent = require('point_of_sale.PosComponent');
    const Registries = require('point_of_sale.Registries');

    class ReservationDetailsEdit extends PosComponent {
        constructor() {
            super(...arguments);
            this.intFields = ['country_id', 'state_id', 'property_product_pricelist'];
            this.changes = {};
        }
        mounted() {
            this.env.bus.on('save-reservation', this, this.saveChanges);
        }
        willUnmount() {
            this.env.bus.off('save-reservation', this);
        }
        captureChange(event) {
            this.changes[event.target.name] = event.target.value;
        }
        saveChanges() {
            let processedChanges = {};
            for (let [key, value] of Object.entries(this.changes)) {
                if (this.intFields.includes(key)) {
                    processedChanges[key] = parseInt(value) || false;
                } else {
                    processedChanges[key] = value;
                }
            }
             if ((!processedChanges.name) || processedChanges.name === '' ){
                return this.showPopup('ErrorPopup', {
                  title: _('A Customer Name Is Required'),
                });
            }
            else if ((!processedChanges.date_str) || processedChanges.date_str === '' ){
                return this.showPopup('ErrorPopup', {
                  title: _('A Date and Time Is Required'),
                });
            } else if ((!processedChanges.pax) || processedChanges.pax === '' ){
                return this.showPopup('ErrorPopup', {
                  title: _('A PAX Is Required'),
                });
            }
            else if ((!processedChanges.time_slot_event) || processedChanges.time_slot_event === '' ){
                return this.showPopup('ErrorPopup', {
                  title: _('A Time Slot Is Required'),
                });
            }
             else if ((!processedChanges.pos_table_id) || processedChanges.pos_table_id === '' ){
                return this.showPopup('ErrorPopup', {
                  title: _('A Table Is Required'),
                });
            }
            else if ((!processedChanges.booking_email) || processedChanges.booking_email === '' ){
                return this.showPopup('ErrorPopup', {
                  title: _('A Customer Email Is Required'),
                });
            }
            else if (!this.validateEmail(processedChanges.booking_email)){
                return this.showPopup('ErrorPopup', {
                  title: _('Email should be username@site.com e.g username@gmail.com'),
                });
            }
            this.trigger('save-changes', { processedChanges });
        }
        validateEmail(email){
          var mailformat = /^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$/;
          if(email.match(mailformat)){
            return true;
          }
          else{
            return false;
          }
        }

    }
    ReservationDetailsEdit.template = 'ReservationDetailsEdit';

    Registries.Component.add(ReservationDetailsEdit);

    return ReservationDetailsEdit;
});
