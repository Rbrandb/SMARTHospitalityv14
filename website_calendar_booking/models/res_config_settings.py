# -*- coding: utf-8 -*-

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    module_allow_auto_validation = fields.Boolean(string='Allow Auto Validation')
    module_allow_auto_mail = fields.Boolean(string='Auto Mail')
    module_allow_auto_reminder = fields.Boolean(string='Auto Reminder')
    day = fields.Integer("Day")
    time = fields.Float("Time")
    allow_seats = fields.Boolean("Total Seats")
    seats = fields.Integer("Total Seats")
    allow_buffer = fields.Boolean("Place Buffer Time Frame")
    buffer = fields.Float("Buffer Time Frame")

    def set_values(self):
        """employee setting field values"""
        res = super().set_values()
        self.env['ir.config_parameter'].set_param('website_calendar_booking.module_allow_auto_validation', self.module_allow_auto_validation)
        self.env['ir.config_parameter'].set_param('website_calendar_booking.module_allow_auto_mail', self.module_allow_auto_mail)
        self.env['ir.config_parameter'].set_param('website_calendar_booking.module_allow_auto_reminder', self.module_allow_auto_reminder)
        self.env['ir.config_parameter'].set_param('website_calendar_booking.allow_buffer', self.allow_buffer)
        self.env['ir.config_parameter'].set_param('website_calendar_booking.buffer', self.buffer)
        self.env['ir.config_parameter'].set_param('website_calendar_booking.allow_seats', self.allow_seats)
        self.env['ir.config_parameter'].set_param('website_calendar_booking.day', self.day)
        self.env['ir.config_parameter'].set_param('website_calendar_booking.time', self.time)
        self.env['ir.config_parameter'].set_param('website_calendar_booking.seats', self.seats)
        return res

    def get_values(self):
        """employee limit getting field values"""
        res = super().get_values()
        value = self.env['ir.config_parameter'].sudo().get_param('website_calendar_booking.module_allow_auto_validation')
        value2 = self.env['ir.config_parameter'].sudo().get_param('website_calendar_booking.module_allow_auto_mail')
        value3 = self.env['ir.config_parameter'].sudo().get_param('website_calendar_booking.module_allow_auto_reminder')
        allow_buffer = self.env['ir.config_parameter'].sudo().get_param('website_calendar_booking.allow_buffer')
        allow_seats = self.env['ir.config_parameter'].sudo().get_param('website_calendar_booking.allow_seats')
        buffer = self.env['ir.config_parameter'].sudo().get_param('website_calendar_booking.buffer')
        value4 = self.env['ir.config_parameter'].sudo().get_param('website_calendar_booking.day')
        value5 = self.env['ir.config_parameter'].sudo().get_param('website_calendar_booking.time')
        seats = self.env['ir.config_parameter'].sudo().get_param('website_calendar_booking.seats')
        res.update(
            {
                'module_allow_auto_validation':value,
                'module_allow_auto_mail':value2,
                'module_allow_auto_reminder':value3,
                'allow_buffer':allow_buffer,
                'allow_seats':allow_seats,
                'buffer':buffer,
                'day':value4,
                'time':value5,
                'seats':seats,
             }
        )
        return res
