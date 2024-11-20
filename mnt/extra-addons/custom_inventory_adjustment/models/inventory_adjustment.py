from odoo import models, fields, api, _
from odoo.exceptions import UserError

class InventoryAdjustment(models.Model):
    _name = 'inventory.adjustment'
    _description = 'Inventory Adjustment'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, default=lambda self: _('New'))
    date = fields.Date(string='Date', default=fields.Date.context_today, required=True, track_visibility='onchange')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')
    ], string='Status', default='draft', track_visibility='onchange')
    line_ids = fields.One2many('inventory.adjustment.line', 'adjustment_id', string='Adjustment Lines')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id)
    reason_id = fields.Many2one('inventory.adjustment.reason', string='Adjustment Reason', required=True, track_visibility='onchange')
    approved_by = fields.Many2one('res.users', string='Approved By', readonly=True)
    approval_date = fields.Datetime(string='Approval Date', readonly=True)

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('inventory.adjustment') or _('New')
        if not vals.get('reason_id'):
            default_settings = self.env['inventory.adjustment.settings'].search([], limit=1)
            if default_settings and default_settings.default_reason_id:
                vals['reason_id'] = default_settings.default_reason_id.id
        return super(InventoryAdjustment, self).create(vals)

    def action_validate(self):
        for adjustment in self:
            if not adjustment.line_ids:
                raise UserError(_('You need to add at least one product to adjust.'))
            for line in adjustment.line_ids:
                line.product_id.with_context(force_company=adjustment.company_id.id).sudo().write({
                    'qty_available': line.new_quantity
                })
            adjustment.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'cancel'})

    def action_approve(self):
        self.ensure_one()
        settings = self.env['inventory.adjustment.settings'].search([], limit=1)
        if settings.require_approval:
            self.write({
                'approved_by': self.env.user.id,
                'approval_date': fields.Datetime.now(),
                'state': 'done'
            })
        else:
            self.write({'state': 'done'})
        if settings.auto_post_to_accounting:
            # Implement the logic to post to accounting here
            pass


class InventoryAdjustmentLine(models.Model):
    _name = 'inventory.adjustment.line'
    _description = 'Inventory Adjustment Line'

    adjustment_id = fields.Many2one('inventory.adjustment', string='Adjustment', required=True, ondelete='cascade')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    current_quantity = fields.Float(string='Current Quantity', readonly=True)
    new_quantity = fields.Float(string='New Quantity', required=True)
    difference = fields.Float(string='Difference', compute='_compute_difference')

    @api.depends('current_quantity', 'new_quantity')
    def _compute_difference(self):
        for line in self:
            line.difference = line.new_quantity - line.current_quantity

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.current_quantity = self.product_id.qty_available


class InventoryAdjustmentReason(models.Model):
    _name = 'inventory.adjustment.reason'
    _description = 'Inventory Adjustment Reason'

    name = fields.Char(string='Reason', required=True)
    code = fields.Char(string='Code', required=True)


class InventoryAdjustmentSettings(models.Model):
    _name = 'inventory.adjustment.settings'
    _description = 'Inventory Adjustment Settings'

    require_approval = fields.Boolean(string='Require Approval', default=True)
    approval_user_id = fields.Many2one('res.users', string='Approval User')
    auto_post_to_accounting = fields.Boolean(string='Auto Post to Accounting', default=False)
    default_reason_id = fields.Many2one('inventory.adjustment.reason', string='Default Reason')
