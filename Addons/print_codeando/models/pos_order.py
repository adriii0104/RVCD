from odoo import models, fields, api
import logging
from odoo.exceptions import UserError
from escpos.printer import Network

_logger = logging.getLogger(__name__)


class PosOrder(models.Model):
    _inherit = 'pos.order'

    # Diccionario para almacenar las cantidades previas por mesa y producto
    order_quantities = {}

    def create(self, vals):
        _logger.info('Creating order...')
        res = super(PosOrder, self).create(vals)
        
        
        print(type(res))
        # is_update=False para nueva orden
        self.print_order_by_category(res, is_update=False)
        return res

    def write(self, vals):
        _logger.info('Updating order...')
        res = super(PosOrder, self).write(vals)
        for order in self:
            # is_update=True para modificaciones
            self.print_order_by_category(order, is_update=True)
        return res

    def print_order_by_category(self, order, is_update=False):
        _logger.info('Processing order by category...')
        order_lines_by_category = {}
        table_id = order.table_id.id

        if table_id not in self.order_quantities:
            self.order_quantities[table_id] = {}

        # Define los IDs y sus nombres
        category_names = {22: 'COCINA', 21: 'BAR'}

        # Agrupar líneas de pedido por categoría y manejar cantidades
        for line in order.lines:
            product_id = line.product_id.id
            category_id = line.product_id.categ_id.id

            if category_id not in order_lines_by_category:
                order_lines_by_category[category_id] = []

            # Obtener la cantidad previa y la cantidad actual
            previous_qty = self.order_quantities[table_id].get(product_id, 0)
            current_qty = line.qty
            qty_change = current_qty - previous_qty

            # Actualizar el diccionario con la nueva cantidad
            self.order_quantities[table_id][product_id] = current_qty

            # Agregar la línea con el cambio de cantidad
            if qty_change != 0:
                order_lines_by_category[category_id].append({
                    'product_name': line.product_id.display_name + ' ' + f" - Nota cliente: ({line.customer_note})" if line.customer_note else line.product_id.display_name,
                    'qty_change': qty_change,
                    'current_qty': current_qty
                })

        # Recorrer las categorías y enviar a imprimir
        for category_id, lines in order_lines_by_category.items():
            if category_id in category_names:
                _logger.info(
                    f"Category {category_names[category_id]} detected with ID {category_id}.")
                receipt = self.generate_receipt(
                    lines, order.table_id.name, order.user_id.name, is_update, category_names[category_id])

    def generate_receipt(self, order_lines, table, user, is_update, category):
        now = fields.Datetime.now()
        formatted_date = now.strftime('%d/%m/%Y')
        formatted_time = now.strftime('%H:%M:%S')

        # Verificar si hay líneas de pedido
        if not order_lines:
            _logger.warning("No order lines found for receipt generation.")
            return "<html><body><p>No items to print.</p></body></html>"

        receipt_lines = []

        for line in order_lines:
            product_name = line['product_name']
            qty_change = line['qty_change']

            if qty_change > 0:
                receipt_lines.append(f"{product_name}: +{qty_change}")
            elif qty_change < 0:
                receipt_lines.append(f"{product_name}: {qty_change}")

        lines = "\n".join(receipt_lines)
        update_text = " (Update)" if is_update else ""

        # Configurar impresoras según la categoría
        if category == 'BAR':
            # printer_ip = '192.168.100.111'
            pass
        elif category == 'COCINA':
            # printer_ip = '192.168.100.112'
            pass
        else:
            _logger.warning(f"No printer configured for category: {category}")
            return

        printer_port = 9100
        # printer = Network(printer_ip, printer_port)

        # Texto formateado basado en el HTML proporcionado
        receipt_text = f"""
********************************
             {category}
--------------------------------

MESA: {table}

--------------------------------

CAMARERO: {user}
FECHA:  {formatted_date} {formatted_time} {update_text}

********************************

{lines}

********************************
Revel Bar & Kitchen
********************************
"""
        print(receipt_text)
        # # Imprime el texto
        printer.text(receipt_text)
        printer.cut()
        printer.close()
