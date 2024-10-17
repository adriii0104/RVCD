/** @odoo-module **/

import { Order } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";

// Extend the Order model to handle notes
patch(Order.prototype, {
    export_as_JSON() {
        const json = super.export_as_JSON(...arguments);
        json.note = this.note || "";
        return json;
    },

    init_from_JSON(json) {
        super.init_from_JSON(...arguments);
        this.note = json.note || "";
    },

    export_for_printing() {
        const result = super.export_for_printing(...arguments);
        result.note = this.note || "";
        return result;
    },

    set_order_note(note) {
        this.note = note;
        // Notify POS to persist changes (update the local state)
    }
});
