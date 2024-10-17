{
    'name': 'POS Floor Access Control',
    'version': '1.0',
    'category': 'Point of Sale',
    'summary': 'Control POS access based on assigned floors to users',
    'description': """
    This module allows assigning specific floors to users, restricting their access to POS sessions only on those floors.
    """,
    'depends': ['point_of_sale'],
    'data': [
        'views/pos_floor_views.xml',
    ],
    'installable': True,
    'application': False,
}
