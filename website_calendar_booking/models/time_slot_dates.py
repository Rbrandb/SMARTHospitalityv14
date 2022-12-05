# -*- coding: utf-8 -*-
from odoo.http import request

from odoo import api, fields, models,_
from odoo.exceptions import UserError

import math

class TimeslotDatesEventEmail(models.Model):

    _name = 'time.slot.date'

    sequence = fields.Integer(help="Determine the display order", default=1)
    name = fields.Float(string="Start Time")
    date = fields.Date("Date")
    slots = fields.Integer("Number of Slots Per day")
    slots_left = fields.Integer("Number of Slots left")
    seats_left = fields.Integer("Seats Left")
    type = fields.Selection([('Lunch',"Lunch"),
                             ('Dinner',"Dinner"),
                             ('Breakfast',"Breakfast")
                             ],string="Type")
    days = fields.Many2one('time.days',string="Day/Days")
    share_slot = fields.Many2one('time.slot.share',strong="Share Slot")
    day_type = fields.Selection([('am', "am"),
                             ('pm', "pm")
                             ], string="Day Type")
    mark_invisible = fields.Boolean("Dont Show on Website")
    complete_name = fields.Char("Full Name")
    reservation_id = fields.Many2one('reservation.event',string="Reservation")
    time_slot = fields.Many2one('time.slot.event',string="Time Slot")
    time_slot_off = fields.Many2one('time.slot.event',string="Time Slot")

    _sql_constraints = [
        ('time_slot_event_uniq', 'slots_left>slots', _('The Slot is not free now.'))
    ]

    @api.onchange('slots')
    def onchange_slots(self):
        self.slots_left = self.slots

    def float_convert_in_time(self, float_val):
        """Convert any float value in 24 hrs time formate."""
        if float_val < 0:
            float_val = abs(float_val)
        hour = math.floor(float_val)
        min = round((float_val % 1) * 60)
        if min == 60:
            min = 0
            hour = hour + 1
        time = str(hour).zfill(2) + ":" + str(min).zfill(2)
        return time

    def time_convert_in_float(self, time_val):
        """Convert any 24 hrs time fomate value in float."""
        factor = 1;
        if time_val[0] == '-':
            time_val = time_val[1:]
            factor = -1
        float_time_pair = time_val.split(":")
        if len(float_time_pair) != 2:
            return factor*float(time_val)
        hours = int(float_time_pair[0])
        minutes = int(float_time_pair[1])
        return factor * round((hours + (minutes / 60)),2)

    def name_get(self):
        """Return: [(id, start_time-end_time)],
            e.g-[(1, 1:00-3:00)]"""
        result = []
        day_name = ''
        for rec in self:
            day_name = ''
            for day in rec.days:
                day_name += day.name+','

            name = self.float_convert_in_time(rec.name)+' '+day_name #+ '-' + self.float_convert_in_time(rec.lname)
            rec.complete_name = name
            result.append((rec.id, name))
        return result

