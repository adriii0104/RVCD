{
    'name': 'POS Order Password Validation',
    'version': '1.0',
    'category': 'Point of Sale',
    'summary': 'Require password to delete or modify POS orders and product quantities',
    'author': 'Codeando SRL',
    'depends': ['point_of_sale'],
    'data': [
        'views/pos_templates.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'odoo_pos_password_validation/static/src/js/pos_password.js',  # Ruta al archivo JS
        ],
    },
    'qweb': ['static/src/xml/pos_password.xml'],
    'installable': True,
    'application': False,
}
