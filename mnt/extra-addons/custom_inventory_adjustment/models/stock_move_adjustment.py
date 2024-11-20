from odoo import models, fields, api

class StockMoveAdjustment(models.Model):
    _inherit = 'stock.move'

    adjustment_id = fields.Many2one('inventory.adjustment', string='Inventory Adjustment', ondelete='set null')

    @api.model
    def create(self, vals):
        move = super(StockMoveAdjustment, self).create(vals)
        if move.inventory_line_id and move.inventory_line_id.inventory_id.adjustment_id:
            move.adjustment_id = move.inventory_line_id.inventory_id.adjustment_id
        return move

class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    adjustment_id = fields.Many2one('inventory.adjustment', string='Custom Adjustment')

    def action_validate(self):
        res = super(StockInventory, self).action_validate()
        if self.adjustment_id:
            self.adjustment_id.write({'state': 'done'})
        return res