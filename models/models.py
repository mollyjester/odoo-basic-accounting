# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from . import veryfistream

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

    # attachment_ids = fields.Many2many('ir.attachment', string="Attachments")
    attachment = fields.Binary(string="Attachment")
    attachment_name = fields.Char(string="Attachment name")

    def process_document(self, document):

        return True

    def process_ocr(self, file_raw, file_name):
        # veryfi client_id: vrfa95DCfutsyxZv7aPdmK6rkllfETI02axGi3i
        # username: ikusurei
        # api key: 2e14f9a9d8191344993293bcd3d86a5f
        if file_raw:
            client_id = 'vrfa95DCfutsyxZv7aPdmK6rkllfETI02axGi3i'
            client_secret = '56H3ngR4Ox6rhVoVDpUayWMIKMOckScc5esAAZbubD90ffMfPgDgA2LlPBHIi5f3zhA5hXxFaN6JOMmtKtYgumf25SMECghrY4cX1Ux2SDfOTWX3RkzwO2vF8Vk0iUtN'
            username = 'ikusurei'
            api_key = '2e14f9a9d8191344993293bcd3d86a5f'
            veryfi_client = veryfistream.VeryfiClient(client_id, client_secret, username, api_key)
            categories = ['Grocery', 'Utilities', 'Travel']
            document_json = veryfi_client.process_document_base64(file_raw, file_name, categories=categories)
            print(document_json)
        return True

    def write(self, vals):
        # if 'attachment' in vals and vals['attachment']:
        #     self.process_ocr(self.attachment.raw, self.attachment.name)
        return super(ObaTransaction, self).write(vals)

    def create(self, vals_list):
        # if 'attachment' in vals_list and vals_list['attachment']:
        #     self.process_ocr(vals_list['attachment'], '')
        ret = super(ObaTransaction, self).create(vals_list)
        # self.env['ir.attachment'].search_count([()])
        return ret
