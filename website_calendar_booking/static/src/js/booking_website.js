odoo.define('booking.website', function (require) {
'use strict';

var ajax = require('web.ajax');
var core = require('web.core');
var qweb = core.qweb;

ajax.loadXML('/website_calendar_booking/static/src/xml/website_calendar_booking_modal1.xml', qweb);

$(document).ready(function() {

        // page is now ready, initialize the calendar...
        var slotDuration = convert_float_time( $("#calendar_slot_duration").val() );
        console.log(slotDuration);
        var minTime = $("#calendar_min_time").val();
        var maxTime = $("#calendar_max_time").val();
        var user = $("#calendar_user").val();
        var eating_types = $('#eating_type').val();
        var calendarID = $("#calendar_id").val();
        var fullCalObj = $('#booking_calendar').fullCalendar({
            // put your options and callbacks here
             header: {
                  left: "prev,next today",
                  center: "title",
                  right: "month"
//                  right: "month,agendaWeek,agendaDay"
                },
//            minTime: minTime,
//            maxTime: maxTime,
//            slotDuration: slotDuration + ':00',
//            slotLabelInterval: slotDuration + ':00',
//            slotLabelFormat: 'hh:mma',
            defaultView: 'month',
//            timezone: 'local',
//            allDaySlot: false,
            themeSystem: 'bootstrap3',
            eventSources: [
                {
                url: '/book/calendar/timeframe/' + calendarID,
                rendering: 'background',
                className: "booking_calendar_book_time"
                },
                {
                url: '/book/calendar/events/' + user,
                rendering: 'background',
                backgroundColor: '#ff0000'
                },
//                {
//                url: '/book/calendar/timeslot/'+eating_types,
//                rendering: 'background',
//                },


            ],
            eventRender: function (event, element) {
//			    if (event.className == 'wcb_back_event') {
				    element.append(event.title);
//				}
            },
//            dayRender: function(date, cell) {
////              cell.append('<div style="text-align:center; background-color:blue; color:#fff;padding:2px 0;margin-top:20px;">Add Your Text!</div>');
//              cell.append('<div style="text-align:center; color:#fff;padding:2px 0;margin-top:20px;"></div>');
//            },
//            eventAfterAllRender: function(view) {
//                var dayEvents = $('#booking_calendar').fullCalendar('clientEvents', function(event) {
//                  if (event.end) {
//                    var dates = getDates(event.start, event.end);
//                    $.each(dates, function(index, value) {
//                      var td = $('td.fc-day[data-date="' + value + '"]');
//                      td.append('<div style="text-align:center; background-color:red; color:#fff;padding:2px 0;margin-top:20px;">Booked</div>')
//                      td.find('div:first').remove();
//                    });
//                  } else {
//                    var td = $('td.fc-day[data-date="' + event.start.format('YYYY-MM-DD') + '"]');
//                    td.append('<div style="text-align:center; background-color:red; color:#fff;padding:2px 0;margin-top:20px;">Booked</div>')
//                    td.find('div:first').remove();
//                  }
//                });
//              },
//            eventAfterAllRender: function (view) {
//                element.append(event.title);
//            },
           dayClick: function(date, jsEvent, view) {

               var timestr = date.toString().split(" ")[4];
               var allEvents = [];
               allEvents = $('#booking_calendar').fullCalendar('clientEvents');
               var event = $.grep(allEvents, function (v) {
                    if(+v.start === +date){
                        return +v.start === +date;
                    }
                    else{
//                   return +v.start._i === +date;
                        return v.start._i.split(" ")[0]+' '+v.start._i.split(" ")[1].split('+')[0] === (new Date(date)).toISOString().slice(0, 10)+' '+date.toString().split(" ")[4];
                    }
               });
//               if (event.length == 0) {

                   this.template = 'website_calendar_booking.calendar_booking_modal';
    		       var self = this;
    		       self.$modal = $( qweb.render(this.template, {}) );
    		       $('body').append(self.$modal);
                   $('#oe_website_calendar_modal').modal('show');
                   var ddate = date.toString().split(' ')
                   $('#date_span').val(ddate[0]+' '+ddate[1]+' '+ddate[2]+' '+ddate[3]);
                   var month_date = (new Date(ddate[2]+" "+ddate[1]+" "+ddate[3])).getMonth()+1;
                   month_date = getDateFormat(month_date);
               var date_check = date.year()+'-'+date.month()+'-'+date.date();
               var dates_today = new Date();
               var date_new = dates_today.getFullYear()+'-'+dates_today.getMonth()+'-'+dates_today.getDate();
               var date_new_2 = dates_today.getFullYear()+'/'+getDateFormat(dates_today.getMonth()+1)+'/'+dates_today.getDate();
               var mydate = new Date(date_check.split('-')[0], date_check.split('-')[1], date_check.split('-')[2]);
               var mydatetoday = new Date(date_new.split('-')[0], date_new.split('-')[1], date_new.split('-')[2]);
               var whole_date = ddate[3]+'/'+month_date+'/'+ddate[2];
                   $('#booking_form_start').val(date);
                   $('#booking_form_calendar_id').val(calendarID);
//                   var time_slot = $('#time_slot').val();
//                   time_slot=time_slot.replaceAll("},{","\"},{").replace("}]","\"}]");
//                   var times=JSON.parse(time_slot);
//                  timeslot full
                   var time_slot_event_full = $('#time_slot_event_full').val();
                   time_slot_event_full.replaceAll("},{","\"},{").replace("}]",",\"}]");
                   var parsed_time_slot_full_event = JSON.parse(time_slot_event_full);
//                   time slot
                   var time_slot_event = $('#time_slot_event').val();
                   time_slot_event.replaceAll("},{","\"},{").replace("}]",",\"}]");
                   var parsed_time_slot_event = JSON.parse(time_slot_event);
//                   time slot date
                   var time_frame_date = $('#book_calendar_time_frame_date').val();
                   time_frame_date.replaceAll("},{","\"},{").replace("}]",",\"}]");
                   var parsed_time_frame_date = JSON.parse(time_frame_date);
//                   table
                   var table_slots = $('#table_slot').val();
                   table_slots.replaceAll("},{","\"},{").replace("}]",",\"}]");
                   var parsed_table = JSON.parse(table_slots);
//                   times.forEach(item => {
//                        item.id=parseInt(item.id);
//                    });
//                    console.log(times);
                    var count = 0;
                    var arr =[];
                    var arrcount = 0 ;
                    $('#spsrry2').hide();
                    $('.bk_slot_div1').find('span').remove();
                    const bk_class = $('.bk_slot_div1');
                    bk_class.find('br').remove();
                    bk_class.html(bk_class.html().replace(/&nbsp;/g,''));

                    var spanclass = '<span class="bk_slot_div" style="padding: 6px 11px;background: #FFFFFF;font-size: 14px;color: #555555;text-align: center;border: 1px solid #979797;border-radius: 4px;cursor: pointer" t-att-data-time_slot_id="1" t-att-data-slot_plans="1">';
                    for(var t=0;t<parsed_time_slot_event.length;t++){
                        var dayss = parsed_time_slot_event[t]['days'].split(',');
//                        for(var i=0; i< times.length; i++) {
//                            if(times[i]['time'] == parsed_time_slot_event[t]['time']){
//                                if(times[i]['date_time'].split(' ')[0] != whole_date){
                        for(var dd=0;dd<dayss.length;dd++){
                            if(ddate[0] == dayss[dd]){
//                                 bk_class.append('<span>'+times[i]['table']+' <span class="bk_slot_div" style="padding: 6px 11px;background: #FFFFFF;font-size: 14px;color: #555555;text-align: center;border: 1px solid #979797;border-radius: 4px;cursor: pointer" id="'+times[i]['id']+'" t-att-data-slot_plans="'+times[i]['time']+'">'+times[i]['time']+'</span></span>&nbsp;&nbsp;');
//                                 bk_class.append('<span><span class="bk_slot_div" style="padding: 6px 11px;background: #FFFFFF;font-size: 14px;color: #555555;text-align: center;border: 1px solid #979797;border-radius: 4px;cursor: pointer" id="'+parsed_time_slot_event[t]['id']+'" t-att-data-slot_plans="'+parsed_time_slot_event[t]['time']+'">'+parsed_time_slot_event[t]['time']+'</span></span>&nbsp;&nbsp;');
                                 arr.push({'id':parsed_time_slot_event[t]['id'],'Time':parsed_time_slot_event[t]['time'],'status':'green','mark_invisible':parsed_time_slot_event[t]['mark_invisible']});
                                 arrcount++;
                                 count = count+1;
                                     if(count == 7){
                                        count = 0;
//                                        bk_class.append('<br></br>');
                                     }
                             }
                          }
//                                }
//                                else if(parsed_time_slot_event[t]['slots_left'] <= parsed_time_slot_event[t]['slots']){
//                                     bk_class.append('<span>'+times[i]['table']+' <span class="bk_slot_div" style="padding: 6px 11px;background: #FFFFFF;font-size: 14px;color: #555555;text-align: center;border: 1px solid #979797;border-radius: 4px;cursor: pointer" id="'+times[i]['id']+'" t-att-data-slot_plans="'+times[i]['time']+'">'+times[i]['time']+'</span>Slots Left('+parsed_time_slot_event[t]['slots_left']+')</span>&nbsp;&nbsp;');
//                                     count = count+1;
//                                     if(count == 3){
//                                        count = 0;
//                                        bk_class.append('<br></br>');
//                                     }
//                                }
//                             }
//                        }
                    }
//                    if(parsed_time_slot_event.length == 0){
                    if(arrcount == 0){
                        $("input").prop("disabled", true );
                        $("textarea").prop("disabled", true );
                        $("select").prop("disabled", true );
//                        $(".slots_available_1").show();
//                        $("#spocc").hide();
                        $('#spsrry').show().text('Time Frame is not available | We are sorry but we have no more seats available for this time, please select another time frame or call us'+' '+$('#companyphone').val());
                        for(var t=0;t<parsed_time_slot_full_event.length;t++){
                            var dayss = parsed_time_slot_full_event[t]['days'].split(',');
                            for(var dd=0;dd<dayss.length;dd++){
                                for(var dd=0;dd<dayss.length;dd++){
                                    if(ddate[0] == dayss[dd]){
//                                        bk_class.append('<span><span  class="disabled disable_msg" style="padding: 6px 11px;background: #e9ecef;font-size: 14px;color: #555555;text-align: center;border: 1px solid #979797;border-radius: 4px;cursor: pointer" id="'+parsed_time_slot_full_event[t]['id']+'" t-att-data-slot_plans="'+parsed_time_slot_full_event[t]['time']+'">'+parsed_time_slot_full_event[t]['time']+'</span></span>&nbsp;&nbsp;');
                                         arr.push({'id':parsed_time_slot_full_event[t]['id'],'Time':parsed_time_slot_full_event[t]['time'],'status':'grey','mark_invisible':parsed_time_slot_full_event[t]['mark_invisible']});
                                         count = count+1;
                                         if(count == 7){
                                            count = 0;
//                                            bk_class.append('<br></br>');
                                         }
                                    }
                                }
                            }

                        }
                    }
                    else{
                        $("input").prop("enable", true );
                        $("textarea").prop("enable", true );
                        $("select").prop("enable", true );
                        $("input").prop("disabled", false );
                        $("textarea").prop("disabled", false );
                        $("select").prop("disabled", false );
//                        $(".slots_available_1").hide();
                         $('#spsrry').hide();
//                         $("#spocc").show();
                        for(var t=0;t<parsed_time_slot_full_event.length;t++){
                            var dayss = parsed_time_slot_full_event[t]['days'].split(',');
                            for(var dd=0;dd<dayss.length;dd++){
                                for(var dd=0;dd<dayss.length;dd++){
                                    if(ddate[0] == dayss[dd]){
//                                        bk_class.append('<span><span  class="disabled disable_msg" style="padding: 6px 11px;background: #e9ecef;font-size: 14px;color: #555555;text-align: center;border: 1px solid #979797;border-radius: 4px;cursor: pointer" id="'+parsed_time_slot_full_event[t]['id']+'" t-att-data-slot_plans="'+parsed_time_slot_full_event[t]['time']+'">'+parsed_time_slot_full_event[t]['time']+'</span></span>&nbsp;&nbsp;');
                                         arr.push({'id':parsed_time_slot_full_event[t]['id'],'Time':parsed_time_slot_full_event[t]['time'],'status':'grey','mark_invisible':parsed_time_slot_full_event[t]['mark_invisible']});
                                         count = count+1;
                                         if(count == 7){
                                            count = 0;
//                                            bk_class.append('<br></br>');
                                         }
                                    }
                                }
                            }

                        }
                    }
                    arr = arr.sort(function(a,b){
                        return new Date('1970/01/01 ' + a.Time) - new Date('1970/01/01 ' + b.Time);
                    });
//                    var n = sort_array(arr);
                    var br_count = 0;
                    var buffer = convert_float_time(parseFloat($('#buffer').val()));
                    var buffer_plus = ''
                    var buffer_previous_time = ''
                    var date_new_buffer_2 = '';
                    var dates_today_24 = moment(dates_today).format("YYYY-MM-DD HH:mm");
                    dates_today_24 = dates_today_24.split(' ');
                    var flag = 0;
                    var seats_future = '';
                    for(var indi=0;indi<arr.length;indi++){
                        flag = 0;
//                        if(br_count == 6){
//                            bk_class.append('<br></br>');
//                            br_count = 0;
//                        }
                        if(arr[indi].status == 'green'){
                            if(Date.parse(whole_date+' '+arr[indi]['Time']) >= Date.parse(date_new_2+' '+dates_today_24[1])){
                                if(Date.parse(whole_date+' '+arr[indi]['Time']) == Date.parse(date_new_2+' '+dates_today_24[1])){
                                    if(arr[indi]['mark_invisible'] == "true"){
                                        buffer_previous_time = whole_date+' '+arr[indi]['Time'];
                                        buffer_plus = moment(whole_date+' '+arr[indi]['Time']).add(parseInt(buffer.split(':')[1]), 'm').toDate();
                                        date_new_buffer_2 = buffer_plus.getFullYear()+'/'+getDateFormat(buffer_plus.getMonth()+1)+'/'+buffer_plus.getDate()+' '+buffer_plus.getHours()+':'+buffer_plus.toLocaleTimeString().split(':')[1]+':'+buffer_plus.toLocaleTimeString().split(':')[2].split(' ')[0];
//                                        continue;
                                    }
                                    else{
//                                    bk_class.append('<span><span class="bk_slot_div clickable_time" id="'+arr[indi]['id']+'" t-att-data-slot_plans="'+arr[indi]['Time']+'">'+arr[indi]['Time']+'</span></span>&nbsp;&nbsp;');
                                        bk_class.append('<span><span  class="disabled disable_msg notclickable" id="'+arr[indi]['id']+'" t-att-data-slot_plans="'+arr[indi]['Time']+'">'+arr[indi]['Time']+'</span></span>&nbsp;&nbsp;');
                                        buffer_plus = moment(whole_date+' '+arr[indi]['Time']).add(parseInt(buffer.split(':')[1]), 'm').toDate();
                                        date_new_buffer_2 = buffer_plus.getFullYear()+'/'+getDateFormat(buffer_plus.getMonth()+1)+'/'+buffer_plus.getDate()+' '+buffer_plus.getHours()+':'+buffer_plus.toLocaleTimeString().split(':')[1]+':'+buffer_plus.toLocaleTimeString().split(':')[2].split(' ')[0];
                                        buffer_previous_time = whole_date+' '+arr[indi]['Time'];
                                        br_count++;
                                    }
                                }
                                else if(Date.parse(whole_date+' '+arr[indi]['Time']) > Date.parse(date_new_2+' '+dates_today_24[1])){
                                    if (date_new_buffer_2 == ''){
                                        if(arr[indi]['mark_invisible'] == "true"){

                                        }
                                        else{
                                            if (parsed_time_frame_date.length > 0){
                                                for(var daywise=0;daywise<parsed_time_frame_date.length;daywise++){
//                                                    if(parseInt(parsed_time_frame_date[daywise]['seats']) <= 0){
//                                                        seats_future = 'Error'
//                                                    }
                                                    if(parsed_time_frame_date[daywise]['date'] == moment(whole_date).format("YYYY-MM-DD") && parsed_time_frame_date[daywise]['time'] ==  arr[indi]['Time']){
                                                         if(parsed_time_frame_date[daywise]['slots_left'] <= 0 && parsed_time_frame_date[daywise]['time'] ==  arr[indi]['Time']){
                                                            bk_class.append('<span><span  class="disabled disable_msg notclickable" id="'+arr[indi]['id']+'" t-att-data-slot_plans="'+arr[indi]['Time']+'">'+arr[indi]['Time']+'</span></span>&nbsp;&nbsp;');
                                                            flag = 1;
                                                        }
                                                        else{
                                                            flag = 1;
                                                            bk_class.append('<span><span class="bk_slot_div clickable_time" id="'+arr[indi]['id']+'" t-att-data-slot_plans="'+arr[indi]['Time']+'">'+arr[indi]['Time']+'</span></span>&nbsp;&nbsp;');
                                                        }
                                                        if(parseInt(parsed_time_frame_date[daywise]['seats']) <= 0){
                                                            seats_future = 'Error'
                                                        }
                                                    }
                                                }
                                                if(flag == 0){
                                                    bk_class.append('<span><span class="bk_slot_div clickable_time" id="'+arr[indi]['id']+'" t-att-data-slot_plans="'+arr[indi]['Time']+'">'+arr[indi]['Time']+'</span></span>&nbsp;&nbsp;');
                                                }
                                            }
                                            else{
                                                bk_class.append('<span><span class="bk_slot_div clickable_time" id="'+arr[indi]['id']+'" t-att-data-slot_plans="'+arr[indi]['Time']+'">'+arr[indi]['Time']+'</span></span>&nbsp;&nbsp;');
                                            }
                                                br_count++;
                                        }
                                    }
                                    else if(Date.parse(whole_date+' '+arr[indi]['Time']) <= Date.parse(date_new_buffer_2)){
                                         if(arr[indi]['mark_invisible'] == "true"){

                                        }
                                        else{
                                            bk_class.append('<span><span  class="disabled disable_msg notclickable" id="'+arr[indi]['id']+'" t-att-data-slot_plans="'+arr[indi]['Time']+'">'+arr[indi]['Time']+'</span></span>&nbsp;&nbsp;');
                                            br_count++;
                                        }
                                    }
                                    else if(Date.parse(whole_date+' '+arr[indi]['Time']) > Date.parse(date_new_buffer_2)){
                                         if(arr[indi]['mark_invisible'] == "true"){

                                        }
                                        else{
                                            bk_class.append('<span><span class="bk_slot_div clickable_time" id="'+arr[indi]['id']+'" t-att-data-slot_plans="'+arr[indi]['Time']+'">'+arr[indi]['Time']+'</span></span>&nbsp;&nbsp;');
                                            br_count++;
                                        }
                                    }
                                }
//                                if(Date.parse(whole_date+' '+arr[indi]['Time']) > Date.parse(buffer_previous_time) && Date.parse(whole_date+' '+arr[indi]['Time']) < Date.parse(date_new_buffer_2)) {
//                                    bk_class.append('<span><span  class="disabled disable_msg notclickable" id="'+arr[indi]['id']+'" t-att-data-slot_plans="'+arr[indi]['Time']+'">'+arr[indi]['Time']+'</span></span>&nbsp;&nbsp;');
//                                }
//                                else if(Date.parse(whole_date+' '+arr[indi]['Time']) > Date.parse(date_new_buffer_2)){
//                                    bk_class.append('<span><span class="bk_slot_div clickable_time" id="'+arr[indi]['id']+'" t-att-data-slot_plans="'+arr[indi]['Time']+'">'+arr[indi]['Time']+'</span></span>&nbsp;&nbsp;');
//                                }

                            }
                            else{
                                if(arr[indi]['mark_invisible'] == "true"){
                                    buffer_previous_time = whole_date+' '+arr[indi]['Time'];
                                    buffer_plus = moment(whole_date+' '+arr[indi]['Time']).add(parseInt(buffer.split(':')[1]), 'm').toDate();
                                    date_new_buffer_2 = buffer_plus.getFullYear()+'/'+getDateFormat(buffer_plus.getMonth()+1)+'/'+buffer_plus.getDate()+' '+buffer_plus.getHours()+':'+buffer_plus.toLocaleTimeString().split(':')[1]+':'+buffer_plus.toLocaleTimeString().split(':')[2].split(' ')[0];
//                                    continue;
                                }
                                else{
                                    bk_class.append('<span><span  class="disabled disable_msg notclickable" id="'+arr[indi]['id']+'" t-att-data-slot_plans="'+arr[indi]['Time']+'">'+arr[indi]['Time']+'</span></span>&nbsp;&nbsp;');
                                    buffer_previous_time = whole_date+' '+arr[indi]['Time'];
                                    buffer_plus = moment(whole_date+' '+arr[indi]['Time']).add(parseInt(buffer.split(':')[1]), 'm').toDate();
                                    date_new_buffer_2 = buffer_plus.getFullYear()+'/'+getDateFormat(buffer_plus.getMonth()+1)+'/'+buffer_plus.getDate()+' '+buffer_plus.getHours()+':'+buffer_plus.toLocaleTimeString().split(':')[1]+':'+buffer_plus.toLocaleTimeString().split(':')[2].split(' ')[0];
                                    br_count++;
                                }
                            }
                        }
                        else{
                            if(Date.parse(whole_date+' '+arr[indi]['Time']) > Date.parse(date_new_2+' '+dates_today_24[1])){
                                if(arr[indi].status == 'green'){
                                    if(arr[indi]['mark_invisible'] == "true"){

                                    }
                                    else{
                                        bk_class.append('<span><span class="bk_slot_div clickable_time" id="'+arr[indi]['id']+'" t-att-data-slot_plans="'+arr[indi]['Time']+'">'+arr[indi]['Time']+'</span></span>&nbsp;&nbsp;');
                                        br_count++;
                                    }
                                }
                                else if(arr[indi].status == 'grey'){
                                     if(arr[indi]['mark_invisible'] == "true"){

                                     }
                                     else{
                                          bk_class.append('<span><span  class="disabled disable_msg notclickable" id="'+arr[indi]['id']+'" t-att-data-slot_plans="'+arr[indi]['Time']+'">'+arr[indi]['Time']+'</span></span>&nbsp;&nbsp;');
                                          br_count++;
                                     }
                                }
                            }
                            else{
                                 if(arr[indi]['mark_invisible'] == "true"){

                                 }
                                 else{
                                    bk_class.append('<span><span  class="disabled disable_msg notclickable" id="'+arr[indi]['id']+'" t-att-data-slot_plans="'+arr[indi]['Time']+'">'+arr[indi]['Time']+'</span></span>&nbsp;&nbsp;');
                                    br_count++;
                                 }
                           }
                        }
//                        br_count++;
                    }
                    var seats = $('#seats').val();
                    seats.replaceAll("},{","\"},{").replace("}]",",\"}]");
                    var parse_seats = JSON.parse(seats);
                    if(seats_future == 'Error'){
                        $("input").prop("disabled", true );
                            $("textarea").prop("disabled", true );
                            $("select").prop("disabled", true );
                            $('#spsrry').hide();
                            $('#spsrry2').show().text('Seats not available | We are sorry but we have no more seats available currently, please call us'+' '+$('#companyphone').val());
                    }

                    if(parse_seats.length > 0){
                        for(var sd=0;sd<parse_seats.length;sd++){
                            if(parse_seats[sd]['date'] == moment(whole_date).format("YYYY-MM-DD")){
                                if(parse_seats[sd]['seat'] == 0){
                                    $("input").prop("disabled", true );
                                    $("textarea").prop("disabled", true );
                                    $("select").prop("disabled", true );
                                    $('#spsrry').hide();
                                    $('#spsrry2').show().text('Seats not available | We are sorry but we have no more seats available currently, please call us'+' '+$('#companyphone').val());
                                }
                            }
                        }
//                       if(mydate <= mydatetoday){
//                            $("input").prop("disabled", true );
//                            $("textarea").prop("disabled", true );
//                            $("select").prop("disabled", true );
//                            $('#spsrry').hide();
//                            $('#spsrry2').show().text('Seats not available | We are sorry but we have no more seats available currently, please call us'+' '+$('#companyphone').val());
//                        }
                    }
//                    else{
//                        $("input").prop("enable", true );
//                        $("textarea").prop("enable", true );
//                        $("select").prop("enable", true );
//                        $("input").prop("disabled", false );
//                        $("textarea").prop("disabled", false );
//                        $("select").prop("disabled", false );
//                        $('#spsrry2').hide();
//                    }
//                    $("span > span", $bkSlot1)
//                      .sort((a, b) => a.id - b.id)
//                      .each((i, el) => $bkSlot1.append($(el).parent()));
                    if($('#user_name').val()){
                        $('#name').val($('#user_name').val());
                    }
                    if($('#user_login').val()){
                        $('#email').val($('#user_login').val());
                    }
                    if($('#companyphone').val()){
                        $('#spanphone').text($('#companyphone').val());
                        $('#spancompanyphone').val($('#companyphone').val());
                    }if($('#current_time').val() < 30){
                        $('.timekitchen').text('Please take notice that the kitchen will be closing at 22:00. During the week and in weekends at 22.30');
                    }if($('#user_phone').val()){
                        $('#phone').val($('#user_phone').val());
                    }
//                   $('.bk_slot_div1').append('<span t-att-class="bk_slot_div" style="padding: 6px 11px;background: #FFFFFF;font-size: 14px;color: #555555;text-align: center;border: 1px solid #979797;border-radius: 4px;cursor: pointer" t-att-data-time_slot_id="1" t-att-data-slot_plans="1">10-11</span>');
                   if(view['name'] == 'month'){
                    $('#my_datetimepicker').val('');
                   }
                   if(view['name'] == 'agendaWeek' || view['name'] == 'agendaDay'){
                       $('#my_datetimepicker').val(timestr);
                   }
                   if ($("#eating_type").val() == "breakfast"){
                       $('#Type').val("BreakFast");
                   }
                   else if ($("#eating_type").val() == "Lunch"){
                       $('#Type').val("Lunch");
                   }
                   else{
                    $('#Type').val("Dinner");
                   }

                   self.$modal.find("#submit_calendar_booking").on('click', function () {
                       self.$modal.modal('hide');
                   });
               if(mydate < mydatetoday){
                   alert("This date has already passed, please select a current or a future date");
                    $("input").prop("disabled", true );
                    $("textarea").prop("disabled", true );
                    $("select").prop("disabled", true );
                    $('#spsrry2').show().text('Old dates cannot be selected. Select todays date or advance date');
               }
//               else{
//                $('#spsrry2').hide();
//               }

//               } else {
//                   alert("This timeslot has already been booked");
//               }

           }
    }); //end fullcalendar load


function convert_float_time(float_time) {
    var format_time = "";
    var decimal = float_time % 1;
    format_time = Math.floor(float_time) + ":" + (60 * decimal);
    return format_time
}
function getDateFormat(month_date){

    if(month_date > 0 && month_date <10){
        month_date = '0'+String(month_date);
    }
    return month_date;
}

function getDates(startDate, endDate) {
  var now = startDate,
    dates = [];

  while (now.format('YYYY-MM-DD') <= endDate.format('YYYY-MM-DD')) {
    dates.push(now.format('YYYY-MM-DD'));
    now.add('days', 1);
  }
  return dates;
};

}); //End document load


});