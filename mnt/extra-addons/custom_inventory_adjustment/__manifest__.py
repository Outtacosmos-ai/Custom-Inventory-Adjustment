{
    'name': 'Custom Inventory Adjustment',
    'version': '11.0.1.0.0',
    'summary': 'Custom inventory adjustment module',
    'description': """
        This module provides custom inventory adjustment functionality with:
        - Custom user groups
        - Menu items for inventory adjustment
        - Stock adjustment features
    """,
    'category': 'Inventory',
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'AGPL-3',
    'depends': ['base', 'stock', 'other_required_module'],
    'data': [
        'security/inventory_security.xml',
        'security/ir.model.access.csv',
        'data/inventory_adjustment_data.xml',
        'data/sequences.xml',
        'views/inventory_adjustment_views.xml',
        'views/menu_items.xml',
        'views/actions.xml',
        'views/templates.xml',
        'reports/adjustment_report.xml',
        'wizards/adjustment_wizard_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}