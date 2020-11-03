{
    'name': 'Website Sale Extended',
    'category': 'Website/Website',
    'sequence': 55,
    'summary': 'Upload images when products checkout',
    'version': '1.0',
    'description': "",
    'depends': ['website_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/assets.xml',
        'static/src/xml/website_sale_file_upload.xml',
        'static/src/xml/progress_bar.xml',
        'views/sale.xml',
        'data/website_data.xml',
        'views/website_crm_templates.xml'
    ],
    'installable': True,
    'application': True,
}
