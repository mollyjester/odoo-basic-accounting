from odoo import models, fields, api


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
