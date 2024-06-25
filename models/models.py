# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError

# veryfi client_id: vrfa95DCfutsyxZv7aPdmK6rkllfETI02axGi3i
# client_secret = '56H3ngR4Ox6rhVoVDpUayWMIKMOckScc5esAAZbubD90ffMfPgDgA2LlPBHIi5f3zhA5hXxFaN6JOMmtKtYgumf25SMECghrY4cX1Ux2SDfOTWX3RkzwO2vF8Vk0iUtN'
# username: ikusurei
# api key: 2e14f9a9d8191344993293bcd3d86a5f


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
        ('revenue', 'Revenue')
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
    date = fields.Date(string="Date", required=True, default=fields.Date.today())
    account_id = fields.Many2one(string="From account", comodel_name='oba.account', readonly=False, required=True)
    offset_account_id = fields.Many2one(string="To account", comodel_name='oba.account', readonly=False, required=True)
    company_id = fields.Many2one('res.company', readonly=False,
                                 default=lambda self: self.env.company, required=True)
    currency_id = fields.Many2one(string="Currency", related='company_id.currency_id', readonly=True)
    source_model = fields.Char('Source model', readonly=True)
    source_id = fields.Many2oneReference('Source Id', model_field='source_model', readonly=True)

    def name_get(self):
        return [(record.id, f"{record.account_id.name} > {record.offset_account_id.name}") for record in self]

    @api.model
    def create(self, vals_list):
        new_record = super(ObaTransaction, self).create(vals_list)
        new_record.account_id.balance = new_record.account_id.balance - new_record.amount
        new_record.offset_account_id.balance = new_record.offset_account_id.balance + new_record.amount
        return new_record

    def write(self, vals):
        ret = super(ObaTransaction, self).write(vals)
        for record in self:
            record.account_id.balance = record.account_id.balance - record.amount
            record.offset_account_id.balance = record.offset_account_id.balance + record.amount
        return ret

    def unlink(self):
        for record in self:
            record.account_id.balance = record.account_id.balance - record.amount
            record.offset_account_id.balance = record.offset_account_id.balance + record.amount
        result = super(ObaTransaction, self).unlink()
        return result
