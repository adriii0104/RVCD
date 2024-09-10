/** @odoo-module */
import { Order } from "@point_of_sale/app/store/models";
import { patch } from "@web/core/utils/patch";

patch(Order.prototype, {
    setup(_defaultObj, options) {
        super.setup(...arguments);
        this.to_invoice = true;
    },
    set_to_invoice(to_invoice) {
        this.assert_editable();
        this.to_invoice = 1;
    },
});
