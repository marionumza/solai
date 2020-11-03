from odoo import models, fields, api

class IrAttachment(models.Model):
	_inherit = 'ir.attachment'

	contactus_token = fields.Char("Contact Us Token")