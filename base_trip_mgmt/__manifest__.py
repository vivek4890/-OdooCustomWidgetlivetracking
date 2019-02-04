
{
    'name': 'Base Trip Management',
    'version': '1.1',
    'category': 'Configuaration',
    'depends': ['hr','account_accountant','fleet', 'web'],
    'demo': [

    ],
    'description': """
    Base Trip Management.
========================================================================
    """,
    'data': [
        'views/page_live.xml',
        'security/ir.model.access.csv',
        'views/base_trip_management_view.xml',
    ],
    'qweb': ['static/src/xml/page.xml'],
    'installable': True,
    'auto_install': False,
    'application': True,
}
