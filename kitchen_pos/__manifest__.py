# -*- coding: utf-8 -*-
{
    'name': 'Kitchen POS',
    'version': '14.0.1.0.0',
    'summary': 'Kitchen POS',
    'description': 'Kitchen POS',
    'category': 'All',
    'author': 'Bojan Anchev',
    'depends': ['base', 'web', 'point_of_sale', 'pos_restaurant', 'pos_combo'],
    'data': [
        # security
        'security/ir.model.access.csv',
        # data
        'data/doneness.xml',
        'data/serve_as.xml',
        'data/kitchen_order.xml',
        'data/data.xml',
        # views
        'views/assets.xml',
        'views/kitchen_pos.xml',
        'views/product.xml',
        'views/pos_order.xml',
        'views/groups.xml'
    ],
    'qweb': [
        'static/src/xml/kitchen.xml',
        'static/src/xml/pos_combo.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False
}
