from odoo import api, fields, models, _
from odoo.exceptions import UserError

class AdjustmentWizard(models.TransientModel):
    _name = 'adjustment.wizard'
    _description = 'Inventory Adjustment Wizard'

    product_id = fields.Many2one('product.product', string='Product', required=True)
    location_id = fields.Many2one('stock.location', string='Location', required=True, domain=[('usage', '=', 'internal')])
    new_quantity = fields.Float('New Quantity', required=True)

    @api.multi
    def action_adjust_inventory(self):
        self.ensure_one()
        if self.new_quantity < 0:
            raise UserError(_('New quantity cannot be negative.'))

        adjustment = self.env['inventory.adjustment'].create({
            'date': fields.Date.context_today(self),
            'line_ids': [(0, 0, {
                'product_id': self.product_id.id,
                'current_quantity': self.product_id.with_context(location=self.location_id.id).qty_available,
                'new_quantity': self.new_quantity,
            })],
        })

        # Create stock inventory
        inventory = self.env['stock.inventory'].create({
            'name': _('Adjustment: %s') % adjustment.name,
            'filter': 'partial',
            'location_id': self.location_id.id,
            'adjustment_id': adjustment.id,
        })
        inventory.action_start()

        # Update inventory line
        inventory_line = self.env['stock.inventory.line'].create({
            'inventory_id': inventory.id,
            'product_id': self.product_id.id,
            'location_id': self.location_id.id,
            'product_qty': self.new_quantity,
        })

        # Validate inventory
        inventory.action_validate()

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'inventory.adjustment',
            'res_id': adjustment.id,
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'current',
        }