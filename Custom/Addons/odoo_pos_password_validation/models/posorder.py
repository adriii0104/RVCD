from odoo import models, api
from odoo.exceptions import UserError

class PosOrder(models.Model):
    _inherit = 'pos.order'

    def _check_password(self, password):
        """ Verificar si la contraseña es correcta """
        correct_password = self.env['ir.config_parameter'].sudo().get_param('pos_order_password')
        if password != correct_password:
            raise UserError("Contraseña incorrecta.")

    def action_delete_order(self, password):
        """ Eliminar una orden con validación de contraseña """
        self._check_password(password)
        return super(PosOrder, self).unlink()

    def action_update_product_qty(self, product_id, new_qty, password):
        """ Actualizar la cantidad de un producto con validación de contraseña """
        self._check_password(password)
        order_line = self.env['pos.order.line'].search([('order_id', '=', self.id), ('product_id', '=', product_id)])
        if order_line:
            order_line.qty = new_qty
        else:
            raise UserError("El producto no se encuentra en la orden.")
