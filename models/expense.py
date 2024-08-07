from odoo import models, fields, api
from . import veryfistream
from odoo.exceptions import ValidationError


class ObaExpense(models.Model):
    _name = 'oba.expense'
    _description = 'Expense'

    vendor_id = fields.Many2one(string='Vendor', comodel_name='res.partner', ondelete='restrict')
    category_id = fields.Many2one(string='Category', comodel_name='oba.expense.category', ondelete='set null')
    amount = fields.Monetary(string="Amount")
    date = fields.Date(string="Date", default=fields.Date.today())
    account_id = fields.Many2one(string="Account", comodel_name='oba.account')
    offset_account_id = fields.Many2one(string="Offset account", comodel_name='oba.account')
    company_id = fields.Many2one('res.company', readonly=True,
                                 default=lambda self: self.env.company)
    currency_id = fields.Many2one(string="Currency", related='company_id.currency_id', readonly=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('posted', 'Posted')
    ], string='Status', copy=False, default='draft')
    attachment = fields.Binary(string="Attachment")
    attachment_name = fields.Char(string="Attachment name")
    transaction_ids = fields.One2many(string="Transactions", comodel_name='oba.transaction', inverse_name="source_id",
                                      readonly=True)

    @api.depends('account_id', 'vendor_id', 'offset_account_id')
    def _compute_display_name(self):
        for expense in self:
            name = f"{expense.account_id.name or 'Account'} > {expense.offset_account_id.name or 'Offset account'} "
            name += f"({expense.vendor_id.name or 'Vendor'})"
            expense.display_name = name

    @api.model
    def process_ocr(self, file_raw, file_name, category):
        ret = None
        if file_raw:
            client_id = self.env['ir.config_parameter'].sudo().get_param('odoo_basic_accounting.veryfi_client_id')
            client_secret = self.env['ir.config_parameter'].sudo().get_param(
                'odoo_basic_accounting.veryfi_client_secret')
            username = self.env['ir.config_parameter'].sudo().get_param('odoo_basic_accounting.veryfi_username')
            api_key = self.env['ir.config_parameter'].sudo().get_param('odoo_basic_accounting.veryfi_api_key')
            if client_id and client_secret and username and api_key:
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
                        'street': json['vendor']['address'],
                        'is_company': True
                    })
                vals['vendor_id'] = partner.id
        return vals

    @api.model
    def total_amount(self, date_start=None, date_end=None, granularity=None):
        domain = [('state', '=', 'posted')]
        if date_start:
            domain.append(('date', '>=', date_start))
        if date_end:
            domain.append(('date', '<=', date_end))
        groupby = 'date'
        if granularity:
            groupby += ':' + granularity
        return self.env['oba.expense'].read_group(domain, ['amount:sum', 'date'], groupby)

    def write(self, vals):
        if 'state' in vals:
            if self.validate_fields(vals):
                self.set_status(vals['state'])
        else:
            for expense in self:
                if expense.state == 'posted':
                    raise ValidationError(f"Expense {expense.display_name} is already posted."
                                          "Revert it to Draft first.")
                else:
                    if 'attachment' in vals and vals['attachment']:
                        json = self.process_ocr(vals['attachment'], vals['attachment_name'],
                                                vals['category_id'] or expense.category_id.name)
                        vals = self.update_vals(vals, json)
        return super(ObaExpense, self).write(vals)

    def unlink(self):
        for expense in self:
            if expense.state == 'posted':
                raise ValidationError(f"Expense {expense.display_name} is already posted."
                                      "Revert it to Draft first.")
        return super(ObaExpense, self).unlink()

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

    def set_status(self, status):
        if status == 'draft':
            transactions = self.env['oba.transaction'].sudo().search(
                [('source_model', '=', self._name), ('source_id', 'in', self.ids)])
            transactions.unlink()
        elif status == 'posted':
            for expense in self:
                self.env['oba.transaction'].create({
                    'amount': expense.amount,
                    'date': expense.date,
                    'account_id': expense.account_id.id,
                    'offset_account_id': expense.offset_account_id.id,
                    'company_id': expense.company_id.id,
                    'source_model': self._name,
                    'source_id': expense.id
                })
        return True

    def validate_fields(self, vals):
        ret = True
        if 'state' in vals and vals['state'] == 'posted':
            for expense in self:
                if not expense.amount:
                    raise ValidationError(f"{expense._fields['amount'].string} cannot be empty.")
                if not expense.date:
                    raise ValidationError(f"{expense._fields['date'].string} cannot be empty.")
                if not expense.account_id:
                    raise ValidationError(f"{expense._fields['account_id'].string} cannot be empty.")
                if not expense.offset_account_id:
                    raise ValidationError(f"{expense._fields['offset_account_id'].string} cannot be empty.")
                if not expense.company_id:
                    raise ValidationError(f"{expense._fields['company_id'].string} cannot be empty.")
        return ret


class ObaExpenseCategory(models.Model):
    _name = 'oba.expense.category'
    _description = 'Expense Category'

    name = fields.Char(string='Name', required=True)
