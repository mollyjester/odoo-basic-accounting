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
    'category': 'Accounting',
    'version': '0.1',

    'depends': ['base', 'web'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/account.xml',
        'views/transaction.xml',
        'views/expense.xml',
        'views/transfer.xml',
        'views/res_config_settings.xml',
        'views/dashboard.xml'
    ],
    'assets': {
        'web.assets_backend': [
            'odoo-basic-accounting/static/src/**/*',
        ],
    },
    'installable': True,
    'application': True
}
