from odoo import models, api, _
from odoo.exceptions import UserError

class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.model
    def unlink(self):
        """ Evita la eliminación de órdenes a menos que el usuario sea administrador """
        if not self.env.user.has_group('base.group_system'):  # Verifica si el usuario es administrador
            raise UserError("No tienes permisos para eliminar esta orden.")
        return super(PosOrder, self).unlink()

    def action_update_product_qty(self, product_id, new_qty):
        """ Permite modificar la cantidad de un producto en la orden solo si el nuevo valor es menor que el actual """
        if not self.env.user.has_group('base.group_system'):  # Verifica si el usuario es administrador
            raise UserError(_("No tienes permisos para modificar la cantidad de productos en la orden."))
        
        # Filtrar la línea de la orden que corresponde al producto
        order_line = self.order_line.filtered(lambda line: line.product_id.id == product_id)
        if not order_line:
            raise UserError(_("El producto no se encuentra en la orden."))

        # Verificar que la nueva cantidad sea menor que la actual
        if new_qty >= order_line.qty:
            raise UserError(_("Solo puedes restar cantidades a los productos en la orden."))

        # Lógica para modificar la cantidad
        order_line.qty = new_qty
