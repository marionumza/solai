
import datetime
import logging
from odoo import http, models, fields, _
from odoo.http import request
from odoo.addons.portal.controllers.web import Home
import ast

logger = logging.getLogger(__name__)

# Completely arbitrary limits
MAX_IMAGE_WIDTH, MAX_IMAGE_HEIGHT = IMAGE_LIMITS = (1024, 768)
LOC_PER_SITEMAP = 45000
SITEMAP_CACHE_TIME = datetime.timedelta(hours=12)

class Website(Home):

    @http.route('/configure/website/expivi', type='http', auth="public", methods=['POST', 'GET'], website=True)
    def configure_product(self, **kwargs):
        return request.render('otl_website_expivi_integration.custom_product_templ')

    @http.route('/save/website/expivi_data/', type='http',auth='public', website=True,csrf=False)
    def save_custom_product_(self, **kwargs):
        domain = []
        raisedbedcorregated=shelfbed16Deep=workbench=False
        for i in range(0, int(len(kwargs) / 10)):
            # kwargs.get('data[configured_products][0][configuration][attributes][i][attribute_id]')
            name = kwargs.get('data[configured_products][0][configuration][attributes]['+str(i)+'][attribute_name]',False)
            value = kwargs.get('data[configured_products][0][configuration][attributes]['+str(i)+'][attribute_value_name]',False)
            if name in ['Glass Type', 'Type', 'Size'] and name and value:
                #.append((name, '=', value))
                val=request.env['product.template.attribute.value'].search([('name', '=',value)])
                domain.append(val.id)

            if name in [ 'WorkBench','ShelfBed16Deep','RaisedBedCorregated'] and name and value:
                if name=='WorkBench' and value:
                    workbench=True
                if name=='ShelfBed16Deep' and value:
                    shelfbed16Deep=True
                if name=='RaisedBedCorregated' and value:
                    raisedbedcorregated=True
        configuration=''
        if kwargs:
            domain.sort()
            product_id=[]
            price=[]
            configuration=kwargs
            main_product_id=[]
            for product in request.env['product.product'].search([('product_template_attribute_value_ids','=',domain)]):
                if product.product_template_attribute_value_ids and product.product_template_attribute_value_ids.ids==domain:
                    product_id.append(product.id)
                    price.append(kwargs.get('data[configured_products][0][price][base]',0))
                    main_product_id.append(False)
                    if raisedbedcorregated:
                        if request.env['product.product'].search([('name','=','RaisedBedCorregated')]):
                            product_id.append(request.env['product.product'].search([('name','=','RaisedBedCorregated')]).id)
                            price.append(request.env['product.product'].search([('name','=','RaisedBedCorregated')]).lst_price)
                            main_product_id.append(product.id)
                    if shelfbed16Deep:
                        if request.env['product.product'].search([('name','=','ShelfBed16Deep')]):
                            product_id.append(request.env['product.product'].search([('name','=','ShelfBed16Deep')]).id)
                            price.append(request.env['product.product'].search([('name','=','ShelfBed16Deep')]).lst_price)
                            main_product_id.append(product.id)
                    if workbench:
                        if request.env['product.product'].search([('name','=','WorkBench')]):
                            product_id.append(request.env['product.product'].search([('name','=','WorkBench')]).id)
                            price.append(request.env['product.product'].search([('name','=','WorkBench')]).lst_price)
                            main_product_id.append(product.id)
            sale_order = request.website.sale_get_order(force_create=True)
            SaleOrderLineSudo = request.env['sale.order.line'].sudo()
            for rang in range(0,len(product_id)):
                #if product_id:
                    vale={'product_id': product_id[rang],
                          'product_uom_qty': 1,
                          'expivi_configuration':configuration,
                          'main_product_id':main_product_id[rang],
                          'order_id': sale_order.id,
                          'product_uom': 1,
                          'price_unit':  price[rang] or 0,
                          'discount': 0,
                          'customer_lead': 0.0}
                    order_line = SaleOrderLineSudo.create(vale)
        return request.env['ir.config_parameter'].get_param('web.base.url')+'/shop/cart'

from odoo.addons.website.models.ir_http import sitemap_qs2dom
from odoo.addons.http_routing.models.ir_http import slug
from werkzeug.exceptions import Forbidden, NotFound
from odoo.addons.website.controllers.main import QueryURL
from odoo.addons.website_sale.controllers.main import TableCompute
from odoo.addons.website_sale.controllers.main import WebsiteSale
import json

class WebsiteSale(WebsiteSale):

    @http.route(['/shop/product/<model("product.template"):product>'], type='http', auth="public", website=True)
    def product(self, product, category='', search='', **kwargs):
        if not product.can_access_from_current_website():
            raise NotFound()
        if product.expivi_catalogueid:
            return request.render('otl_website_expivi_integration.custom_product_templ')
        return request.render("website_sale.product", self._prepare_product_values(product, category, search, **kwargs))

    @http.route(['/shop/cart/update'], type='http', auth="public", methods=['GET', 'POST'], website=True, csrf=False)
    def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        """This route is called when adding a product to cart (no options)."""
        if product_id and request.env['product.template'].browse(int(product_id)).expivi_catalogueid:
            return request.redirect("/configure/website/expivi")
           # return request.render('otl_website_expivi_integration.custom_product_templ')
        sale_order = request.website.sale_get_order(force_create=True)
        if sale_order.state != 'draft':
            request.session['sale_order_id'] = None
            sale_order = request.website.sale_get_order(force_create=True)

        product_custom_attribute_values = None
        if kw.get('product_custom_attribute_values'):
            product_custom_attribute_values = json.loads(kw.get('product_custom_attribute_values'))

        no_variant_attribute_values = None
        if kw.get('no_variant_attribute_values'):
            no_variant_attribute_values = json.loads(kw.get('no_variant_attribute_values'))

        sale_order._cart_update(
            product_id=int(product_id),
            add_qty=add_qty,
            set_qty=set_qty,
            product_custom_attribute_values=product_custom_attribute_values,
            no_variant_attribute_values=no_variant_attribute_values
        )

        if kw.get('express'):
            return request.redirect("/shop/checkout?express=1")

        return request.redirect("/shop/cart")

    def sitemap_shop(env, rule, qs):
        if not qs or qs.lower() in '/shop':
            yield {'loc': '/shop'}
        Category = env['product.public.category']
        dom = sitemap_qs2dom(qs, '/shop/category', Category._rec_name)
        dom += env['website'].get_current_website().website_domain()
        for cat in Category.search(dom):
            loc = '/shop/category/%s' % slug(cat)
            if not qs or qs.lower() in loc:
                yield {'loc': loc}

    @http.route([
        '''/shop''',
        '''/shop/page/<int:page>''',
        '''/shop/category/<model("product.public.category"):category>''',
        '''/shop/category/<model("product.public.category"):category>/page/<int:page>'''
    ], type='http', auth="public", website=True, sitemap=sitemap_shop)
    def shop(self, page=0, category=None, search='', ppg=False, **post):
        add_qty = int(post.get('add_qty', 1))
        if category and request.env.ref('website_form_custom_product.custom_product_').id ==category.id:
            return request.render('website_form_custom_product.custom_product_templ')
        Category = request.env['product.public.category']
        if category:
            category = Category.search([('id', '=', int(category))], limit=1)
            if not category or not category.can_access_from_current_website():
                raise NotFound()
        else:
            category = Category

        if ppg:
            try:
                ppg = int(ppg)
                post['ppg'] = ppg
            except ValueError:
                ppg = False
        if not ppg:
            ppg = request.env['website'].get_current_website().shop_ppg or 20

        ppr = request.env['website'].get_current_website().shop_ppr or 4

        attrib_list = request.httprequest.args.getlist('attrib')
        attrib_values = [[int(x) for x in v.split("-")] for v in attrib_list if v]
        attributes_ids = {v[0] for v in attrib_values}
        attrib_set = {v[1] for v in attrib_values}

        domain = self._get_search_domain(search, category, attrib_values)

        keep = QueryURL('/shop', category=category and int(category), search=search, attrib=attrib_list, order=post.get('order'))

        pricelist_context, pricelist = self._get_pricelist_context()

        request.context = dict(request.context, pricelist=pricelist.id, partner=request.env.user.partner_id)

        url = "/shop"
        if search:
            post["search"] = search
        if attrib_list:
            post['attrib'] = attrib_list

        Product = request.env['product.template'].with_context(bin_size=True)

        search_product = Product.search(domain)
        website_domain = request.website.website_domain()
        categs_domain = [('parent_id', '=', False)] + website_domain
        if search:
            search_categories = Category.search([('product_tmpl_ids', 'in', search_product.ids)] + website_domain).parents_and_self
            categs_domain.append(('id', 'in', search_categories.ids))
        else:
            search_categories = Category
        categs = Category.search(categs_domain)

        if category:
            url = "/shop/category/%s" % slug(category)

        product_count = len(search_product)
        pager = request.website.pager(url=url, total=product_count, page=page, step=ppg, scope=7, url_args=post)
        products = Product.search(domain, limit=ppg, offset=pager['offset'], order=self._get_search_order(post))

        ProductAttribute = request.env['product.attribute']
        if products:
            # get all products without limit
            attributes = ProductAttribute.search([('product_tmpl_ids', 'in', search_product.ids)])
        else:
            attributes = ProductAttribute.browse(attributes_ids)

        layout_mode = request.session.get('website_sale_shop_layout_mode')
        if not layout_mode:
            if request.website.viewref('website_sale.products_list_view').active:
                layout_mode = 'list'
            else:
                layout_mode = 'grid'

        values = {
            'search': search,
            'category': category,
            'attrib_values': attrib_values,
            'attrib_set': attrib_set,
            'pager': pager,
            'pricelist': pricelist,
            'add_qty': add_qty,
            'products': products,
            'search_count': product_count,  # common for all searchbox
            'bins': TableCompute().process(products, ppg, ppr),
            'ppg': ppg,
            'ppr': ppr,
            'categories': categs,
            'attributes': attributes,
            'keep': keep,
            'search_categories_ids': search_categories.ids,
            'layout_mode': layout_mode,
        }
        if category:
            values['main_object'] = category
        return request.render("website_sale.products", values)