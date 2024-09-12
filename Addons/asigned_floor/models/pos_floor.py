from odoo import models, fields
from odoo.exceptions import ValidationError

class ResUsers(models.Model):
    _inherit = 'res.users'

    floor_ids = fields.Many2many('restaurant.floor', string='Assigned Floors')