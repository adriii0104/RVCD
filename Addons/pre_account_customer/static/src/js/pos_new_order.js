/** @odoo-module */

import { Component } from "@odoo/owl";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { usePos } from "@point_of_sale/app/store/pos_hook";

export class ProductCombosButton extends Component {
    static template = "custom_pos_screen.nwacc";

    setup() {
        this.pos = usePos();
    }

    // Evento de clic en el botón
    async click() {
        this.pos.add_new_order(); // Crea una nueva orden
        this.pos.showScreen('ProductScreen'); // Muestra la pantalla de productos
    }
}

// Agrega el botón de combos al ProductScreen
ProductScreen.addControlButton({
    component: ProductCombosButton,
    condition: function () {
        return true; // Condición para mostrar el botón; ajustar según sea necesario
    },
});
