from odoo import api, models

class AdjustmentReport(models.AbstractModel):
    _name = 'report.custom_inventory_adjustment.report_adjustment'
    _description = 'Inventory Adjustment Report'

    @api.model
    def get_report_values(self, docids, data=None):
        docs = self.env['inventory.adjustment'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'inventory.adjustment',
            'docs': docs,
            'data': data,
        }