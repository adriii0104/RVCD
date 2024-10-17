odoo.define('odoo_pos_password_validation.pos_password', function (require) {
    "use strict";

    const models = require('point_of_sale.models');
    const PosModelSuper = models.Order;

    models.Order = models.Order.extend({
        async remove_order() {
            const password = prompt("Introduce la contraseña para eliminar la orden:");
            if (password) {
                try {
                    await this.rpc({
                        model: 'pos.order',
                        method: 'action_delete_order',
                        args: [password],
                    });
                } catch (error) {
                    alert("Contraseña incorrecta");
                }
            }
        },

        async update_product_qty(product, qty) {
            const password = prompt("Introduce la contraseña para modificar la cantidad:");
            if (password) {
                try {
                    await this.rpc({
                        model: 'pos.order',
                        method: 'action_update_product_qty',
                        args: [product.id, qty, password],
                    });
                } catch (error) {
                    alert("Contraseña incorrecta");
                }
            }
        },
    });
});
