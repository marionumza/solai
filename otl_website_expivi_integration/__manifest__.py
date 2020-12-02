
{
    'name': 'Website Custom Product Expivi Integration',
    'summary': 'Get the enterprise look and feel',
    'description': """
            This module overrides website and  customize product via expivi integration
    """,
    'depends': ['business_snippet_blocks_core','sale','website','website_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/custom_product.xml',
        'views/custom_product.xml',
        'views/res_configSettings.xml',
        'views/templates.xml',
        'views/product_template_view.xml',
        # 'data/custom_product_category.xml'
    ],
    'installable': True,
    'auto_install': True,
}
