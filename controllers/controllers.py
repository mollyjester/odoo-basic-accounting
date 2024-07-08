# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request


class ObaStatistics(http.Controller):
    @http.route('/oba/statistics', type='json', auth='user')
    def get_statistics(self):
        data_set = request.env['oba.expense'].total_amount('2024-01-01', '2024-07-31', 'month')
        print(data_set)
        expenses = {record['date:month']: record['amount'] for record in data_set}
        return {
            'expenses': expenses,
            # 'expenses_categorised': category, amount
            # income: month, amount
            # income_categorised: category, amount
            # balance: month, income-expense
            # balance_per_account: account, amount
        }
