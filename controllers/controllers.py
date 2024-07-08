# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request


class ObaStatistics(http.Controller):
    @http.route('/oba/statistics', type='json', auth='user')
    def get_expenses(self):
        # data_set = request.env['oba.expense'].total_amount('2024-01-01', '2024-07-31', 'month')
        # for record in data_set:
        #     print(record)
        return {
            'average_quantity': 0,
            'average_time': 1,
            'nb_cancelled_orders': 2,
            'nb_new_orders': 3,
            'orders_by_size': {
                'm': 4,
                's': 5,
                'xl': 6,
            },
            'total_amount': 7
        }
