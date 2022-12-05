# -*- coding: utf-8 -*-
from odoo.http import request

from odoo import api, fields, models,_

class TableEventEmail(models.Model):

    _name = "table.event"

    name = fields.Char(string="Table #")


    _sql_constraints = [
        ('table_event_uniq', 'unique(name)', _('This name is already exist.'))
    ]

class TableTimeSlot(models.Model):
    _name = 'table.time.slot'

    # name = fields.Many2one('table.event',string="Table")
    time_slot = fields.Many2one('time.slot.event',string="Time Slot")
    state = fields.Selection([('Available','Available'),('Booked',"Booked")],string="Status",default='Available')
    check_status = fields.Char(compute="compute_status")
    date_time = fields.Datetime("Date Time",default=fields.Datetime.now)

    # _sql_constraints = [
    #     ('table_time_slot_uniq', 'unique(time_slot,name)', _('This time slot already is already placed for this table.'))
    # ]

    def compute_status(self):
        for dates in self:
            if not dates.date_time.date() == fields.Datetime.now().date():
                dates.state = 'Available'
                dates.check_status = dates.date_time
                dates.date_time = fields.Datetime.now()
            else:
                dates.check_status = dates.date_time

    def name_get(self):
        """Return: [(id, start_time-end_time)],
            e.g-[(1, 1:00-3:00)]"""
        result = []
        for rec in self:
            name = rec.name.name+'('+rec.time_slot.float_convert_in_time(rec.time_slot.name)+')'#+'-'+rec.time_slot.float_convert_in_time(rec.time_slot.lname) +')'
            result.append((rec.id, name))
        return result

