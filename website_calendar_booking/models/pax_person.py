# -*- coding: utf-8 -*-
from odoo.http import request

from odoo import api, fields, models

class PAXPerson(models.Model):

    _name = 'pax.person'

    name = fields.Char("Number of Persons")