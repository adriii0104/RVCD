{
    'name': '  Print Receipt POS',
    'version': '1.0',
    'category': 'Point of Sale',
    'summary': 'Custom module for adding custom button to POS',
    'description': """
    This module adds a custom button to the POS product screen.
    """,
    'depends': ['point_of_sale'],
    'assets': {
        'point_of_sale._assets_pos': [
            # Incluye tu archivo JS aquí
            'pre_account_customer/static/src/js/pos_create_button.js',
            'pre_account_customer/static/src/xml/pos_button_templates.xml',  # Incluye tu archivo XML aquí
            'pre_account_customer/static/src/xml/pso_new_order.xml',
            'pre_account_customer/static/src/js/pos_new_order.js'
        ],
    },
    'controllers': [
        'controllers/api.py',  # Your Python controller
    ],
    'installable': True,
    'application': False,
}
