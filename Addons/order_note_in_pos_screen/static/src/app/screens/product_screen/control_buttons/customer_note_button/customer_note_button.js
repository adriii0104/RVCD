/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { ProductScreen } from "@point_of_sale/app/screens/product_screen/product_screen";
import { useService } from "@web/core/utils/hooks";
import { TextAreaPopup } from "@point_of_sale/app/utils/input_popups/textarea_popup";
import { Component } from "@odoo/owl";
import { usePos } from "@point_of_sale/app/store/pos_hook";

// Define the component for the note button
export class OrderNoteButton extends Component {
    static template = "order_note_in_pos_screen.OrderNoteButton";

    setup() {
        this.pos = usePos();
        this.popup = useService("popup");
    }

    async onClick() {
        const currentOrder = this.pos.get_order();
        if (!currentOrder) return;

        const { confirmed, payload: inputNote } = await this.popup.add(TextAreaPopup, {
            startingValue: currentOrder.note || "",
            title: _t("Add Order Note"),
        });

        if (confirmed) {
            currentOrder.set_order_note(inputNote); // Update the note locally
        }
    }
}

// Add the button to the product screen
ProductScreen.addControlButton({
    component: OrderNoteButton,
});