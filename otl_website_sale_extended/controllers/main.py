from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
import logging
_logger = logging.getLogger(__name__)
from odoo import fields, http
import os
import base64
import json
import ast


class WebsiteSale(WebsiteSale):

    # overrided to upload images
    @http.route(['/shop/checkout'], type='http', auth="public", website=True, sitemap=False)
    def checkout(self, **post):
        order = request.website.sale_get_order()
        if order.image_ids:
            redirection = self.checkout_redirection(order)
            if redirection:
                return redirection

            if order.partner_id.id == request.website.user_id.sudo().partner_id.id:
                return request.redirect('/shop/address')

            for f in self._get_mandatory_billing_fields():
                if not order.partner_id[f]:
                    return request.redirect('/shop/address?partner_id=%d' % order.partner_id.id)

            values = self.checkout_values(**post)

            if post.get('express'):
                return request.redirect('/shop/confirm_order')

            values.update({'website_sale_order': order})

            # Avoid useless rendering if called in ajax
            if post.get('xhr'):
                return 'ok'
            return request.render("website_sale.checkout", values)
        else:
            if post.get('express',0):
                return request.redirect('/shop/upload/images?express=1')
            else:
                return request.redirect('/shop/upload/images')
            return request.render("otl_website_sale_extended.file_upload_products_checkout", post)

    # calls When a new file uploaded
    @http.route('/file-upload', type='http', auth="public", methods=['POST'], website=True, csrf=False)
    def validate_file_upload(self, **kw):
        image_id = False
        sale_id = kw.get('sale_id',False)
        if sale_id:
            sale_order = request.env['sale.order'].sudo().search([('id', '=', kw['sale_id'])])
            if sale_order:
                if kw.get('file', False):
                    file = kw['file']
                    file_name = os.path.splitext(file.filename)
                    file_binary = base64.encodestring(kw['file'].read())
                    Attachment = request.env['ir.attachment'].sudo().create({
                        'name':file.filename,
                        'datas':file_binary
                        })
                    if Attachment:
                        image = request.env['document.line'].sudo().create({'attachment_id':Attachment.id,'document_binary':file_binary,'file_name':file.filename,'sale_id':sale_order.id})
                        image_id = image.id
                    
        return json.dumps(image_id)

    # calls when removing a file
    @http.route(['/remove/file/<image_id>'], type='http', auth="public", website=True, csrf=False)
    def render_remove_file(self, image_id, **kw):
        if image_id:
            image = request.env['document.line'].sudo().search([('id','=',int(image_id))])
            if image:
                image.attachment_id.unlink()
                image.unlink()
        return json.dumps({'result':True})

    @http.route(['/GetUploadedImages'], type='http', auth="public", website=True, csrf=False)
    def render_uploaded_images(self, **kw):
        order = request.website.sale_get_order()
        images = []
        result = {}
        if order and order.image_ids:
            for image in order.image_ids:
                if image.attachment_id:
                    if not image.attachment_id.access_token:
                        image.attachment_id.generate_access_token()
                    images.append((
                        image.file_name or 'Attachment',
                        image.id,
                        '/web/image/%s?access_token=%s'%(image.attachment_id.id,image.attachment_id.access_token)
                        ))
        result['images'] = images
        return json.dumps(result)

    @http.route(['/shop/upload/images'], type='http', methods=['GET', 'POST'], auth="public", website=True, sitemap=False)
    def render_upload_images(self, **kw):
        order = request.website.sale_get_order()
        values = {'sale_id':order.id}
        if kw.get('edit',0):
            if order.image_ids:
                values.update({'edit':1,'file_count':len(order.image_ids)})

        if kw.get('express',0):
            values.update({'express':1})
        return request.render("otl_website_sale_extended.file_upload_products_checkout", values)