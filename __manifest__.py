# -*- coding: utf-8 -*-
{
    'name': "Basic Accounting",

    'summary': """
        Basic Accounting for households""",

    'description': """
        Since Odoo Community is a free platform, you are not limited to use it for a business purposes only.
        I was in need of a simple accounting module without all the bells and whistles. Here it is.
    """,

    'author': "Sergei Likharev",
    'website': "",
    'license': "GPL-3",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/16.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/account.xml',
        'views/transaction.xml',
        'views/expense.xml',
        'views/res_config_settings.xml'
    ],
    'installable': True,
    'application': True
}
