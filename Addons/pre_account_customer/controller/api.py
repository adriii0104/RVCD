from odoo import http
from odoo.http import request
import json
from datetime import datetime
from escpos.printer import Network


class PosCustomController(http.Controller):

    @http.route('/pos/send_order', type='http', auth='user', methods=['POST'], csrf=False)
    def receive_order(self, **kwargs):
        try:
            # Obtener el contenido del cuerpo de la solicitud
            data = request.httprequest.get_data(as_text=True)

            # Convertir el cuerpo en un diccionario Python
            json_data = json.loads(data)

            # Extraer los datos del JSON
            table = json_data.get('table')
            cashier = json_data.get('cashier')
            partner_name = json_data.get('partner_name')
            total = json_data.get('total')
            tax = json_data.get('tax')
            order_lines = json_data.get('order_lines')
            payment_lines = json_data.get('payment_lines')

            # Imprimir los datos recibidos
            print("Received Order Data:")
            print(
                f"Cashier: {cashier}, Partner: {partner_name}, Total: {total}, Tax: {tax}")
            print(f"Order Lines: {order_lines}")
            print(f"Payment Lines: {payment_lines}")

            if order_lines:
                for line in order_lines:
                    print(
                        f"Product: {line.get('product', 'Unknown')}, Quantity: {line.get('quantity', 0)}, Price: {float(line.get('price', 0)):.2f}")

            generate_summary_string = self.generate_summary_string(
                order_lines, cashier, partner_name, total, tax, table)

            # Retornar respuesta de éxito
            return json.dumps({
                'success': True,
                'message': 'Order received successfully!'
            })

        except Exception as e:
            # Manejo de errores
            return json.dumps({
                'success': False,
                'error': str(e),
            })

    def generate_summary_string(self, lines, cashier, partner_name, total, tax, table):
        # Create a string representation of the summary

        bold_on = chr(27) + chr(69) + chr(1)
        bold_off = chr(27) + chr(69) + chr(0)
        summary_str = f"""
               REVEL BAR & KITCHEN
           Calle Virgilio Díaz Ordóñez
    Santo Domingo este Distrito Nacional 10130
               RNC: 132477332
           Teléfono: +1 809-870-0606
          Fecha: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}
{'-'*50}
                   PRECUENTA
{'-'*50}
Descripción{' '*10}Cantidad{' '*10}Importe
{'-'*50}
"""
    # Adding product lines to the summary
        for line in lines:
            summary_str += f"{str(line['product']).ljust(25)}{str(line['quantity']).ljust(10)}{str(line['subtotal']).rjust(10)}\n"

        # Calculate amounts (assuming you are receiving untaxed amount and adding tax + tip)
        amount_untaxed = total - tax
        tax_amount = tax  # Assuming tax is sent correctly
        tip_amount = amount_untaxed * 0.10  # Assuming 10% tip
        total_with_tip = total + tip_amount

        # Adding total amounts to the summary
        summary_str += f"""
{'-'*50}
{'-'*50}
Importe sin impuestos:             RD$ {amount_untaxed:.2f}
18% ITBIS:                         RD$ {tax_amount:.2f}
10% Propina:                       RD$ {tip_amount:.2f}

{'-'*50}
{bold_on}Total:                             RD$ {total_with_tip:.2f}{bold_off}
{'-'*50}
Centro de Venta: Revel Bar & Kitchen
Cliente : {partner_name}
MESA: {table}
Cajero: {cashier}
{'-'*50}

Tipo NCF: {'_'*25}

RNC: {'_'*25}

NOMBRE: {'_'*25}
    """

        print(summary_str)
        # Uncomment the following lines to print to a network printer
        # printer_ip = '192.168.100.110'
        # printer_port = 9100
        # printer = Network(printer_ip, printer_port)
        # printer.text(summary_str)
        # printer.cut()
        # printer.close()
