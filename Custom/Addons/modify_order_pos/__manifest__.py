{
    'name': 'Modify Order POS',
    'version': '1.0',
    'category': 'Point of Sale',
    'summary': 'Modify the order in POS',
    'description': """
    Restrict order modification in POS
    """,
    'data': [
        'security/ir.model.access.csv',
        'views/pos_order.xml',
    ],
    'depends': ['point_of_sale'],
    'installable': True,
    'auto_install': False,
    'application': False,
}