from odoo import models, fields, api
from odoo.exceptions import ValidationError


class ObaTransfer(models.Model):
    _name = 'oba.transfer'
    _description = 'Transfer'

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
    transaction_ids = fields.One2many(string="Transactions", comodel_name='oba.transaction', inverse_name="source_id",
                                      readonly=True)

    @api.depends('account_id', 'offset_account_id')
    def _compute_display_name(self):
        for expense in self:
            name = f"{expense.account_id.name or 'Account'} > {expense.offset_account_id.name or 'Offset account'} "
            expense.display_name = name

    def write(self, vals):
        if 'state' in vals:
            if self.validate_fields(vals):
                self.set_status(vals['state'])
        else:
            for transfer in self:
                if transfer.state == 'posted':
                    raise ValidationError(f"Transfer {transfer.display_name} is already posted."
                                          "Revert it to Draft first.")
        return super(ObaTransfer, self).write(vals)

    def unlink(self):
        for transfer in self:
            if transfer.state == 'posted':
                raise ValidationError(f"Transfer {transfer.display_name} is already posted."
                                      "Revert it to Draft first.")
        return super(ObaTransfer, self).unlink()

    def set_status(self, status):
        if status == 'draft':
            transactions = self.env['oba.transaction'].sudo().search(
                [('source_model', '=', self._name), ('source_id', 'in', self.ids)])
            transactions.unlink()
        elif status == 'posted':
            for transfer in self:
                self.env['oba.transaction'].create({
                    'amount': transfer.amount,
                    'date': transfer.date,
                    'account_id': transfer.account_id.id,
                    'offset_account_id': transfer.offset_account_id.id,
                    'company_id': transfer.company_id.id,
                    'source_model': self._name,
                    'source_id': transfer.id
                })
        return True

    def validate_fields(self, vals):
        ret = True
        if 'state' in vals and vals['state'] == 'posted':
            for transfer in self:
                if not transfer.amount:
                    raise ValidationError(f"{transfer._fields['amount'].string} cannot be empty.")
                if not transfer.date:
                    raise ValidationError(f"{transfer._fields['date'].string} cannot be empty.")
                if not transfer.account_id:
                    raise ValidationError(f"{transfer._fields['account_id'].string} cannot be empty.")
                if not transfer.offset_account_id:
                    raise ValidationError(f"{transfer._fields['offset_account_id'].string} cannot be empty.")
                if not transfer.company_id:
                    raise ValidationError(f"{transfer._fields['company_id'].string} cannot be empty.")
        return ret
