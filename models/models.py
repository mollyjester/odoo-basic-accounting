# -*- coding: utf-8 -*-

from odoo import models, fields, api
#import requests
#import time


class obaAccount(models.Model):
    _name = 'oba.account'
    _description = 'Account'

    name = fields.Char(string="Account", required=True, index=True)
    description = fields.Char(string="Description")
    type = fields.Selection(string="Type", selection=[
        ('assets', 'Assets'),
        ('expenses', 'Expenses'),
        ('liabilities', 'Liabilities'),
        ('equity', 'Equity'),
        ('Revenue', 'Revenue')
    ], required=True)
    balance = fields.Monetary(string="Balance", readonly=True)
    company_id = fields.Many2one('res.company', readonly=False,
                                 default=lambda self: self.env.company, required=True)

class obaTransaction(models.Model):
    _name = 'oba.transaction'
    _description = 'Transaction'

    amount = fields.Monetary(string="Amount", required=True)
    date = fields.Date(string="Date", required=True)

    account_id = fields.Many2one(string="From account", 'oba.account', readonly=False, required=True)
    offset_account_id = fields.Many2one(string="To account", 'oba.account', readonly=False, required=True)

    #state = fields.Selection([
    #    ('draft', 'New'),
    #    ('posted', 'Posted'),
    #    ('cancel', 'Cancelled')
    #], string='Status', copy=False, default='draft', tracking=True)
