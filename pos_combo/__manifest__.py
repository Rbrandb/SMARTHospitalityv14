{
    'name': "POS Combo in Odoo",

    'summary': """
        This module is used to offering several products for sale as one combined product in POS.""",

    'description': """""",

    'author': "Jawaid Iqbal",
    'website': "https://www.linkedin.com/in/muhammad-jawaid-iqbal-659a6898/",

    'category': 'Point of Sale',
    'version': '14.0.1.6',

    'depends': ['base', 'point_of_sale', 'pos_restaurant'],

    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    'qweb': ['static/src/xml/pos_combo.xml'],
}
