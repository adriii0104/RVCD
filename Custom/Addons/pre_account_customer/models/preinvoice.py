from odoo import models, fields

class PosOrder(models.Model):
    _inherit = 'pos.order'

    def get_order_details(self, order_id):
        order = self.browse(order_id)
        if order:
            
            print('\n\n\n\n\n\n, "READY TO PRINT RECEIPT" \n\n\n\n\n\n')
            return {
                'total': order.amount_total,
                'lines': [{'product': line.product_id.name, 'price': line.price_unit} for line in order.lines],
            }
        return {}
