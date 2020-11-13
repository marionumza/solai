from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
import logging
_logger = logging.getLogger(__name__)
from odoo import fields, http
import os
import base64
import json
import ast
from odoo.addons.website_form.controllers.main import WebsiteForm

try:
    from secrets import token_hex
except ImportError:
    from os import urandom

    def token_hex(nbytes=None):
        return urandom(nbytes).hex()


class WebsiteSale(WebsiteSale):

    # overrided to upload images
    @http.route(['/shop/checkout'], type='http', auth="public", website=True, sitemap=False)
    def checkout(self, **post):
        order = request.website.sale_get_order()
        if order.image_ids or post.get('proceed_without_images',False):
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
        if image_id and image_id != 'undefined':
            image = request.env['document.line'].sudo().search([('id','=',int(image_id))])
            if image:
                image.attachment_id.unlink()
                image.unlink()
            return json.dumps({'result':True})
        return json.dumps({'result':False})

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
                    url = '/web/image/%s?access_token=%s'%(image.attachment_id.id,image.attachment_id.access_token)
                    if image.attachment_id.sudo().mimetype == 'application/pdf':
                        url = ''
                    images.append((
                        image.file_name or 'Attachment',image.id,url))
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


class ContactController(WebsiteForm):

    @http.route(['/contactus'], type='http', auth='public', website=True)
    def render_contactus(self, **kwargs):
        values = {}
        values.update({
            'contactus_token':token_hex(32)
            })
        return http.request.render('website.contactus', values)

    @http.route('/website_form/<string:model_name>', type='http', auth="public", methods=['POST'], website=True)
    def website_form(self, model_name, **kwargs):
        if kwargs.get('send_mail_from_contactus',False):
            model_name = 'mail.mail'
        return super(ContactController, self).website_form(model_name, **kwargs)


    def extract_data(self, model, values):
        send_mail_from_contactus = False
        contactus_token = ''
        if values.get('send_mail_from_contactus',False):
            send_mail_from_contactus = True
            values.pop('send_mail_from_contactus')
        if values.get('contactus_token',False):
            contactus_token = values['contactus_token']
            values.pop('contactus_token')
        data = super(ContactController, self).extract_data(model, values)
        attachment_ids = []
        if send_mail_from_contactus and contactus_token:
            attachments = request.env['ir.attachment'].sudo().search([('contactus_token','=',contactus_token)])
            for attachment in attachments:
                attachment_ids.append(attachment.sudo().id)
            data['record']['attachment_ids'] = attachment_ids
        return data

    def insert_record(self, request, model, values, custom, meta=None):
        model_name = model.sudo().model
        if model_name == 'mail.mail':
            values.update({'subject': 'Inquiry from Modular Greenhouses Website'})
        record = super(ContactController, self).insert_record(request, model, values, custom, meta)
        return record



    @http.route('/contactus-file-upload', type='http', auth="public", methods=['POST'], website=True, csrf=False)
    def validate_contactus_file_upload(self, **kw):
        attachment_id = False
        if kw.get('file', False):
            file = kw['file']
            file_name = os.path.splitext(file.filename)
            file_binary = base64.encodestring(kw['file'].read())
            Attachment = request.env['ir.attachment'].sudo().create({
                'name':file.filename,
                'datas':file_binary,
                })
            attachment_id = Attachment.id
        return json.dumps(attachment_id)

    @http.route(['/update/contactustoken/<att_dict>'], type='http', auth="public", website=True, csrf=False)
    def render_update_token(self, att_dict, **kw):
        values = ast.literal_eval(att_dict)
        attachment_id = values.get('attachment_id',False)
        token = values.get('token',False)
        if attachment_id and attachment_id != 'undefined' and token:
            attachment = request.env['ir.attachment'].sudo().search([('id','=',int(attachment_id))])
            if attachment:
                attachment.sudo().write({'contactus_token':token})
        return json.dumps({'result':True})


    @http.route(['/remove/contactusfile/<attachment_id>'], type='http', auth="public", website=True, csrf=False)
    def render_remove_contactusfile(self, attachment_id, **kw):
        if attachment_id and attachment_id != 'undefined':
            attachment = request.env['ir.attachment'].sudo().search([('id','=',int(attachment_id))])
            if attachment:
                attachment.unlink()
            return json.dumps({'result':True})
        return json.dumps({'result':False})