# -*- coding: utf-8 -*-
import werkzeug
import json
import base64
import logging
_logger = logging.getLogger(__name__)
from dateutil.parser import parse
import dateutil
import time
import pytz
from datetime import datetime, timedelta

import odoo.http as http
from odoo.http import request
from odoo.exceptions import UserError
from odoo import _,fields
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, format_datetime

from odoo.addons.http_routing.models.ir_http import slug

class WebsiteBookingController(http.Controller):

    @http.route('/book/personalinfo', type="http", auth="public", website=True)
    def book_calendar_create(self, **kw):
        """Creates a booking using the fields on the booking field"""
        module_allow_auto_validation = request.env['ir.config_parameter'].sudo().get_param('website_calendar_booking.module_allow_auto_validation')
        module_allow_auto_mail = request.env['ir.config_parameter'].sudo().get_param('website_calendar_booking.module_allow_auto_mail')
        values = {}
        for field_name, field_value in kw.items():
            values[field_name] = field_value

        calendar = request.env['website.calendar'].sudo().browse( int(values['calendar_id']) )

        #worlds worse way of converting to UTC...
        parse_string = values['start']
        if "+" in parse_string:
            start_date = parse(parse_string.replace("+","-") ).astimezone(pytz.utc)
        elif "-" in parse_string:
            start_date = parse(parse_string.replace("-","+") ).astimezone(pytz.utc)
        if not kw.get('start_timeslot'):
            raise UserError(_('Time slot is not selected. Select Time Slot'))
        # table = request.env['table.time.slot'].search([('id','=',kw.get('start_timeslot'))])
        time_slot_event = request.env['time.slot.event'].search([('id','=',kw.get('start_timeslot'))])
        alpha_minutes = calendar.booking_slot_duration * 60
        stop_time = start_date + timedelta(minutes=alpha_minutes)
        # time_t = datetime.strptime(values['my_datetimepicker'].split(' ')[0]+':00', "%H:%M:%S")
        # delta = timedelta(hours=time_t.hour, minutes=time_t.minute, seconds=time_t.second)
        # startdate_add = start_date+delta
        alpha_minutes_start = time_slot_event.name*60
        start_date = start_date + timedelta(minutes=alpha_minutes_start)
        stop_time = stop_time.strftime("%Y-%m-%d %H:%M:%S")
        start_date = start_date.strftime("%Y-%m-%d %H:%M:%S")
        # start_date = startdate_add.strftime("%Y-%m-%d %H:%M:%S")

        calendar.booking_slot_duration
        pax = request.env['pax.person']
        if values['Pax'] == 'More than 6':
            pax = request.env['pax.person'].search([('name', '=', 'More than 6')])
            values['Pax'] = 'morethan6'
        else:
            pax = request.env['pax.person'].search([('name','=',values['Pax'])])
        final_date = fields.Datetime.to_datetime(start_date).astimezone(pytz.UTC).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        string_date = str(fields.Datetime.to_datetime(start_date).date())
        date_start =  string_date + ' 00:00:00'
        date_end = string_date + ' 23:59:59'
        # check_req = request.env['reservation.event'].search(
        #     [('booking_email', '=', values['email']),('inactive', '=', False),('date_str','=',str(final_date)),('state','not in',['reject','available'])])
        check_req = request.env['reservation.event'].search(
            [('booking_email', '=', values['email']), ('inactive', '=', False), ('date_str', '>=', date_start),
             ('date_str', '<=', date_end), ('state', 'not in', ['reject', 'available'])])
        if not check_req:
            cal_event = request.env['reservation.event'].sudo().create({'user_id': calendar.user_id.id,
                                                                    'name': values['name'],
                                                                    'start': fields.Datetime.to_datetime(final_date)+ timedelta(hours=4),
                                                                    'date_str': str(final_date),
                                                                    'stop': stop_time,
                                                                    'phone':values['phone'],
                                                                    'pax':values['Pax'],
                                                                    'pax_person':pax.id,
                                                                    'booking_email': values['email'],
                                                                    'description': values['comment'],
                                                                    'type':values['Type'],
                                                                    'time_slot_event':time_slot_event.id,
                                                                    # 'browser_info':request.httprequest.user_agent.browser.title()+' v'+request.httprequest.user_agent.version,
                                                                    'browser_info':values['browser_info'],
                                                                    # 'table_time_slot':table.id,
                                                                    })
        else:
            # raise UserError(_('Your reservation order have already been created contact %s for any inconvenience' % request.env.company.phone))
            return http.request.render('website_calendar_booking.error_confirmation', {'order': check_req,'phone':request.env.company.phone})

        if module_allow_auto_validation:
            # if cal_event.start.date() == fields.Date().today():
                cal_event.button_validate_action()
        if module_allow_auto_mail:
            cal_event.SendByEmail()
            cal_event.with_context(mail=1).button_sendMail_action()

        # cal_event = request.env['calendar.event'].sudo().create({'user_id': calendar.user_id.id,'name': values['name'] + " (Booking)", 'start': start_date,'stop': stop_time, 'booking_email': values['email'], 'description': values['email'] + "\n" + values['comment'] })

        # return werkzeug.utils.redirect("/book/calendar/" + str(calendar.id) )
        return request.render("website_calendar_booking.confirmation", {'order': cal_event})

    @http.route('/book/calendar/create', type="http", auth="public", website=True)
    def book_personal_info_create(self, **kw):
        if not kw.get('start_timeslot'):
            raise UserError(_('Time slot is not selected. Select Time Slot'))
        print('kw',kw)
        return request.render("website_calendar_booking.personal_info", {'order': kw})

    @http.route('/book/calendar/<calendar>', type="http", auth="public", website=True)
    def book_calendar(self, calendar, **kw):
        """Let's user see all aviable booking times and create bookings"""
        # my_calendar = request.env['website.calendar'].sudo().browse( int(calendar) )
        my_calendar = request.env['website.calendar'].sudo().browse( int(calendar) )
        print("kw",kw)
        print("context",request._context)
        return http.request.render('website_calendar_booking.website_calendar_booking_page', {'calendar': my_calendar})

    def get_time_cal(self):
        kitchen_close = '22:00:00'
        kitchen_close_weekend = '22:30:00'
        if request._context.get('tz'):
            current = fields.Datetime.now().now(tz=pytz.timezone(request._context.get('tz'))).replace(microsecond=0).replace(
            tzinfo=None)
        else:
            current = fields.Datetime.now()
        d1 = current
        if current.strftime("%A") in ['Saturday','Sunday']:
            kitchen = str(current.date()) + ' ' + kitchen_close_weekend
            d1 = datetime.strptime(kitchen, '%Y-%m-%d %H:%M:%S')
        else:
            kitchen = str(current.date()) + ' ' + kitchen_close
            d1 = datetime.strptime(kitchen, '%Y-%m-%d %H:%M:%S')
        diff = d1 - current
        diff_final = (diff.days * 24 * 60) + (diff.seconds/60)
        # if diff_final <= 30:
        return diff_final
        # else:
        #     return False


    @http.route('/book/breakfast/<calendar>', type="http", auth="public", website=True)
    def book_breakfast(self, calendar, **kw):
        """Let's user see all aviable booking times and create bookings"""
        my_calendar = request.env['website.calendar'].sudo().browse(int(calendar))
        print("kw", kw)
        print("context", request._context)
        table = self.get_table()
        time_slot = self.book_calendar_timeslot()
        time_slot_event = self.book_calendar_timeslotevent('Breakfast')
        time_slot_event_full = self.book_calendar_timeslotevent_full('Breakfast')
        book_calendar_time_frame_date = self.book_calendar_time_frame_date('Breakfast')
        print('timeslot', time_slot)
        user = request.env['res.users']
        buffer = request.env['ir.config_parameter'].sudo().get_param('website_calendar_booking.buffer')
        seats = request.env['reservation.event.dashboard'].search([('state', '=', 'seats')])
        seat_string = ""
        for s in seats:
            seat_string += '{'
            seat_string += '"seat": "' + str(s.seats) + '",'
            seat_string += '"date": "' + str(s.date_dash) + '"'
            seat_string += '},'
        seat_string = seat_string[:-1]
        if not request.env.ref('base.public_user') == request.env.user:
            user = request.env.user
        return http.request.render('website_calendar_booking.website_calendar_booking_page', {'calendar': my_calendar,
                                                                                              'eating_type':'breakfast',
                                                                                              'time_slot':time_slot,
                                                                                              'table_slot':table,
                                                                                              'time_slot_event':time_slot_event,
                                                                                              'user':user,
                                                                                              'company':request.env.company,
                                                                                              'current_time':self.get_time_cal(),
                                                                                              'time_slot_event_full':time_slot_event_full,
                                                                                              'seats':"["+seat_string+"]",
                                                                                              'buffer': buffer,
                                                                                              'book_calendar_time_frame_date': book_calendar_time_frame_date,
                                                                                              })

    @http.route('/book/Lunch/<calendar>', type="http", auth="public", website=True)
    def book_Lunch(self, calendar, **kw):
        """Let's user see all aviable booking times and create bookings"""
        my_calendar = request.env['website.calendar'].sudo().browse(int(calendar))
        print("kw", kw)
        print("context", request._context)
        table = self.get_table()
        time_slot = self.book_calendar_timeslot()
        time_slot_event = self.book_calendar_timeslotevent('Lunch')
        time_slot_event_full = self.book_calendar_timeslotevent_full('Lunch')
        book_calendar_time_frame_date = self.book_calendar_time_frame_date('Lunch')
        user = request.env['res.users']
        buffer = request.env['ir.config_parameter'].sudo().get_param('website_calendar_booking.buffer')
        seats = request.env['reservation.event.dashboard'].search([('state','=','seats')])
        seat_string = ""
        for s in seats:
            seat_string += '{'
            seat_string += '"seat": "' + str(s.seats) + '",'
            seat_string += '"date": "' + str(s.date_dash) + '"'
            seat_string += '},'
        seat_string = seat_string[:-1]
        if not request.env.ref('base.public_user') == request.env.user:
            user = request.env.user
        print('timeslot', time_slot)
        return http.request.render('website_calendar_booking.website_calendar_booking_page',
                                   {'calendar': my_calendar, 'eating_type': 'Lunch','time_slot':time_slot,'table_slot':table,
                                    'time_slot_event':time_slot_event,
                                    'user':user,
                                    'current_time': self.get_time_cal(),
                                    'company': request.env.company,
                                    'time_slot_event_full':time_slot_event_full,
                                    'seats':"["+seat_string+"]",
                                    'buffer':buffer,
                                    'book_calendar_time_frame_date':book_calendar_time_frame_date,
                                    })

    @http.route('/book/Dinner/<calendar>', type="http", auth="public", website=True)
    def book_Dinner(self, calendar, **kw):
        """Let's user see all aviable booking times and create bookings"""
        my_calendar = request.env['website.calendar'].sudo().browse(int(calendar))
        print("kw", kw)
        print("context", request._context)
        table = self.get_table()
        time_slot = self.book_calendar_timeslot()
        time_slot_event = self.book_calendar_timeslotevent('Dinner')
        time_slot_event_full = self.book_calendar_timeslotevent_full('Dinner')
        book_calendar_time_frame_date = self.book_calendar_time_frame_date('Dinner')
        print('timeslot',time_slot)
        seats = request.env['reservation.event.dashboard'].search([('state', '=', 'seats')])
        seat_string = ""
        for s in seats:
            seat_string += '{'
            seat_string += '"seat": "' + str(s.seats) + '",'
            seat_string += '"date": "' + str(s.date_dash) + '"'
            seat_string += '},'
        seat_string = seat_string[:-1]
        user = request.env['res.users']
        buffer = request.env['ir.config_parameter'].sudo().get_param('website_calendar_booking.buffer')
        if not request.env.ref('base.public_user') == request.env.user:
            user = request.env.user
        return http.request.render('website_calendar_booking.website_calendar_booking_page',
                                   {'calendar': my_calendar, 'eating_type': 'Dinner','time_slot':time_slot,'table_slot':table,
                                    'time_slot_event':time_slot_event,
                                    'user':user,
                                    'current_time':self.get_time_cal(),
                                    'company': request.env.company,
                                    'time_slot_event_full':time_slot_event_full,
                                    'seats':"["+seat_string+"]",
                                    'buffer':buffer,
                                    'book_calendar_time_frame_date':book_calendar_time_frame_date
                                    })

    @http.route(['/book/cancel/<int:order>'], type="http", auth="public", website=True)
    def home_reservation_cancel(self,order):
        """Let's user see all aviable booking times and create bookings"""
        print("Cancel")
        print(order)
        reserve_id = request.env['reservation.event'].search([('id', '=', order)])
        # reserve_id.update({'state':'reject'})
        reserve_id.button_reject_action()
        reserve_id.sudo().SendCancelEmail()
        return http.request.render('website_calendar_booking.cancellation',{'order': reserve_id})

    @http.route('/book/calendar', type="http", auth="public", website=True)
    def home_reservation_calendar(self):
        """Let's user see all aviable booking times and create bookings"""
        return http.request.render('website_calendar_booking.home_reservation')

    def get_table(self):
        arr = []
        my_calendar = request.env['table.time.slot'].sudo().search([('state', '=', 'Available')])
        for mc in my_calendar:
            arr.append(mc.name.name)
        arr = list(set(arr))
        str_arr = ""
        str_arr += '['
        length = 0
        for rec in arr:
            str_arr += '"'+rec+'"'
            if length < (len(arr)-1):
                str_arr += ','
            length = length + 1

        str_arr += ']'
        print('str_arr',str_arr)
        return str_arr

    def book_calendar_time_frame_date(self, type):
        my_calendar = request.env['time.slot.date'].sudo().search([('type', 'ilike', type)])
        fiter_calendar = request.env['time.slot.date']
        share_id = request.env['time.slot.date']
        return_string = ""
        days = ''
        dates_list = []
        var_list = {}
        for dl in my_calendar:
            dates_list.append(dl.date)
        dates_list = list(set(dates_list))
        time_share = []
        slot_left = -100
        for ld in dates_list:
            slot_left = -100
            track_id = None
            for mc in my_calendar:
                if ld == mc.date:
                    if slot_left == -100:
                        slot_left = mc.slots_left
                        track_id = mc
                        var_list[str(ld)+' '+str(mc.float_convert_in_time(mc.name))] = mc
                    elif slot_left >= mc.slots_left:
                        slot_left = mc.slots_left
                        track_id = mc
                        var_list[str(ld)+' '+str(mc.float_convert_in_time(mc.name))] = mc
                    if mc.share_slot and (not mc.name in time_share):
                        time_share.append(mc.name)
                        share_id += mc
                        var_list[str(ld)+' '+str(mc.float_convert_in_time(mc.name))] = mc
            # fiter_calendar += track_id
            # fiter_calendar += share_id - fiter_calendar
        for key,value in var_list.items():
            fiter_calendar += var_list[str(key)]
        print('filter_calendar',fiter_calendar)


        for event in fiter_calendar:
            days = ''
            for day in event.days:
                days += day.abre + ','
            time_str = event.float_convert_in_time(event.name)
            # '-'+event.time_slot.float_convert_in_time(event.time_slot.lname)
            return_string += '{'
            return_string += '"id": "' + str(event.id) + '",'
            return_string += '"slots": "' + str(event.slots) + '",'
            return_string += '"slots_left": "' + str(event.slots_left) + '",'
            return_string += '"days": "' + days[:-1] + '",'
            return_string += '"mark_invisible": "' + str(event.mark_invisible).lower() + '",'
            return_string += '"date": "' + str(event.date) + '",'
            return_string += '"reservation": "' + str(event.reservation_id.id) + '",'
            return_string += '"time_slot": "' + str(event.time_slot.id) + '",'
            return_string += '"seats": "' + str(event.seats_left) + '",'
            return_string += '"time": "' + time_str + ' ' + str(event.day_type or '') + '"'
            return_string += '},'
        return_string = return_string[:-1]
        print(return_string)
        return "[" + return_string + "]"

    def book_calendar_timeslotevent(self,type):
        my_calendar = request.env['time.slot.event'].sudo().search([('type','ilike',type),('slots_left','>',0)])
        return_string = ""
        days = ''
        for event in my_calendar:
            days = ''
            for day in event.days:
                days += day.abre+','
            time_str = event.float_convert_in_time(event.name)
                       #'-'+event.time_slot.float_convert_in_time(event.time_slot.lname)
            return_string += '{'
            return_string += '"id": "' + str(event.id) + '",'
            return_string += '"slots": "' + str(event.slots) + '",'
            return_string += '"slots_left": "' + str(event.slots_left) + '",'
            return_string += '"days": "' + days[:-1] + '",'
            return_string += '"mark_invisible": "' + str(event.mark_invisible).lower() + '",'
            return_string += '"time": "' + time_str+' '+str(event.day_type or '')+'"'
            return_string += '},'
        return_string = return_string[:-1]
        print(return_string)
        return "[" + return_string + "]"

    # same functionality, rebrand will be done later
    def book_calendar_timeslotevent_full(self,type):
        my_calendar = request.env['time.slot.event'].sudo().search([('type','ilike',type),('slots_left','=',0)])
        return_string = ""
        days = ''
        for event in my_calendar:
            days = ''
            for day in event.days:
                days += day.abre+','
            time_str = event.float_convert_in_time(event.name)
                       #'-'+event.time_slot.float_convert_in_time(event.time_slot.lname)
            return_string += '{'
            return_string += '"id": "' + str(event.id) + '",'
            return_string += '"slots": "' + str(event.slots) + '",'
            return_string += '"slots_left": "' + str(event.slots_left) + '",'
            return_string += '"days": "' + days[:-1] + '",'
            return_string += '"mark_invisible": "' + str(event.mark_invisible).lower() + '",'
            return_string += '"time": "' + time_str + ' ' + str(event.day_type or '') + '"'
            return_string += '},'
        return_string = return_string[:-1]
        print(return_string)
        return "[" + return_string + "]"

    def book_calendar_timeslot(self):
        my_calendar = request.env['table.time.slot'].sudo().search([('state','=','Available')])
        return_string = ""
        for event in my_calendar:
            time_str = event.time_slot.float_convert_in_time(event.time_slot.name)
                       #'-'+event.time_slot.float_convert_in_time(event.time_slot.lname)
            return_string += '{'
            return_string += '"id": "' + str(event.id) + '",'
            return_string += '"table": "' + str(event.name.name)+ '",'
            return_string += '"date_time": "' + str(event.date_time)+ '",'
            return_string += '"state": "' + str(event.state)+ '",'
            return_string += '"time": "' + time_str + ' ' + str(event.day_type or '') + '"'
            return_string += '},'
        return_string = return_string[:-1]
        print(return_string)
        return "[" + return_string + "]"

    @http.route('/book/calendar/timeframe/<calendar>', type="http", auth="public", website=True)
    def book_calendar_timeframe(self, calendar, **kw):
        my_calendar = request.env['website.calendar'].sudo().browse(int(calendar))
        return_string = ""
        for time_frame in my_calendar.time_frame_ids:
            return_string += '{'

            day_number = 0
            if time_frame.day == "sunday":
                day_number = 0

            if time_frame.day == "monday":
                day_number = 1

            if time_frame.day == "tuesday":
                day_number = 2

            if time_frame.day == "wednesday":
                day_number = 3

            if time_frame.day == "thursday":
                day_number = 4

            if time_frame.day == "friday":
                day_number = 5

            if time_frame.day == "saturday":
                day_number = 6

            return_string += '"start": "' + str(time_frame.start_time).replace(".",":") + '",'
            return_string += '"end": "' + str(time_frame.end_time).replace(".",":") + '",'
            return_string += '"dow": [' + str(day_number) + ']'
            return_string += '},'

        return_string = return_string[:-1]
        return "[" +  return_string + "]"

    @http.route('/book/calendar/events/<user>', type="http", auth="public", csrf=False, website=True)
    def book_calendar_events(self, user, **kw):
        """Get events from calendar.event"""

        values = {}
        for field_name, field_value in kw.items():
            values[field_name] = field_value

        return_string = ""
        # for event in request.env['calendar.event'].sudo().search([('user_id','=', int(user) )]):
        for event in request.env['reservation.event'].sudo().search([('user_id','=', int(user)),('state','not in',['available','reject'])]):
            return_string += '{'
            return_string += '"id": "' + str(event.id) + '",'

            #Only display the event title if you are the owner of this event
            if http.request.env.user.id == int(user):
                return_string += '"title": "' + event.name + '",'
                return_string += '"className": "wcb_back_event",'

            return_string += '"start": "' + str(event.start) + '+00:00",'
            return_string += '"end": "' + str(event.stop) + '+00:00"'
            return_string += '},'

        return_string = return_string[:-1]
        print(return_string)
        return "[" +  return_string + "]"

    @http.route('/book/calendar/timeslot/<eating_types>', type="http", auth="public", csrf=False, website=True)
    def book_calendar_events(self, eating_types, **kw):
        string_ret = self.book_calendar_timeslotevent(eating_types)
        return string_ret