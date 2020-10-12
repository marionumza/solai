from odoo import models, fields, api, _

class DocumentLine(models.Model):
    _name = 'document.line'
    _description = "Documents"

    document_binary = fields.Binary(string="Attachment", attachment=True)
    file_name = fields.Char('File Name')
    sale_id = fields.Many2one('sale.order')
    attachment_id = fields.Many2one('ir.attachment')


class Sale(models.Model):
	_inherit = 'sale.order'

	image_ids = fields.One2many('document.line','sale_id')