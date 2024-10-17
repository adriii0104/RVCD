from odoo import models, api, exceptions

class PosOrder(models.Model):
    _inherit = 'pos.order'

    def unlink(self):
        if not self.env.user.has_group('base.group_system'):
            raise exceptions.AccessError("You do not have the necessary permissions to delete this order.")
        return super(PosOrder, self).unlink()
