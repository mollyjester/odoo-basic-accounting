from odoo import models, fields, api
from . import veryfistream


class ObaExpense(models.Model):
    _name = 'oba.expense'
    _description = 'Expense'

    vendor_id = fields.Many2one(string='Vendor', comodel_name='res.partner', ondelete='restrict')
    category_id = fields.Many2one(string='Category', comodel_name='oba.expense.category', ondelete='set null')
    amount = fields.Monetary(string="Amount", required=True)
    date = fields.Date(string="Date", required=True, default=fields.Date.today())
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
    attachment = fields.Binary(string="Attachment")
    attachment_name = fields.Char(string="Attachment name")

    def name_get(self):
        return [(record.id, f"{record.account_id.name} > {record.vendor_id.name or record.offset_account_id.name}") for
                record in self]

    @api.model
    def process_ocr(self, file_raw, file_name, category):
        ret = None
        # veryfi client_id: vrfa95DCfutsyxZv7aPdmK6rkllfETI02axGi3i
        # username: ikusurei
        # api key: 2e14f9a9d8191344993293bcd3d86a5f
        if file_raw:
            client_id = 'vrfa95DCfutsyxZv7aPdmK6rkllfETI02axGi3i'
            client_secret = '56H3ngR4Ox6rhVoVDpUayWMIKMOckScc5esAAZbubD90ffMfPgDgA2LlPBHIi5f3zhA5hXxFaN6JOMmtKtYgumf25SMECghrY4cX1Ux2SDfOTWX3RkzwO2vF8Vk0iUtN'
            username = 'ikusurei'
            api_key = '2e14f9a9d8191344993293bcd3d86a5f'
            veryfi_client = veryfistream.VeryfiClient(client_id, client_secret, username, api_key)
            ret = veryfi_client.process_document_base64(file_raw, file_name, categories=category)
        return ret

    @api.model
    def update_vals(self, vals, json):
        if json:
            vals['amount'] = json['total']
            vals['date'] = fields.Date.to_date(json['date'])
            if json['vendor'] and json['vendor']['name']:
                partner = self.env['res.partner'].search([('name', '=', json['vendor']['name'])], limit=1)
                if not partner:
                    partner = self.env['res.partner'].create({
                        'name': json['vendor']['name'],
                        'street': json['vendor']['address']
                    })
                vals['vendor_id'] = partner.id
        return vals

    def write(self, vals):
        if 'attachment' in vals and vals['attachment']:
            json = self.process_ocr(vals['attachment'], vals['attachment_name'], vals['category_id'] or self.category_id.name)
            vals = self.update_vals(vals, json)
        return super(ObaExpense, self).write(vals)

    @api.model
    def create(self, vals_list):
        if 'attachment' in vals_list and vals_list['attachment']:
            category = None
            if vals_list['category_id']:
                category = [
                    self.env['oba.expense.category'].search([('id', '=', vals_list['category_id'])], limit=1).name]
            json = self.process_ocr(vals_list['attachment'], vals_list['attachment_name'], category)
            vals_list = self.update_vals(vals_list, json)
        return super(ObaExpense, self).create(vals_list)


class ObaExpenseCategory(models.Model):
    _name = 'oba.expense.category'
    _description = 'Expense Category'

    name = fields.Char(string='Name', required=True)
