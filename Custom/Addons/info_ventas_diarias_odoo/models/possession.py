from odoo import models, fields, api
import logging
from datetime import datetime
from escpos.printer import Network
import smtplib
from email.mime.text import MIMEText

_logger = logging.getLogger(__name__)

class PosConfig(models.Model):
    _inherit = 'pos.config'

    def action_print_totals_kanban(self):
        # Inicializar variables
        totals_by_employee = {}
        product_details = {}
        category_totals = {}
        total_company_sales = 0
        total_payment_methods = {}
        payment_counts = {}
        total_itbis = 0
        initial_balance = 0
        final_balance = 0

        # Usuario que solicita el reporte y fecha actual
        user = self.env.user
        current_date = datetime.now().strftime('%Y-%m-%d')

        # Obtener la sesión actual
        current_session = self.current_session_id
        if not current_session or current_session.state != 'opened':
            current_session = self.env['pos.session'].search(
                [('config_id', '=', self.id), ('state', '=', 'closed')], 
                order='stop_at desc', limit=1
            )

        if not current_session:
            _logger.warning("No se encontraron sesiones actuales o pasadas.")
            return  # No hay sesión para procesar

        # Saldo inicial
        initial_balance = current_session.cash_register_balance_start or 0

        # Órdenes de la sesión
        orders = self.env['pos.order'].search([('session_id', '=', current_session.id)])

        # Iterar sobre las órdenes
        for order in orders:
            employee = order.employee_id
            if employee not in totals_by_employee:
                totals_by_employee[employee] = {
                    'total_sales': 0, 'payment_methods': {}, 'total_operations': 0,
                    'products': {}, 'cancelled': 0, 'product_units_sold': 0
                }

            total_itbis += order.amount_tax

            for line in order.lines:
                product_name = line.product_id.name
                category_name = line.product_id.categ_id.name

                # Actualizar detalles de producto por empleado
                totals_by_employee[employee]['products'].setdefault(product_name, {'quantity': 0, 'total': 0})
                totals_by_employee[employee]['products'][product_name]['quantity'] += line.qty
                totals_by_employee[employee]['products'][product_name]['total'] += line.price_subtotal_incl

                # Detalles generales de producto
                product_details.setdefault(product_name, {'quantity': 0, 'total': 0})
                product_details[product_name]['quantity'] += line.qty
                product_details[product_name]['total'] += line.price_subtotal_incl

                # Actualizar totales de categoría
                category_totals.setdefault(category_name, {'quantity': 0, 'total': 0})
                category_totals[category_name]['quantity'] += line.qty
                category_totals[category_name]['total'] += line.price_subtotal_incl

                # Actualizar unidades vendidas por empleado
                totals_by_employee[employee]['product_units_sold'] += line.qty

            for payment in order.payment_ids:
                payment_method = payment.payment_method_id.name
                totals_by_employee[employee]['payment_methods'].setdefault(payment_method, 0)
                totals_by_employee[employee]['payment_methods'][payment_method] += payment.amount
                totals_by_employee[employee]['total_sales'] += payment.amount
                totals_by_employee[employee]['total_operations'] += 1
                total_company_sales += payment.amount
                total_payment_methods.setdefault(payment_method, 0)
                total_payment_methods[payment_method] += payment.amount
                payment_counts.setdefault(payment_method, 0)
                payment_counts[payment_method] += 1

            # Actualizar saldo final
            final_balance += order.amount_total

            # Rastreo de cancelaciones
            if order.state == 'cancel':
                totals_by_employee[employee]['cancelled'] += order.amount_total

        # Formato del ticket
        bold_on = chr(27) + chr(69) + chr(1)
        bold_off = chr(27) + chr(69) + chr(0)

        ticket_text = f"""
----------------------------------------
        REVEL BAR & KITCHEN
----------------------------------------
Solicitado por: {user.name}
Fecha del Reporte: {current_date}


----------------------------------------
SALDO INICIAL:                 ${initial_balance:.2f}
----------------------------------------

Pagos Registrados:
"""
        for method, amount in total_payment_methods.items():
            count = payment_counts.get(method, 0)
            ticket_text += f"{method:<20} Cantidad: {count:<4} ${amount:,.2f}\n"

        ticket_text += f"""
----------------------------------------
SALDO FINAL:                   ${final_balance:.2f}
----------------------------------------

Total Ventas: ${total_company_sales:.2f}
Total ITBIS: ${total_itbis:.2f}
----------------------------------------
"""

        # Detalle de productos
        ticket_text += "DETALLE DE PRODUCTOS VENDIDOS:\n"
        ticket_text += "{:<15} {:<10} {:<10}\n".format("Nombre", "Cant", "Total")
        for product, details in product_details.items():
            ticket_text += "{:<15} {:<10.1f} ${:<10.2f}\n".format(product[:30], details['quantity'], details['total'])

        ticket_text += "\n----------------------------------------\n"

        # Totales de categorías de productos
        ticket_text += "{}DETALLE DE CATEGORÍAS DE PRODUCTOS VENDIDOS:{}\n".format(bold_on, bold_off)
        ticket_text += "{:<13} {:<10} {:<10}\n".format("Categoría", "Cant", "Total")
        for category, details in category_totals.items():
            ticket_text += "{}{:<13} {:<10.1f} ${:<10.2f}{}\n".format(bold_on, category[:30], details['quantity'], details['total'], bold_off)
        
        ticket_text += "\n----------------------------------------\n"

        # Pagos por Empleado (formato de recibo)
        ticket_text += "COBROS POR EMPLEADO:\n"
        ticket_text += "----------------------------------------\n"
        for employee, data in totals_by_employee.items():
            ticket_text += f"{bold_on}{employee.name}{bold_off}\n"
            for payment_method, amount in data['payment_methods'].items():
                ticket_text += "{}    {:<10} {:<5} ${:<10.2f}\n".format(bold_on,
                    payment_method[:10],
                    data['total_operations'],
                    amount,
                )
            ticket_text += "{}    Total {:<10} ${:<10.2f} {}\n".format(bold_on,
                data['total_operations'],
                data['total_sales'],
                bold_off
            )

        # Resumen por Empleado
        ticket_text += "----------------------------------------\n"
        ticket_text += "RESUMEN POR EMPLEADO:\n"
        ticket_text += "{:<20} {:<10} {:<10} {:<10}\n".format("Empleado", "Cancelados", "Ventas", "Total")
        for employee, data in totals_by_employee.items():
            ticket_text += "{:<20} ${:<10.2f} {:<10} ${:<10.2f}\n".format(
                employee.name,
                data['cancelled'],
                data['product_units_sold'],
                data['total_sales']
            )

        ticket_text += "----------------------------------------\n"
        ticket_text += "          FIN DEL INFORME\n"
        ticket_text += "----------------------------------------"

        # Imprimir el ticket
        print(ticket_text)
        # printer_ip = '192.168.100.110'
        # printer_port = 9100
        # printer = Network(printer_ip, printer_port)
        # printer.text(ticket_text)
        # printer.cut()
        # printer.close()

        # # Contenido del correo electrónico
        # email_content = ticket_text
        # report_sales(email_content)

# def report_sales(body_rec):
#     # Detalles del correo electrónico
#     sender_email = "reportsendrevel@outlook.com"
#     receiver_email = "adriii0104@hotmail.com"
#     subject = "Reporte de ventas"
#     body = body_rec
#     password = "revelbar2023"

#     # Enviar el correo electrónico usando SMTP
#     try:
#         with smtplib.SMTP("smtp-mail.outlook.com", 587) as server:
#             server.starttls()
#             server.login(sender_email, password)
#             server.sendmail(sender_email, receiver_email, body)
#         print("Correo enviado con éxito.")
#     except Exception as e:
#         print(f"Error al enviar el correo: {e}")
