from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    installer_id = fields.Many2one('res.users', string='Installer', )


class ResUsers(models.Model):
    _inherit = 'res.users'

    installer = fields.Boolean('Installer')
