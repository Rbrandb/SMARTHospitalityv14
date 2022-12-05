# -*- coding: utf-8 -*-
import logging
_logger = logging.getLogger(__name__)

from odoo import api, fields, models,_


class Company(models.Model):
    _inherit = 'res.company'

    managers = fields.Many2many('res.users',string="Managers")
