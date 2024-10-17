/** @odoo-module */

import { Component } from "@odoo/owl";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { usePos } from "@point_of_sale/app/store/pos_hook";

export class ProductCombosButton extends Component {
    static template = "custom_pos_screen.ProductCombosButton";

    setup() {
        this.pos = usePos();
    }

    // Función para obtener detalles del cliente
    getPartnerDetails() {
        const partner = this.pos.get_order().get_partner();
        if (!partner) {
            throw new Error("Please select a customer before proceeding with the order.");
        }
        return partner.name || "Unknown";
    }

    // Función para obtener detalles de la orden
    getOrderDetails() {
        const order = this.pos.get_order();

        console.log(Object.getOwnPropertyNames(order));
    
        // Imprime el prototipo del objeto para ver los métodos heredados
        console.log(Object.getOwnPropertyNames(Object.getPrototypeOf(order)));

        return {
            cashier: order.cashier.name || "Unknown",
            table: order.getTable().name ? order.getTable().name || "No Table" : "No Table",  // Incluye la mesa actual
            orderLines: order.get_orderlines().map(line => ({
                product: line.get_product().display_name,
                quantity: line.get_quantity(),
                priceUnit: line.get_unit_price(),
                subtotal: line.get_price_with_tax(),
            })),
            total: order.get_total_with_tax(),
            tax: order.get_total_tax(),
            paymentLines: order.get_paymentlines().map(payment => ({
                method: payment.get_payment_method().name,
                amount: payment.get_amount(),
            })),
        };
    }

    // Función para enviar los datos al servidor
    async sendOrderToServer(data) {
        const response = await fetch('/pos/send_order', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data),
        });

        if (!response.ok) {
            throw new Error(`Failed to send order to the server. Status: ${response.status}`);
        }

        return await response.json();
    }

    // Evento de clic en el botón
    async click() {
        try {
            const partnerName = this.getPartnerDetails();
            const orderDetails = this.getOrderDetails();

            // Consolida los datos que se van a enviar
            const dataToSend = {
                table: orderDetails.table,
                cashier: orderDetails.cashier,
                partner_name: partnerName,
                total: orderDetails.total,
                tax: orderDetails.tax,
                order_lines: orderDetails.orderLines,
                payment_lines: orderDetails.paymentLines,
                corin: 'corin' // Añadir cualquier otro campo necesario
            };

            console.log('Sending order data to server:', dataToSend);

            // Envía los datos al servidor
            const result = await this.sendOrderToServer(dataToSend);

            if (result.success) {
                console.log('Order successfully sent to the server.');
            } else {
                console.error('Failed to send order to the server.', result);
            }
        } catch (error) {
            console.error("Error processing order:", error.message || error);
        }
    }
}

// Agrega el botón de combos al ProductScreen
ProductScreen.addControlButton({
    component: ProductCombosButton,
    condition: function () {
        return true;
    },
});
