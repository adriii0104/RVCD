{
    'name': 'POS Order Password Validation',
    'version': '1.0',
    'category': 'Point of Sale',
    'summary': 'Permite a los administradores eliminar órdenes y modificar cantidades solo si son disminuciones.',
    'description': """
        Este módulo agrega validación de contraseña para la eliminación de órdenes en el POS.
        Solo los usuarios administradores pueden eliminar órdenes y modificar cantidades.
    """,
    'author': 'Codeando',
    'website': 'codeando.com.do',
    'depends': ['point_of_sale'],
    'data': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
