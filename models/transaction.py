from odoo import models, fields, api


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

    @api.depends('account_id', 'offset_account_id')
    def _compute_display_name(self):
        for expense in self:
            expense.display_name = \
                f"{expense.account_id.name} > {expense.offset_account_id.name}"

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
            record.account_id.balance = record.account_id.balance + record.amount
            record.offset_account_id.balance = record.offset_account_id.balance - record.amount
        return super(ObaTransaction, self).unlink()
