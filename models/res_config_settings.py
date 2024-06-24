from odoo import models, fields, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    veryfi_client_id = fields.Char(string="Client Id",
                                   config_parameter="odoo_basic_accounting.veryfi_client_id")
    veryfi_client_secret = fields.Char(string="Client secret",
                                       config_parameter="odoo_basic_accounting.veryfi_client_secret")
    veryfi_username = fields.Char(string="User name",
                                  config_parameter="odoo_basic_accounting.veryfi_username")
    veryfi_api_key = fields.Char(string="API key",
                                 config_parameter="odoo_basic_accounting.veryfi_api_key")
