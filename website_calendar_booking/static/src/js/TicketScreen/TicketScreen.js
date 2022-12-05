odoo.define('website_calendar_booking.ReservationTicketScreen', function (require) {
    'use strict';

    const Registries = require('point_of_sale.Registries');
    const IndependentToOrderScreen = require('point_of_sale.IndependentToOrderScreen');
    const { useListener } = require('web.custom_hooks');
    const { posbus } = require('point_of_sale.utils');

    class ReservationTicketScreen extends IndependentToOrderScreen {
        constructor() {
            super(...arguments);
//            useListener('close-screen', this.close);
            useListener('close-screen', this.close);
            useListener('loading-expan_collapse-callback', this.expan_collapse);
            useListener('filter-selected', this._onFilterSelected);
            useListener('click-save', () => this.env.bus.trigger('save-reservation'));
            useListener('search', this._onSearch);
            useListener('save-changes', this.saveChanges);
//            useListener('filter', this._onfilter);
            this.searchDetails = {};
//            this.filterDetails = {};
            this.filter = null;
//            this.detailIsShown= false;
            this.state = {
                query: null,
                selectedClient: this.props.client,
                detailIsShown: false,
                isEditMode: false,
                editModeProps: {
                    partner: {
                        country_id: this.env.pos.company.country_id,
                        state_id: this.env.pos.company.state_id,
                    }
                },
            };
            this._initializeSearchFieldConstants();
        }
        mounted() {
            posbus.on('ticket-button-clicked', this, this.close);
            this.env.pos.get('orders').on('add remove change', () => this.render(), this);
            this.env.pos.on('change:selectedOrder', () => this.render(), this);
        }
        willUnmount() {
            posbus.off('ticket-button-clicked', this);
            this.env.pos.get('orders').off('add remove change', null, this);
            this.env.pos.off('change:selectedOrder', null, this);
        }
        close(){
            window.location.reload();
        }
        back() {
            if(this.state.detailIsShown) {
                this.state.detailIsShown = false;
                this.render();
            } else {
//                this.props.resolve({ confirmed: false, payload: false });
                this.trigger('close-screen');
            }
        }
        async saveChanges(event) {
            try {
                let partnerId = await this.rpc({
                    model: 'reservation.event',
                    method: 'create_from_ui',
                    args: [event.detail.processedChanges],
                });
                await this.env.pos.load_server_data(partnerId);
                this.state.detailIsShown = false;
                this.render();
            } catch (error) {
                if (error.message.code < 0) {
                    await this.showPopup('OfflineErrorPopup', {
                        title: this.env._t('Offline'),
                        body: this.env._t('Unable to save changes.'),
                    });
                } else {
                    throw error;
                }
            }
        }
         activateEditMode(event) {
           const { isNewClient } = event.detail;
            this.state.isEditMode = true;
            this.state.detailIsShown = true;
            this.state.isNewClient = isNewClient;
            if (!isNewClient) {
                this.state.editModeProps = {
                    partner: this.state.selectedClient,
                };
            }
            this.render();

         }
        expan_collapse(event){
            var content = event.detail.currentTarget.getElementsByClassName('content');
            if(event.detail.target.className == "col start wide title" ||  event.detail.target.className == "header-status"){
                for (var i = 0; i < content.length; i++) {

                    if (content[i].style.display === "block") {
                      content[i].style.display = "none";
                    } else {
                      content[i].style.display = "block";
                    }
                }
                event.detail.currentTarget.getElementsByClassName('header-text')[0].classList.toggle('active');
            }
////            $(".pointer .header").click(function() {
//              let parent = $(this).closest('.pointer');
//              //getting the next element
//              let $content = parent.find('.content');
//              //open up the content needed - toggle the slide- if visible, slide up, if not slidedown.
//              $content.slideToggle(500, function() {
//                //execute this after slideToggle is done
//                //change text of header based on visibility of content div
//                parent.find('.header-text').toggleClass('active');
//              });

//            });
        }
        _onFilterSelected(event) {
            this.filter = event.detail.filter;
//            for making drop down search
            if(this.filter == "Confirm" || this.filter == "confirm"){
                const searchDetails = {'fieldValue':'State','searchTerm':event.detail.filter};
                Object.assign(this.searchDetails, searchDetails);
            }
            else if(this.filter == "Available" || this.filter == "available"){
                const searchDetails = {'fieldValue':'State','searchTerm':event.detail.filter};
                Object.assign(this.searchDetails, searchDetails);
            }
            else if(this.filter == "New" || this.filter == "new"){
                const searchDetails = {'fieldValue':'State','searchTerm':'draft'};
                Object.assign(this.searchDetails, searchDetails);
            }
            this.render();
        }
        _onSearch(event) {
            const searchDetails = event.detail;
            Object.assign(this.searchDetails, searchDetails);
            this.render();
        }
//        _onfilter(event) {
//            const searchDetails = event.detail;
//            Object.assign(this.searchDetails, searchDetails);
//            this.render();
//        }
        /**
         * Override to conditionally show the new ticket button.
         */
        get showNewTicketButton() {
            return true;
        }
        get orderList() {
            return this.env.pos.reservations;
        }
        OnchangeTable(event,order) {
//            alert(event);
//            this.changes[event.target.name] = event.target.value;
            this.env.pos.OnchangeTable(event.target);
        }
        get getStates(){
            var arr = ['draft','confirm','available','reject'];
            return arr;
        }
        get filteredOrderList() {
            const filterCheck = (order) => {
                if (this.filter && this.filter == "State") {
                    const screen =  {'name':"ReservationTicketScreen"};//order.get_screen_data();
                    return this.filter === this.constants.screenToStatusMap[screen.name];
                }
                return true;
            };
//        for search tag
            const { fieldValue, searchTerm } = this.searchDetails;
            const fieldAccessor = this._searchFields[fieldValue];
            const searchCheck = (order) => {
                if (!fieldAccessor) return true;
                const fieldValue = fieldAccessor(order);
                if (fieldValue === null) return true;
                if (!searchTerm) return true;
                return fieldValue && fieldValue.toString().toLowerCase().includes(searchTerm.toLowerCase());
            };
            const predicate = (order) => {
                return filterCheck(order) && searchCheck(order);
            };//search tag works ends


            return this.orderList.filter(predicate);
        }
        selectOrder(order) {
            this._setOrder(order);
            if (order === this.env.pos.get_order()) {
                this.close();
            }
        }
        _setOrder(order) {
            this.env.pos.set_order(order);
        }
        createNewOrder() {
            this.env.pos.add_new_order();
        }
        sendMail() {
            this.env.pos.sendMail();
        }
        button_validate_action(order) {
            this.env.pos.button_validate_action(order);
        }
        button_available_action(order) {
            this.env.pos.button_available_action(order);
        }
        async deleteOrder(order) {
            if (order) {
                order.destroy({ reason: 'abandon' });
            }
            posbus.trigger('order-deleted');
        }
        getDate(order) {
            return moment(order.creation_date).format('YYYY-MM-DD hh:mm A');
        }
        getTotal(order) {
            return this.env.pos.format_currency(order.get_total_with_tax());
        }
        getCustomer(order) {
            return order.get_client_name();
        }
        getCardholderName(order) {
            return order.get_cardholder_name();
        }
        getEmployee(order) {
            return order.employee.name;
        }
        getStatus(order) {
            const screen = order.get_screen_data();
            return this.constants.screenToStatusMap[screen.name];
        }
        /**
         * Hide the delete button if one of the payments is a 'done' electronic payment.
         */
//        hideDeleteButton(order) {
//            return order
//                .get_paymentlines()
//                .some((payment) => payment.is_electronic() && payment.get_payment_status() === 'done');
//        }
        showCardholderName() {
            return this.env.pos.payment_methods.some(method => method.use_payment_terminal);
        }
        get searchBarConfig() {
            return {
                searchFields: this.constants.searchFieldNames,
                filter: { show: true, options: this.filterOptions },
            };
        }
        get filterOptions() {
            return ['Name',  'Date','Confirm','Available','New'];
        }
        /**
         * An object with keys containing the search field names which map to functions.
         * The mapped functions will be used to generate representative string for the order
         * to match the search term when searching.
         * E.g. Given 2 orders, search those with `Receipt Number` containing `1111`.
         * ```
         * orders = [{
         *    name: '000-1111-222'
         *    total: 10,
         *   }, {
         *    name: '444-5555-666'
         *    total: 15,
         * }]
         * ```
         * `Receipt Number` search field maps to the `name` of the order. So, the orders will be
         * represented by their name, and the search will result to:
         * ```
         * result = [{
         *    name: '000-1111-222',
         *    total: 10,
         * }]
         * ```
         * @returns Record<string, (models.Order) => string>
         */
        get _searchFields() {
            var fields = {
                'Name': (order) => order.name,
                'State': (order) => order.state,
                Date: (order) => moment(order.start).format('YYYY-MM-DD hh:mm A'),
//                Customer: (order) => order.get_client_name(),
            };

            return fields;
        }
        /**
         * Maps the order screen params to order status.
         */
        get _screenToStatusMap() {
            return {
                ProductScreen: 'Ongoing',
                PaymentScreen: 'Payment',
                ReceiptScreen: 'Receipt',
            };
        }
        _initializeSearchFieldConstants() {
            this.constants = {};
            Object.assign(this.constants, {
                searchFieldNames: Object.keys(this._searchFields),
                screenToStatusMap: this._screenToStatusMap,
            });
        }
    }
    ReservationTicketScreen.template = 'ReservationTicketScreen';

    Registries.Component.add(ReservationTicketScreen);

    return ReservationTicketScreen;
});
