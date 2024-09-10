from odoo import api, fields, models

class PosOrder(models.Model):
    _inherit = 'pos.order'

    # Add the note field to the pos.order model
    note = fields.Text(string='Note')

    @api.model
    def _order_fields(self, ui_order):
        result = super(PosOrder, self)._order_fields(ui_order)

        # Ensure the note field is included in the result
        if 'note' in ui_order:
            result['note'] = ui_order['note']
        else:
            # Fetch the existing order and get the note if available
            existing_order = self.search([('pos_reference', '=', ui_order.get('name'))], limit=1)
            if existing_order:
                result['note'] = existing_order.note or ''  # Ensure the note is set
            else:
                result['note'] = ''  # Default to empty if not found

        return result

    @api.model
    def create_from_ui(self, orders, draft=False):
        # Create orders from the UI and include the note field
        result = super(PosOrder, self).create_from_ui(orders, draft)
        for order in result:
            if 'note' in order:
                order.write({'note': order['note']})
        return result
