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

    @api.depends('account_id', 'vendor_id', 'offset_account_id')
    def _compute_display_name(self):
        for expense in self:
            expense.display_name = \
                f"{expense.account_id.name} > {expense.offset_account_id.name} ({expense.vendor_id.name})"

    @api.model
    def process_ocr(self, file_raw, file_name, category):
        ret = None
        if file_raw:
            client_id = self.env['ir.config_parameter'].sudo().get_param('odoo_basic_accounting.veryfi_client_id')
            client_secret = self.env['ir.config_parameter'].sudo().get_param(
                'odoo_basic_accounting.veryfi_client_secret')
            username = self.env['ir.config_parameter'].sudo().get_param('odoo_basic_accounting.veryfi_username')
            api_key = self.env['ir.config_parameter'].sudo().get_param('odoo_basic_accounting.veryfi_api_key')
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
