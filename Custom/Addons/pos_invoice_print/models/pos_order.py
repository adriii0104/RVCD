from odoo import models, api
import logging
from escpos.printer import Network

_logger = logging.getLogger(__name__)

class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.model
    def create_from_ui(self, orders, draft=False):
        res = super(PosOrder, self).create_from_ui(orders, draft=draft)
        if not draft:
            for order_data in res:
                pos_order = self.env['pos.order'].browse(order_data['id'])
                invoice = pos_order.account_move
                if invoice:
                    invoice_summary = self._create_invoice_summary(invoice)
                    print(invoice_summary)
        return res

    def _create_invoice_summary(self, invoice):
        try:
            replace_prefix_with_name = self.replace_prefix_with_name(
                invoice.l10n_latam_document_number)

            # Format invoice lines
            bold_on = chr(27) + chr(69) + chr(1)
            bold_off = chr(27) + chr(69) + chr(0)
            lines = []
            for line in invoice.invoice_line_ids:
                line_data = {
                    'Product': line.product_id.name[:15] if len(line.product_id.name) > 15 else line.product_id.name,
                    'Quantity': line.quantity,
                    'Unit Price': line.price_unit,
                    'Total': line.price_total,
                }
                lines.append(line_data)

            # Create a string representation
            if invoice.partner_id.name == 'Factura de Consumo':
                result = ''
            elif isinstance(invoice.partner_id.vat, str) and len(invoice.partner_id.vat) == 9:
                result = f'Razón Social: {invoice.partner_id.name}'
            elif isinstance(invoice.partner_id.vat, str) and len(invoice.partner_id.vat) == 11:
                result = f'Nombre: {invoice.partner_id.name}'

            summary_str = f"""
                REVEL BAR & KITCHEN
            Calle Virgilio Díaz Ordóñez
      Santo Domingo Este, Distrito Nacional 10130
        	  RNC: 132477332
            Teléfono: +1 809-870-0606
            Fecha Emisión: {invoice.invoice_date}
  
{'-'*48}
              {replace_prefix_with_name}
{'-'*48}
NCF: {invoice.l10n_latam_document_number}   
Válida hasta: 31/12/2025
Vence: {invoice.invoice_date}
{f'Cédula: {invoice.partner_id.vat}' if isinstance(invoice.partner_id.vat, str) and len(invoice.partner_id.vat) == 11 else f'RNC: {invoice.partner_id.vat}' if isinstance(invoice.partner_id.vat, str) and len(invoice.partner_id.vat) == 9 else '' }
{result}
{'-'*48}
Descripción{' '*10}Cantidad{' '*10}Importe \n
{'-'*48}
"""
            for line in lines:
                summary_str += f"{str(line['Product']).ljust(25)}{str(line['Quantity']).ljust(10)}{str(line['Total']).rjust(10)}\n"

            # Calculate tax and total
            amount_untaxed = invoice.amount_untaxed
            tax_amount = amount_untaxed * 0.18  # Assuming 18% ITBIS
            tip_amount = amount_untaxed * 0.10  # Assuming 10% Tip
            total = amount_untaxed + tax_amount + tip_amount

            summary_str += f"""
{'-'*48}
Importe sin impuestos:             RD$ {amount_untaxed:,.2f}
18% ITBIS:                         RD$ {tax_amount:,.2f}
10% Propina:                       RD$ {tip_amount:,.2f}

{'-'*48}
{bold_on}TOTAL:                             RD$ {total:,.2f}{bold_off}
            
            
            ¡Gracias por preferirnos!
            """

            # Uncomment the following lines to print to a network printer
            printer_ip = '192.168.100.110'
            printer_port = 9100
            printer = Network(printer_ip, printer_port)
            printer.text(summary_str)
            printer.cut()
            printer.close()
            print(summary_str)

            return summary_str

        except Exception as e:
            _logger.error(
                f"Error creating invoice summary for invoice {invoice.id}: {e}")
            return "Error creating invoice summary."

    def replace_prefix_with_name(self, sequence):
        # Define the mapping of prefixes to names
        prefix_mapping = {
            'B01': 'Factura de Crédito Fiscal',
            'B02': 'Factura de Consumo',
            'B03': 'Nota de Débito',
            'B04': 'Nota de Crédito',
            'B05': 'Único Ingreso',
            'B06': 'Régimen Especial',
            'B07': 'Factura Gubernamental',
            'B08': 'Factura de Exportación'
        }

        # Extract the prefix from the sequence (first 3 characters)
        prefix = sequence[:3] if sequence else ''
        # Extract the rest of the sequence
        rest_of_sequence = sequence[3:] if sequence else ''

        # Get the name corresponding to the prefix
        name = prefix_mapping.get(prefix, 'Unknown')

        # Return the formatted string
        return f"{name}"
