# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

class ObaAccount(models.Model):
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
    company_id = fields.Many2one('res.company', readonly=False,
                                 default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one(string="Currency", related='company_id.currency_id', readonly=True)
    balance = fields.Monetary(string="Balance", readonly=True, currency_field='currency_id')

    def write(self, vals):
        # Do not allow changing the company_id when transactions exist
        if vals.get('company_id', False):
            for account in self:
                if self.env['oba.transaction'].search_count(
                        ['|', ('account_id', '=', account.id), ('offset_account_id', '=', account.id)]):
                    raise UserError('Company cannot be changed while related transactions exist.')
        return super(ObaAccount, self).write(vals)

class ObaTransaction(models.Model):
    _name = 'oba.transaction'
    _description = 'Transaction'

    amount = fields.Monetary(string="Amount", required=True)
    date = fields.Date(string="Date", required=True)

    account_id = fields.Many2one(string="From account", comodel_name='oba.account', readonly=False, required=True)
    offset_account_id = fields.Many2one(string="To account", comodel_name='oba.account', readonly=False, required=True)

    company_id = fields.Many2one('res.company', readonly=False,
                                 default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one(string="Currency", related='company_id.currency_id', readonly=True)

    state = fields.Selection([
        ('draft', 'New'),
        ('posted', 'Posted'),
        ('cancel', 'Cancelled')
    ], string='Status', copy=False, default='draft', tracking=True)

    attachment_ids = fields.Many2many('ir.attachment', string="Attachments")
