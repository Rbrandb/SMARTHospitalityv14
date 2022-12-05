# -*- coding: utf-8 -*-
from odoo.http import request
import pytz
import logging
_logger = logging.getLogger(__name__)

from odoo import api, fields, models,_
from odoo.addons.base.models import ir_mail_server
from odoo.exceptions import UserError
from datetime import timedelta

class ReservationEvent(models.Model):
    _name = 'reservation.event'

    name = fields.Char("Name")
    booking_email = fields.Char("Email")
    phone = fields.Char("Phone")
    pax = fields.Selection([('1','1'),
                            ('2', '2'),
                            ('3', '3'),
                            ('4', '4'),
                            ('5', '5'),
                            ('6', '6'),
                            ('morethan6', 'More than 6')
                            ],string="PAX")
    pax_person = fields.Many2one('pax.person',string="PAX")
    description = fields.Text("Special Occassion")
    start = fields.Datetime("Date")
    stop_time = fields.Datetime("Date")
    date_str = fields.Char("Date")
    date_boolean = fields.Boolean("Change Date", default=False)
    stop = fields.Datetime("Date")
    duration = fields.Float("Duration")
    type = fields.Char("Type")
    user_id = fields.Many2one('res.users', 'Responsible', default=lambda self: self.env.user)
    partner_ids = fields.Many2one('res.partner',string="Responsible")
    code = fields.Char("Code")
    state = fields.Selection([('draft','New'),('confirm','Confirm'),('reject','Cancelled'),
                            ('available','Free')
                              ],string='State',track_visibility='onchange', default='draft', copy=False)
    # table = fields.Many2one('table.event',string="Table")
    table_time_slot = fields.Many2one('table.time.slot',string="Table")
    time_slot_event = fields.Many2one('time.slot.event',string="Time Slot")
    pos_table_id = fields.Many2one('restaurant.table', string="Table")
    inactive = fields.Boolean("Archive/Unarchive",default=False)
    # email_reminder = fields.Date()
    email_reminders = fields.Date()
    advance = fields.Boolean("Advance Booking",default=False)
    browser_info = fields.Char("Browser Infor")

    # _sql_constraints = [
    #     ('booking_email_time_uniq', 'unique(booking_email, date_str)', 'reservation is already created!'),
    # ]

    @api.model
    def create_from_ui(self, reservation):
        """ create or modify a reservation from the point of sale ui.
            reservation contains the reservation's fields. """
        # image is a dataurl, get the data after the comma
        pax = self.env['pax.person']
        if reservation.get('pax'):
            reservation['pax_person'] = pax.search([('name','=',reservation.get('pax'))]).id
        reservation_id = reservation.pop('id', False)
        if reservation_id:  # Modifying existing reservation
            self.browse(reservation_id).write(reservation)
        else:
            reservation_id = self.create(reservation).id
        return reservation_id

    @api.onchange('pax_person')
    def onchange_pax_person(self):
        if self.pax_person:
            self.pax = str(self.pax_person.name)

    @api.onchange('date_str','start')
    def onchange_start(self):
        if self.start:
            self.date_str = str(self.start - timedelta(hours=4))
        pass

    @api.onchange('pos_table_id')
    def onchange_pos_table_id(self):
        table = self.env['reservation.event'].search([('pos_table_id','=',self.pos_table_id.id),
                                                      ('pos_table_id','!=',False),
                                                      ('state','!=','available')])
        print('table',table)
        if len(table) > 0:
            raise UserError(_("Table are already allocated"))


    def OnchangeTable(self,table_id):
        check = self.env['reservation.event'].search([('pos_table_id','=',int(table_id)),('pos_table_id','!=',False),('state','!=','available')])
        if not check:
            self.pos_table_id = int(table_id)
        else:
            raise UserError(_("Table are already allocated"))

    def get_pos_table_records(self):
        print("--------get_post_table_records------------------", self)
        return self.pos_table_id

    def cron_expire_reservation_event(self):
        # today= fields.Datetime.now()
        if self._context.get('tz'):
            today= fields.Datetime.now().now(tz=pytz.timezone(self._context.get('tz'))).replace(microsecond=0).replace(tzinfo=None)
        else:
            today = fields.Datetime.now()
        # reservations = self.env['reservation.event'].search([('state','in',['confirm'])])
        # reservations = self.env['reservation.event'].search([('state','in',['confirm','draft']),('inactive','=',False)])
        reservations = self.env['reservation.event'].search([('inactive','=',False)])
        print("Expiry")

        for rec in reservations:
            start = fields.Datetime.to_datetime(rec.date_str)
            if today > start:
                if rec.state in ['available','draft','reject']:
                    rec.make_archive()
                    # rec.unlink()
                else:
                    rec.button_available_action()
                    rec.make_archive()
                    # rec.unlink()
                # days_left = rec.start.date() - today.date()

    def cron_validate_new_reservation_event(self):
        if self._context.get('tz'):
            today = fields.Datetime.now().now(tz=pytz.timezone(self._context.get('tz'))).replace(microsecond=0).replace(
            tzinfo=None)
        else:
            today = fields.Datetime.now()
        reservations = self.env['reservation.event'].search([('state', 'in', ['draft','confirm']), ('inactive', '=', False)])
        for rec in reservations:
            if today.date() == rec.start.date():
                rec.button_validate_action()
                rec.with_context(mail=1).button_sendMail_action()
        # button_validate_action


    def cron_reminder_reservation_event(self):
        if self._context.get('tz'):
            today = fields.Datetime.now().now(tz=pytz.timezone(self._context.get('tz'))).replace(microsecond=0).replace(
            tzinfo=None)
        else:
            today = fields.Datetime.now()
        # reservations = self.env['reservation.event'].search([('state','in',['confirm'])])
        reservations = self.env['reservation.event'].search([('state', 'in',['confirm','draft']), ('inactive', '=', False)])
        print("Reminder")

        for rec in reservations:
            start = fields.Datetime.to_datetime(rec.date_str)
            days_left = start - today
            module_allow_auto_reminder = self.env['ir.config_parameter'].sudo().get_param(
                'website_calendar_booking.module_allow_auto_reminder')
            day = self.env['ir.config_parameter'].sudo().get_param('website_calendar_booking.day')
            time = self.env['ir.config_parameter'].sudo().get_param('website_calendar_booking.time')
            time_left = float(time)
            time_conv = timedelta(hours=time_left)
            msg = ''
            if module_allow_auto_reminder:
                if rec.create_date.date() == start.date():
                    pass
                elif days_left.days == int(day):
                    main_url = self.env['ir.config_parameter'].get_param('web.base.url')
                    cancel = 'if you would like to cancel your reservation, please click:<a href="' + main_url + '/book/cancel/' + str(
                        rec.id) + '">here</a>  or call the restaurant at ' + str(
                        self.env.company.phone) + '. Keep in mind that you should call the restaurant a minimum of two hours before the reservation time.\n\n'
                    if not rec.email_reminders or rec.email_reminders != fields.Date().today():
                        rec.email_reminders = fields.Date().today()
                        rec.reminder_SendByEmail(cancel, days_left)
                elif (not days_left.days < 0) and (days_left <= time_conv):
                    if not rec.email_reminders or rec.email_reminders != fields.Date().today():
                        rec.email_reminders = fields.Date().today()
                        msg = "Keep in mind that you should call the restaurant a minimum of two hours before the reservation time."
                        rec.reminder_SendByEmail(msg, days_left)

    def make_archive(self):
        self.inactive = True

    def get_whole_data(self):
        data = self.env['reservation.event'].search([('state','in',['draft','confirm','available'])])
        return data

    def get_recent_data(self):
        data = self.env['reservation.event'].search([('id','=',self.id)])
        return data

    def get_seats(self):
        seats = self.env['ir.config_parameter'].sudo().get_param('website_calendar_booking.seats')
        return int(seats)

    def button_validate_action(self):
        self.state = 'confirm'
        slot_date = self.env['time.slot.date']
        self.table_time_slot.state = 'Booked'
        seats_total = self.get_seats()
        if self._context.get('tz'):
            current = fields.Datetime.now().now(tz=pytz.timezone(self._context.get('tz'))).replace(microsecond=0).replace(
            tzinfo=None)
        else:
            current = fields.Datetime.now()
        date_str = fields.Datetime.to_datetime(self.date_str).date()
        slot_date = self.env['time.slot.date'].search([('date', '=', date_str), ('name', '=', self.time_slot_event.name)])
        # slot_date = self.env['time.slot.date'].search([('date','=',date_str),('time_slot','=',self.time_slot_event.id)])
        shared_date = self.env['time.slot.share'].search([('slots','=',self.time_slot_event.id)])
        # if not slot_date:
        #     slot_date = self.env['time.slot.date'].search([('time_slot','in',shared_date.slots.ids)])
        seat_date = self.env['time.slot.date'].search([('date', '=', date_str)])
        # days = self.env['time.days'].search([('name', '=', current.strftime("%A"))])
        days = self.env['time.days'].search([('name', '=', date_str.strftime(("%A")))])
        if not slot_date:
            if not self.time_slot_event.share_slot:
                slots_left = self.time_slot_event.slots - 1
                people = int(self.pax_person.name)
                if not seat_date:
                    seats = seats_total - people
                else:
                    seats = seat_date[-1].seats_left - people
                if seats < 0:
                    raise UserError(
                        _("Seats not available | We are sorry but we have no more seats available currently, please call us %s" % self.env.company.phone))
                slot_date = slot_date.create({'name':self.time_slot_event.name,
                                              'slots':self.time_slot_event.slots,
                                              'slots_left':slots_left,
                                              'days':days.id,
                                              'type':self.time_slot_event.type,
                                              'share_slot':self.time_slot_event.share_slot,
                                              'date':date_str,
                                              'seats_left':seats,
                                              'reservation_id': self.id,
                                              'time_slot': self.time_slot_event.id,
                                              })
            else:
                people = int(self.pax_person.name)
                if seat_date:
                    seats = seat_date[-1].seats_left - people
                else:
                    seats = seats_total - people
                if seats < 0:
                    raise UserError(
                        _("Seats not available | We are sorry but we have no more seats available currently, please call us %s" % self.env.company.phone))
                for share in self.time_slot_event.share_slot.slots:
                    slots_left = share.slots_left - 1
                    slot_date = slot_date.create({'name': share.name,
                                                  'slots': self.time_slot_event.slots,
                                                  'slots_left': slots_left,
                                                  'days': days.id,
                                                  'type': self.time_slot_event.type,
                                                  'share_slot': self.time_slot_event.share_slot.id,
                                                  'date': date_str,
                                                  'seats_left': seats,
                                                  'reservation_id': self.id,
                                                  'time_slot': self.time_slot_event.id,
                                                  })

        else:
            for date_slot in slot_date[-1]:
                people = int(self.pax_person.name)
                if not seat_date:
                    seats = date_slot.seats_left - people
                else:
                    seats = seat_date[-1].seats_left - people
                if seats < 0:
                    raise UserError(
                        _("Seats not available | We are sorry but we have no more seats available currently, please call us %s" % self.env.company.phone))
                if not self.time_slot_event.share_slot:
                    slots_left = date_slot.slots_left - 1
                    if slots_left < 0:
                        raise UserError(_("Slots are already filled"))
                    else:
                        slot_date = slot_date.create({'name': self.time_slot_event.name,
                                                  'slots': date_slot.slots,
                                                  'slots_left': slots_left,
                                                  'days': days.id,
                                                  'type': self.time_slot_event.type,
                                                  'share_slot': self.time_slot_event.share_slot.id,
                                                  'date': date_str,
                                                  'seats_left': seats,
                                                  'reservation_id': self.id,
                                                  'time_slot': self.time_slot_event.id,
                                                  })
                else:
                    people = int(self.pax_person.name)
                    # seats = date_slot.seats_left - people
                    if not seat_date:
                        seats = date_slot.seats_left - people
                    else:
                        seats = seat_date[-1].seats_left - people
                    if seats < 0:
                        raise UserError(
                            _("Seats not available | We are sorry but we have no more seats available currently, please call us %s" % self.env.company.phone))
                    for share in slot_date[-1].share_slot.slots:
                        slots_left = date_slot.slots_left - 1
                        if slots_left < 0:
                            raise UserError(_("Slots are already filled"))
                        else:
                            slot_date = slot_date.create({'name': share.name,
                                                      'slots': date_slot.slots,
                                                      'slots_left': slots_left,
                                                      'days': days.id,
                                                      'type': self.time_slot_event.type,
                                                      'share_slot': self.time_slot_event.share_slot.id,
                                                      'date': date_str,
                                                      'seats_left': seats,
                                                      'reservation_id': self.id,
                                                      'time_slot': self.time_slot_event.id,
                                                      })

    def button_reset_action(self):
        self.state = 'draft'
        self.process_further()

    def button_available_action(self):
        self.state = 'available'
        self.process_further()

    def process_further(self):
        seats_total = self.get_seats()
        reservation = self.env['reservation.event']
        date_str = fields.Datetime.to_datetime(self.date_str).date()
        slot_date = self.env['time.slot.date'].search([('reservation_id', '=', self.id)])
        # other_like_slots = self.env['time.slot.date'].search([('date','=',date_str)], order='id DESC')
        other_like_slots = self.env['time.slot.date'].search([('date','=',date_str)])
        left_slots = other_like_slots - slot_date
        for ls in left_slots:
            ls.reservation_id.state = 'draft'
            if not ls.reservation_id in reservation:
                reservation += ls.reservation_id
            ls.unlink()
        slot_date.unlink()
        for res in reservation:
            res.button_validate_action()
        pass
    # def button_validate_action(self):
    #     self.state = 'confirm'
    #     self.table_time_slot.state = 'Booked'
    #     seats = request.env['reservation.event.dashboard'].search([('state', '=', 'seats')])
    #     # self.table_time_slot.time_slot.slots_left = self.table_time_slot.time_slot.slots-1
    #     people = int(self.pax_person.name)
    #     result = seats.total_seats_amount - people
    #     date_today = fields.Date().today()
    #     date_str = fields.Datetime.to_datetime(self.date_str).date()
    #     if result < 0:
    #         if not date_str > date_today:
    #             raise UserError(_("Seats not available | We are sorry but we have no more seats available currently, please call us %s" % self.env.company.phone))
    #     if not date_str > date_today:
    #         if not self.time_slot_event.share_slot:
    #             if self.time_slot_event.slots_left > 0:
    #                 self.time_slot_event.slots_left = self.time_slot_event.slots_left-1
    #             else:
    #                 raise UserError(_("Slots are already filled"))
    #         else:
    #             for share in self.time_slot_event.share_slot.slots:
    #                 if share.slots_left > 0:
    #                     share.slots_left = share.slots_left - 1
    #                 else:
    #                     raise UserError(_("Slots are already filled"))
    #         self.advance = False
    #     else:
    #         self.advance = True

    # def button_available_action(self):
    #     self.state = 'available'
    #     self.table_time_slot.state = 'Available'
    #     self.table_time_slot.state = 'Available'
    #     if not self.time_slot_event.share_slot:
    #         self.time_slot_event.slots_left = self.time_slot_event.slots_left + 1
    #     else:
    #         for share in self.time_slot_event.share_slot.slots:
    #             share.slots_left = share.slots_left + 1

    def button_reject_action(self):
        self.state = 'reject'
        self.process_further()

    # def button_reset_action(self):
    #     self.state = 'draft'
    #     if not self.time_slot_event.share_slot:
    #         self.time_slot_event.slots_left = self.time_slot_event.slots_left + 1
    #     else:
    #         for share in self.time_slot_event.share_slot.slots:
    #             share.slots_left = share.slots_left + 1

    def reminder_SendByEmail(self,msg,days_left):
        '''
        This function opens a window to compose an email, with the remittance email template
        '''
        # self.ensure_one()
        td = ''
        btn_url = ''
        emp_pipe = self.env['reservation.event']
        template_obj = self.env['mail.template']

        if self:
            from_rfc2822 = ir_mail_server.extract_rfc2822_addresses(self.user_id.login)
            if not from_rfc2822:
                raise UserError(_(("Malformed 'Return-Path' or 'From' address: %r - "
                                   "It should contain one valid plain ASCII email e.g %r <%r@gmail.com>") % (
                                      self.user_id.login, self.user_id.login, self.user_id.login.lower())))
            emp_pipe = self
        else:
            emp_pipe = self
        days_hrs = ''
        str_hr = ''
        if days_left.days:
            if str(days_left).split(','):
                str_hr = 'and '+str(days_left).split(',')[1]+'hr(s) left'
            days_hrs += str(days_left.days)+' day(s) left '+str_hr
        elif days_left.seconds:
            days_hrs += str(days_left) + ' hour(s) left'
        for rec in self:
            if not rec.user_id:
                continue
            user_id = self.env['res.users'].search([('id', '=', self._context.get('uid'))])
            active_ids = self.env.context.get('uid', [])
            login = self.env['res.users'].search([('id', '=', active_ids)])
            template_obj = self.env['mail.mail']
            td = ''
            base_url = self.env['ir.config_parameter'].get_param('web.base.url')
            base_url += '/web#id=%d&view_type=form&model=%s' % (rec.id, 'reservation.event')
            message_body = '<p>Hello ' + str(
                rec.booking_email) + ',\n</p><br/><br/>This is a reminder about your reservation at Mundo Bizarro. You have '+str(days_hrs)+'. You can visit our website here: <a href="' + base_url + '">Visit</a>. '+msg
                # rec.booking_email) + ',\n</p><br/><br/>Reminder about your appointment. You have a day and hour(s) are left. '+msg

            total_message = message_body
            template_data = {
                'subject': ' Reminder About Appointment',
                'body_html': total_message,
                'email_from': self.user_id.login,
                # self.send_from,#self.outgoing_mail_server.name,#self.env['res.users'].search([('id', '=', active_ids)]).login,
                'email_to': self.booking_email,
            }
            template_id = template_obj.create(template_data)
            template_id.with_context(employee_pipeline=self).send()

    def SendCancelEmail(self):
        emp_pipe = self.env['reservation.event']
        template_obj = self.env['mail.template']

        if self:
            from_rfc2822 = ir_mail_server.extract_rfc2822_addresses(self.user_id.login)
            if not from_rfc2822:
                raise UserError(_(("Malformed 'Return-Path' or 'From' address: %r - "
                                   "It should contain one valid plain ASCII email e.g %r <%r@gmail.com>") % (
                                      self.user_id.login, self.user_id.login, self.user_id.login.lower())))
            emp_pipe = self
        else:
            emp_pipe = self

        for rec in self:
            if not rec.user_id:
                continue
            user_id = self.env['res.users'].search([('id', '=', self._context.get('uid'))])
            active_ids = self.env.context.get('uid', [])
            login = self.env['res.users'].search([('id', '=', active_ids)])
            template_obj = self.env['mail.mail']
            td = ''
            base_url = self.env['ir.config_parameter'].get_param('web.base.url')
            base_url += '/web#id=%d&view_type=form&model=%s' % (rec.id, 'reservation.event')
            message_body = '<p>Hello ' + str(
                rec.user_id.name) + ',\n</p><br/><br/>Reservation have been Cancelled.\n Please visit <a href="' + base_url + '">Visit</a>'

            total_message = message_body
            template_data = {
                'subject': rec.name + ' Notification About Cancellation of Reservation',
                'body_html': total_message,
                'email_from': self.user_id.login,
                # self.send_from,#self.outgoing_mail_server.name,#self.env['res.users'].search([('id', '=', active_ids)]).login,
                'email_to': self.user_id.login,
            }
            template_id = template_obj.create(template_data)
            template_id.with_context(employee_pipeline=self).send()

    def SendByEmail(self):
        '''
        This function opens a window to compose an email, with the remittance email template
        '''
        # self.ensure_one()
        td = ''
        btn_url = ''
        emp_pipe = self.env['reservation.event']
        template_obj = self.env['mail.template']

        if self:
            from_rfc2822 = ir_mail_server.extract_rfc2822_addresses(self.user_id.login)
            if not from_rfc2822:
                raise UserError(_(("Malformed 'Return-Path' or 'From' address: %r - "
                                   "It should contain one valid plain ASCII email e.g %r <%r@gmail.com>") % (
                                      self.user_id.login, self.user_id.login, self.user_id.login.lower())))
            emp_pipe = self
        else:
            emp_pipe = self

        for rec in self:
            if not rec.user_id:
                continue
            user_id = self.env['res.users'].search([('id', '=', self._context.get('uid'))])
            active_ids = self.env.context.get('uid', [])
            login = self.env['res.users'].search([('id', '=', active_ids)])
            template_obj = self.env['mail.mail']
            td = ''
            base_url = self.env['ir.config_parameter'].get_param('web.base.url')
            base_url += '/web#id=%d&view_type=form&model=%s' % (rec.id, 'reservation.event')
            message_body = '<p>Hello ' + str(
                rec.user_id.name) + ',\n</p><br/><br/>New Reservation have been recieved.\n Please visit <a href="' + base_url + '">Visit</a>'

            total_message = message_body
            mail_combine = self.user_id.login+','
            if self.env.company.managers:
                for rec_mail in self.env.company.managers:
                    mail_combine += rec_mail.login+','
            template_data = {
                'subject': rec.name + ' New Notification About Reservation',
                'body_html': total_message,
                'email_from': self.user_id.login,
                # self.send_from,#self.outgoing_mail_server.name,#self.env['res.users'].search([('id', '=', active_ids)]).login,
                'email_to': mail_combine,#self.user_id.login,
            }
            template_id = template_obj.create(template_data)
            template_id.with_context(employee_pipeline=self).send()

    def button_sendMail_action(self):
        td = ''
        btn_url = ''
        template_obj = self.env['mail.template']
        emp_pipe = self

        if self:
            from_rfc2822 = ir_mail_server.extract_rfc2822_addresses(self.env.company.email)
            if not from_rfc2822:
                raise UserError(_(("Malformed 'Return-Path' or 'From' address: %r - "
                                   "It should contain one valid plain ASCII email e.g %r <%r@gmail.com>") % (
                                      self.env.company.email, self.env.company.email, self.env.company.email.lower())))
            emp_pipe = self
        # else:
        #     emp_pipe = self.env['reservation.event.line'].search([])

        for rec in emp_pipe:
            if not rec:
                continue
            user_id = self.env['res.users'].search([('id', '=', self._context.get('uid'))])
            #            tb = self.env['crm.lead'].search([('stage_id','=',rec.pipeline_stages.id),('user_id','=',user_id.id)])
            # tb = self.env['crm.lead'].search([('stage_id', '=', rec.pipeline_stages.id)])
            # print('tb', tb)
            active_ids = self.env.context.get('uid', [])
            login = self.env['res.users'].search([('id', '=', active_ids)])
            # template_obj = self.env['mail.mail']
            td = ''
            state = ''
            if rec.state == 'confirm':
                state = 'has been confirmed. Your code is '+rec.code
            elif rec.state == 'reject':
                state = 'has been <b>Rejected</b> due to non-availability.'
            else:
                state = 'is being processed'
            message_body = '<p>Hello ' + str(
                rec.name) + ',\n</p><br/><br/>Your booking '+state +'\n <table border="0" width="100%" cellpadding="10" bgcolor="#ededed" style="padding: 20px; background-color: #ededed" summary="o_mail_notification">\n <thead>\n <td><b>Name</b></td>\n <td><b>Email</b></td>\n  <td><b>Phone</b></td>\n <td><b>Type</b></td>\n<td><b>Date</b></td>\n </thead>\n<tbody>'
            main_url = self.env['ir.config_parameter'].get_param('web.base.url')
            base_url = self.env['ir.config_parameter'].get_param('web.base.url')
            base_url += '/web#id=%d&view_type=form&model=%s' % (rec.id, 'reservation.event')
            td += '<tr><td>'+str(rec.name or '')+'</td><td>' + str(
                rec.booking_email or '') + '</td><td>' + str(rec.phone or '') + '</td><td>' + str(
                rec.type or '') + '</td><td>'+str(rec.date_str)+'</td></tr>'

            end_body = '</tbody>\n</table>\n\n\n '
            # if rec.pipeline_stages.training_url:
            #     btn_url = '<br></br><a style="text-decoration: none;color: white;background-color: #7c7bad;border-color: #7c7bad;padding: 5px 10px;padding-top: 5px;padding-bottom: 5px;font-size: 12px;line-height: 1.5;border-radius: 3px;" href="' + rec.pipeline_stages.training_url + '" class="button">Stage Tutorial</a>'
            cancel = '<br></br><br></br><br></br><br></br><br></br>To cancel the reservation please click on this url:<a href="'+main_url+'/book/cancel/'+str(rec.id)+'">Cancel</a>. \n\n'
            special_info = 'For more information, please contact or email us at: '+self.env.company.phone+ 'or at '+self.env.company.email
            total_message = message_body + td + end_body+cancel+special_info #+ btn_url
            lang = self.env.context.get('lang')
            template_data = {
                'subject': str(rec.name or '') + ' Reservation Management',
                'body_html': total_message,
                'email_from': self.env.company.email,
                # self.send_from,#self.outgoing_mail_server.name,#self.env['res.users'].search([('id', '=', active_ids)]).login,
                'email_to': rec.booking_email,
                'report_name': str(rec.name or '') + ' Reservation Management',
                'lang': lang,
                # 'res_id' : self.id,
                'model': 'reservation.event',
            }
            template_id = template_obj.create(template_data)
            template_id.model = 'reservation.event'

            if not len(emp_pipe) == 1 or emp_pipe._context.get('mail'):
                mail_mail = template_id.with_context(employee_pipeline=rec).send_mail(rec.id)
                sent = self.env['mail.mail'].browse(mail_mail).send()
                _logger.info("Mail-->customer : %s" % (sent), exc_info=True)
                _logger.info("Mail Template-->customer : %s" % (template_id), exc_info=True)
            else:
                ctx = {
                    'default_model': 'reservation.event',
                    'default_res_id': rec.ids[0],
                    'default_use_template': bool(template_id),
                    'default_template_id': template_id.id,
                    'default_composition_mode': 'comment',
                    'lang':lang,
                    # 'mark_so_as_sent': True,
                    # 'force_email': True,
                    # 'employee_pipeline':self,
                    # 'model_description': self.with_context(lang=lang).type_name,
                }
                return {
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model': 'mail.compose.message',
                    'views': [(False, 'form')],
                    'view_id': False,
                    'target': 'new',
                    'context': ctx,
                }


    @api.model
    def create(self, vals):
        count = 0
        date_time_string = str(fields.Datetime.to_datetime(vals['date_str']).date())
        date_start = date_time_string + ' 00:00:00'
        date_end = date_time_string + ' 23:59:59'
        # reservation = self.env['reservation.event'].search([('booking_email','=',vals.get('booking_email')),('date_str','=',vals['date_str']),('state','in',['draft','confirm'])])
        reservation = self.env['reservation.event'].search([('booking_email','=',vals.get('booking_email')),('date_str','>=',date_start),('date_str','<=',date_end),('state','in',['draft','confirm'])])
        if not vals.get('booking_email'):
            raise UserError(_("Mail id required"))
        if reservation:
            raise UserError(_("Reservation is already created with this mail id"))
        date_start = str(fields.Datetime.to_datetime(vals.get('date_str')).date()) + ' 00:00:00'
        date_end = str(fields.Datetime.to_datetime(vals.get('date_str')).date()) + ' 23:59:59'
        res_pax = self.env['reservation.event'].search(
            [('date_str', '>=', date_start), ('date_str', '<=', date_end),('state','in',['draft','confirm'])])
        for pax_count in res_pax:
            count = count + int(pax_count.pax_person.name)
        count = self.get_seats() - (count+vals.get('pax_person'))
        if count < 0:
            raise UserError(
                _("Seats not available | We are sorry but we have no more seats available currently, please call us %s" % self.env.company.phone))
        vals['code'] = self.env['ir.sequence'].next_by_code('reservation.event') or _('New')
        result = super().create(vals)
        # result.SendByEmail()
        return result

    def write(self, vals):
        for resv in self:
            count = 0
            date_start = str(fields.Datetime.to_datetime(resv.date_str).date()) + ' 00:00:00'
            date_end = str(fields.Datetime.to_datetime(resv.date_str).date()) + ' 23:59:59'
            res_pax = self.env['reservation.event'].search(
                [('date_str', '>=', date_start), ('date_str', '<=', date_end),('state','in',['draft','confirm'])])
            for pax_count in res_pax:
                if not self == pax_count:
                    count = count + int(pax_count.pax_person.name)
            count = self.get_seats() - (count+ (vals.get('pax_person') or int(self.pax_person.name)))
            if count < 0:
                raise UserError(
                    _("Seats not available | We are sorry but we have no more seats available currently, please call us %s" % self.env.company.phone))
        return super().write(vals)

    def unlink(self):
        if not self._context.get(('reser_delete')):
            for move in self:
                if move.start.date() == fields.Datetime.now().date():
                    raise UserError(_("You cannot delete an entry of today's date. You can Archive it"))
        return super().unlink()

class ReservationEvent(models.Model):
    _name = 'reservation.event.dashboard'
    _description = "Dashboard"
    _order = 'date_dash asc'

    color = fields.Integer(string='Color Index')
    name = fields.Char(string="Name")
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirmed'), ('reject', 'Rejected'),
                              ('available', 'Free'),('seats', 'Seat')
                              ], string='State', track_visibility='onchange', default='draft', copy=False)
    number_of_draft = fields.Integer("Number of Draft",compute="compute_reservation")
    number_of_confirm = fields.Integer("Number of Confirmed",compute="compute_confirmed")
    number_of_reject = fields.Integer("Number of Confirmed",compute="compute_reject")
    number_of_free = fields.Integer("Number of Confirmed",compute="compute_free")
    seats = fields.Integer("Amount of Available",compute="compute_seats")
    total_seats = fields.Integer("Amount of Available",compute="compute_seats")
    total_seats_amount = fields.Integer("Amount of Seats")
    new_dash = fields.Char("New")
    date_dash = fields.Char("Date Dash")
    complete_name = fields.Char("Whole Sentence")
    inactive = fields.Boolean(default=False)
    draft_date = fields.Integer("Draft Counts")
    confirm_date = fields.Integer("Confirm Counts")
    free_date = fields.Integer("Free Counts")
    reject_date = fields.Integer("Reject Counts")
    auto_delete_reservation = fields.Char(compute="auto_remove_reservation")

    def auto_remove_reservation(self):
        reservations_id = self.env['reservation.event'].search([('inactive','=',False)])
        list_reservations_id = self.env['reservation.event']
        email_lists = []
        email_dict = {}
        for res in reservations_id:
            email_dict[res.booking_email+res.date_str] = list_reservations_id
        for res in reservations_id:
            email_dict[res.booking_email+res.date_str] += res

        for key, value in email_dict.items():
            if len(value) > 1:
                length = 1 - len(value)
                for rec in value[length:]:
                    # rec.make_archive()
                    rec.with_context(reser_delete=1).unlink()
        self.auto_delete_reservation = "True"






    def get_todaydate(self):
        today = ''
        if self._context.get('tz'):
            today = fields.Datetime.now().now(tz=pytz.timezone(request._context.get('tz'))).replace(
                microsecond=0).replace(tzinfo=None)
        else:
            today = fields.Datetime.now()
        return today

    def compute_seats(self):
        res = self.env['reservation.event'].search([('state', 'in', ['confirm','draft']),('inactive','=',False)])
        free_cancel = self.env['reservation.event'].search([('state', 'in', ['reject','available']),('inactive','=',False)])
        seat = self.env['ir.config_parameter'].sudo().get_param('website_calendar_booking.seats')
        dashboards = self.env['reservation.event.dashboard'].search([('new_dash', '=', False)])
        date_wise = {}
        date_draft = {}
        date_confirm = {}
        date_free = {}
        date_reject = {}
        date_list = []
        date_list_cancel = []
        # self.total_seats = seat
        print('seat',seat)
        no_of_person = 0
        today = self.get_todaydate()
        dashboards_new = self.env['reservation.event.dashboard'].search([('new_dash', '=', 'new'),('date_dash','<',str(today.date()))])
        if dashboards_new:
            for dn in dashboards_new:
                dn.inactive = True
                dn.seats = int(seat)
                dn.total_seats = int(seat)
                print("line701",int(seat))
                _logger.info("line701EE : %s" % (seat), exc_info=True)
        for rec in res:
            if fields.Datetime.to_datetime(rec.date_str).date() >= today.date():
                date_list.append(fields.Datetime.to_datetime(rec.date_str).date())
        for rec in free_cancel:
            if fields.Datetime.to_datetime(rec.date_str).date() >= today.date():
                date_list_cancel.append(fields.Datetime.to_datetime(rec.date_str).date())
        date_list = list(set(date_list))
        for dl in date_list:
            no_of_person = 0
            draft = 0
            confirm = 0
            for rec in res:
                if dl == fields.Datetime.to_datetime(rec.date_str).date():
                    no_of_person = no_of_person + int(rec.pax_person.name)
                    date_wise[dl] = no_of_person
                    if rec.state == 'confirm':
                        confirm = confirm + 1
                        date_confirm[dl]= confirm
                        if dl not in date_draft:
                            date_draft[dl] = 0
                    elif rec.state == 'draft':
                        if dl not in date_confirm:
                            date_confirm[dl] = 0
                        draft = draft + 1
                        date_draft[dl] = draft
        for dl in date_list_cancel:
            free = 0
            reject = 0
            for fc in free_cancel:
                if dl == fields.Datetime.to_datetime(fc.date_str).date():
                    no_of_person = no_of_person + int(fc.pax_person.name)
                    if dl not in date_wise:
                        date_wise[dl] = 0
                    if fc.state == 'reject':
                        reject = reject + 1
                        date_reject[dl]= reject
                    elif fc.state == 'available':
                        free = free + 1
                        date_free[dl] = free
        #display current today
        no_of_person = 0
        confirm_date = 0
        draft_date = 0
        free_date = 0
        reject_date = 0
        for rec in res:
            if fields.Datetime.to_datetime(rec.date_str).date() == today.date():
                no_of_person = no_of_person + int(rec.pax_person.name)
                if rec.state == 'draft':
                    draft_date = draft_date + 1
                elif rec.state == 'confirm':
                    confirm_date = confirm_date + 1
        for rec in free_cancel:
            if fields.Datetime.to_datetime(rec.date_str).date() == today.date():
                if rec.state == 'available':
                    free_date = free_date + 1
                elif rec.state == 'reject':
                    reject_date = reject_date + 1
        print("pax",no_of_person)
        for dash in dashboards:
            dash.complete_name = today.date().strftime("%A") +',' +str(today.date().day)+' '+today.date().strftime("%B")
            dash.total_seats = int(seat)
            dash.draft_date = draft_date
            dash.confirm_date = confirm_date
            dash.free_date = free_date
            dash.reject_date = reject_date
            dash.seats = int(seat) - no_of_person
            dash.total_seats_amount = int(seat) - no_of_person
        #display future
        for key,value in date_wise.items():
            seats_comp = int(seat) - date_wise[key]
            complete_name = key.strftime("%A") + ',' + str(key.day) + ' ' + key.strftime(
                "%B")
            dash_board_exists = self.env['reservation.event.dashboard'].search([('new_dash', '=', 'new'),('date_dash','=',str(key))])
            if dash_board_exists:
                dash_board_exists.complete_name = complete_name
                if key in date_confirm:
                    dash_board_exists.confirm_date = date_confirm[key]
                else:
                    dash_board_exists.confirm_date = 0
                if key in date_draft:
                    dash_board_exists.draft_date = date_draft[key]
                else:
                    dash_board_exists.draft_date = 0
                if key in date_free:
                    dash_board_exists.free_date = date_free[key]
                else:
                    dash_board_exists.free_date = 0
                if key in date_reject:
                    dash_board_exists.reject_date = date_reject[key]
                else:
                    dash_board_exists.reject_date = 0
                dash_board_exists.total_seats = int(seat)
                dash_board_exists.seats = seats_comp
                dash_board_exists.total_seats_amount = seats_comp
                print("line780",seats_comp)
                _logger.info("line780EE : %s" % (seats_comp), exc_info=True)
            else:
                print("line782", seats_comp)
                _logger.info("line782EE : %s" % (seats_comp), exc_info=True)

                rd = self.env['reservation.event.dashboard'].create({'name':'Seat',
                                                            'state':'seats',
                                                            'total_seats':int(seat),
                                                            'seats':seats_comp,
                                                            'total_seats_amount':seats_comp,
                                                            'new_dash':'new',
                                                            'date_dash':str(key),
                                                            'complete_name':complete_name,
                                                            'create_uid':1,
                                                            'color':0,
                                                            'draft_date':date_draft.get(key),
                                                            'confirm_date': date_confirm.get(key)
                                                            })
                print('rd',rd)

    def compute_free(self):
        res = self.env['reservation.event'].search([('state','=','available'),('inactive','=',False)])
        self.number_of_free = len(res)

    def compute_reservation(self):
        res = self.env['reservation.event'].search([('state','=','draft'),('inactive','=',False)])
        self.number_of_draft = len(res)

    def compute_reject(self):
        res = self.env['reservation.event'].search([('state','=','reject'),('inactive','=',False)])
        self.number_of_reject = len(res)

    def compute_confirmed(self):
        res = self.env['reservation.event'].search([('state','=','confirm'),('inactive','=',False)])
        self.number_of_confirm = len(res)

    def open_confirmed_action(self):
        action = self.env.ref('website_calendar_booking.action_reservationt_mgmnt').sudo().read()[0]
        action['domain'] = [('state', '=', 'confirm')]
        return action

    def open_reject_action(self):
        action = self.env.ref('website_calendar_booking.action_reservationt_mgmnt').sudo().read()[0]
        action['domain'] = [('state', '=', 'reject')]
        return action

    def open_available_action(self):
        action = self.env.ref('website_calendar_booking.action_reservationt_mgmnt').sudo().read()[0]
        action['domain'] = [('state', '=', 'available')]
        return action

    def open_datewise_action(self):
        action = self.env.ref('website_calendar_booking.action_reservationt_mgmnt').sudo().read()[0]
        today = self.get_todaydate()
        rec_date = fields.Datetime.to_datetime(self.date_dash).date()
        full_rec_start = str(rec_date) + ' 00:00:00'
        full_rec_end = str(rec_date)+' 23:59:59'

        if rec_date < today.date():
            if self._context.get('state') == 'draft':
                re = self.env['reservation.event'].search([('state', 'in', ['draft']),('inactive','=',False),('start','>=',today.date()),('start','<=',today.date())])
                action['domain'] = [('state', 'in', ['draft']),('inactive','=',False),('start','>=',today.date()),('start','<=',today.date())]
            elif self._context.get('state') == 'confirm':
                re = self.env['reservation.event'].search([('state', 'in', ['confirm']),('inactive','=',False),('start','>=',today.date()),('start','<=',today.date())])
                action['domain'] = [('state', 'in', ['confirm']),('inactive','=',False),('start','>=',today.date()),('start','<=',today.date())]
            elif self._context.get('state') == 'available':
                re = self.env['reservation.event'].search([('state', 'in', ['available']),('inactive','=',False),('start','>=',today.date()),('start','<=',today.date())])
                action['domain'] = [('state', 'in', ['available']),('inactive','=',False),('start','>=',today.date()),('start','<=',today.date())]
            elif self._context.get('state') == 'reject':
                re = self.env['reservation.event'].search([('state', 'in', ['reject']),('inactive','=',False),('start','>=',today.date()),('start','<=',today.date())])
                action['domain'] = [('state', 'in', ['reject']),('inactive','=',False),('start','>=',today.date()),('start','<=',today.date())]
        else:
            if self._context.get('state') == 'draft':
                re = self.env['reservation.event'].search([('state', 'in', ['draft']),('inactive','=',False),('date_str','>=',full_rec_start),('date_str','<=',full_rec_end)])
                action['domain'] = [('state', 'in', ['draft']),('inactive','=',False),('date_str','>=',full_rec_start),('date_str','<=',full_rec_end)]
            elif self._context.get('state') == 'confirm':
                re = self.env['reservation.event'].search([('date_str', 'in', ['confirm']),('inactive','=',False),('date_str','>=',full_rec_start),('date_str','<=',full_rec_end)])
                action['domain'] = [('state', 'in', ['confirm']),('inactive','=',False),('date_str','>=',full_rec_start),('date_str','<=',full_rec_end)]
            elif self._context.get('state') == 'available':
                re = self.env['reservation.event'].search([('state', 'in', ['available']),('inactive','=',False),('date_str','>=',full_rec_start),('date_str','<=',full_rec_end)])
                action['domain'] = [('state', 'in', ['available']),('inactive','=',False),('date_str','>=',full_rec_start),('date_str','<=',full_rec_end)]
            elif self._context.get('state') == 'reject':
                re = self.env['reservation.event'].search([('state', 'in', ['reject']),('inactive','=',False),('date_str','>=',full_rec_start),('date_str','<=',full_rec_end)])
                action['domain'] = [('state', 'in', ['reject']),('inactive','=',False),('date_str','>=',full_rec_start),('date_str','<=',full_rec_end)]
        return action

    def open_action(self):
        action = self.env.ref('website_calendar_booking.action_reservationt_mgmnt').sudo().read()[0]
        action['domain'] = [('state','=','draft')]
        # action['context'] = {
        #     'search_default_name': self.name,
        #     'default_name': self.name,
        # }
        return action
        # return {
        #     'name': _('Reservation Management'),
        #     'view_mode': 'form',
        #     'view_id': self.env.ref('website_calendar_booking.action_reservationt_mgmnt').id,
        #     'res_model': 'reservation.event',
        #     # 'context': "{'move_type':'out_invoice'}",
        #     'domain': [('state','in','draft')],
        #     'type': 'ir.actions.act_window',
        #     # 'res_id': self.account_move.id,
        # }


    def dashboard_sales_order_action_id(self):
        pass

    def dashboard_sales_action_id(self):
        pass

    def load_data(self):
        for rec in self.env['reservation.event'].search([]):
            self.name = rec.name