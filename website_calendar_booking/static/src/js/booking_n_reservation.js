/* Copyright (c) 2016-Present Webkul Software Pvt. Ltd. (<https://webkul.com/>) */
/* See LICENSE file for full copyright and licensing details. */
/* @License       : https://store.webkul.com/license.html */

odoo.define('website_calendar_booking.booking_n_reservation', function(require) {
    "use strict";

    var ajax = require('web.ajax');
    var core = require('web.core');
    var _t = core._t;

    var Days = {
        'sun' : 0,
        'mon' : 1,
        'tue' : 2,
        'wed' : 3,
        'thu' : 4,
        'fri' : 5,
        'sat' : 6,
    }

    $(document).ready(function() {
        // Booking day slot selection
//        $('body').on('click','.subbtn',function(evnt){
//
//            if ($('#start_timeslot')[0].value){
//                    console.log("Success");
//                }
//             else{
//                $('.selectslot').css('color',"#ff0e0e");
//                $('.selectslot').msgpopup({
//                    text: 'Select SLot!',
//                    type: 'error', // or success, error, alert and normal
//                    x: false, // or false
//                });
//
//            }
//
//        });

         $('body').on('click','.disable_msg',function(evnt){
            if ($('#start_timeslot')[0].value){
                $('#'+$('#start_timeslot')[0].value).css('background-color',"#ffffff");
            }
            $('#span_select').val('');
            $('#spsrry').show().text('Time Frame is not available | We are sorry but we have no more seats available for this time, please select another time frame or call us'+' '+$('#companyphone').val());
         });
        $('body').on('keyup','#comment',function(evnt){
            if ($('#comment').val().length > 0){
                $("#spocc").show();
            }
            else{
                $("#spocc").hide();
            }
        });
        $('body').on('click','.subbtn',function(evnt){
            if($('#span_select').val() == false){
                $('.errormsg').show().text('Select Time Frame').val();
            }
            else{
                $('.errormsg').hide();
            }
        });
        $('body').on('click','.bk_slot_div',function(evnt){
            $('#spsrry').hide();
            $('.errormsg').hide();
            if ($('#start_timeslot')[0].value){
                $('#'+$('#start_timeslot')[0].value).css('background-color',"#ffffff");
            }
            var $this = $(this);
            $('#start_timeslot').val($this[0].id);
            $('#span_select').val($this[0].id);
            $(this).css('background-color',"#62b683",'color',"#f9ebeb");
//            var browser = JSON.stringify($.browser)
//            $('#browser_info').val(browser);
            var browser = '';
            navigator.sayswho= (function(){
                var N= navigator.appName, ua= navigator.userAgent, tem,
                M= ua.match(/(opera|chrome|safari|firefox|msie|edg)\/?\s*([\d\.]+)/i);
                if(M && (tem= ua.match(/version\/([\.\d]+)/i))!= null) M[2]= tem[1];
                M= M? [M[1], M[2]]:[N, navigator.appVersion, '-?'];
                return M.join(' ');
            })();
            if(navigator.userAgent.match(/SAMSUNG|Samsung|SGH-[I|N|T]|GT-[I|N]|SM-[A|N|P|T|Z]|SHV-E|SCH-[I|J|R|S]|SPH-L/i)) {
                browser = "Samsung"+' (parent names:'+navigator.userAgent+')';
                $('#browser_info').val(browser);
            }
            else if(window.navigator.userAgentData){// for edge
                browser = window.navigator.userAgentData.brands[2]['brand']+' '+window.navigator.userAgentData.brands[2]['version'];
                $('#browser_info').val(browser);
            }
            else{
                $('#browser_info').val(navigator.sayswho);
            }

//            var slot_plans = $this.data('slot_plans');
//            var booking_modal = $('#booking_modal');
//            var bk_loader = $('#bk_n_res_loader');
//            var time_slot_id = parseInt($this.data('time_slot_id'),10);
//            var model_plans = booking_modal.find('.bk_model_plans');
//            var bk_modal_slots = booking_modal.find('.bk_modal_slots');
//            var product_id = parseInt(booking_modal.data('res_id'),10);
//            var bk_sel_date = $('#bk_sel_date');
//            bk_loader.show();
//            ajax.jsonRpc("/booking/reservation/slot/plans", 'call',{
//                'time_slot_id' : time_slot_id,
//                'slot_plans' : slot_plans,
//                'sel_date' : bk_sel_date.val(),
//                'product_id' : product_id,
//            })
//            .then(function (result) {
//                bk_loader.hide();
//                reset_total_price();
//                model_plans.html(result);
//            });
//            bk_modal_slots.find('.bk_slot_div').not($this).each(function(){
//                var $this = $(this);
//                if($this.hasClass('bk_active')){
//                    $this.removeClass('bk_active');
//                }
//            });
//            if(!$this.hasClass('bk_active')){
//                $this.addClass('bk_active');
//            }
        });
function fnBrowserDetect(){

         let userAgent = navigator.userAgent;
         let browserName;

         if(userAgent.match(/chrome|chromium|crios/i)){
             browserName = "chrome";
           }else if(userAgent.match(/firefox|fxios/i)){
             browserName = "firefox";
           }  else if(userAgent.match(/safari/i)){
             browserName = "safari";
           }else if(userAgent.match(/opr\//i)){
             browserName = "opera";
           } else if(userAgent.match(/edg/i)){
             browserName = "edge";
           }else{
             browserName="No browser detection";
           }

          document.querySelector("h1").innerText="You are using "+ browserName +" browser";
  }

    });
});
