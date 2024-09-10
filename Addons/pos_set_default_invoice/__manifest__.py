# -*- coding: utf-8 -*-
{
    'name': "Point Of Sale Default Invoice Set",
    'summary': """set invoice by default in pos""",
    'description': """
        set invoice by default in pos
        it makes invoice compulsory, and dosen't allows to unselect it.
    """,
    "author": "Alhaditech",
    "website": "www.alhaditech.com",
    'license': 'OPL-1',
    'images': ['static/description/cover.png'],
    'category': 'Invoicing',
    'version': '17.1.0',
    'depends': ['point_of_sale'],
    'data': [
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_set_default_invoice/static/src/js/models.js',
        ],
    },

}
