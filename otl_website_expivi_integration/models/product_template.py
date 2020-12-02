from odoo import api, fields, models
from odoo.http import request

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    expivi_catalogueid = fields.Char('Expivi Catalogue Id')

class OTLExtraComponent(models.Model):
    _name = "otl.extra.component"

    name = fields.Char('Name')
    price = fields.Float(string='Attribute Price')
    quantity = fields.Float(string='Attribute Quantity')
    order_id = fields.Many2one('sale.order',string="Sale order")
    expivi_attribute_id = fields.Integer(String="Expivi Attribute ID")

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    main_product_id = fields.Many2one('product.product', string='Main Product')
    expivi_configuration = fields.Char('Expivi Configuration')

class SaleOrder(models.Model):
    _inherit = "sale.order"

    extracomponent_ids = fields.One2many('otl.extra.component', 'order_id', string='Extra Component')

    # def _website_product_id_change(self, order_id, product_id, qty=0):
    #     order = self.sudo().browse(order_id)
    #     product_context = dict(self.env.context)
    #     product_context.setdefault('lang', order.partner_id.lang)
    #     product_context.update({
    #         'partner': order.partner_id,
    #         'quantity': qty,
    #         'date': order.date_order,
    #         'pricelist': order.pricelist_id.id,
    #         'force_company': order.company_id.id,
    #     })
    #     product = self.env['product.product'].with_context(product_context).browse(product_id)
    #     discount = 0
    #
    #     if order.pricelist_id.discount_policy == 'without_discount':
    #         # This part is pretty much a copy-paste of the method '_onchange_discount' of
    #         # 'sale.order.line'.
    #         price, rule_id = order.pricelist_id.with_context(product_context).get_product_price_rule(product,
    #                                                                                                  qty or 1.0,
    #                                                                                                  order.partner_id)
    #         pu, currency = request.env['sale.order.line'].with_context(product_context)._get_real_price_currency(
    #             product, rule_id, qty, product.uom_id, order.pricelist_id.id)
    #         if pu != 0:
    #             if order.pricelist_id.currency_id != currency:
    #                 # we need new_list_price in the same currency as price, which is in the SO's pricelist's currency
    #                 date = order.date_order or fields.Date.today()
    #                 pu = currency._convert(pu, order.pricelist_id.currency_id, order.company_id, date)
    #             discount = (pu - price) / pu * 100
    #             if discount < 0:
    #                 # In case the discount is negative, we don't want to show it to the customer,
    #                 # but we still want to use the price defined on the pricelist
    #                 discount = 0
    #                 pu = price
    #         if self.env['product.template'].browse(product_id).expivi_catalogueid:
    #     else:
    #         pu = product.price
    #         if order.pricelist_id and order.partner_id:
    #             order_line = order._cart_find_product_line(product.id)
    #             if order_line:
    #                 pu = self.env['account.tax']._fix_tax_included_price_company(pu, product.taxes_id,
    #                                                                              order_line[0].tax_id, self.company_id)
    #
    #     return {
    #         'product_id': product_id,
    #         'product_uom_qty': qty,
    #         'order_id': order_id,
    #         'product_uom': product.uom_id.id,
    #         'price_unit': pu,
    #         'discount': discount,
    #     }


