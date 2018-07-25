# -*- coding: utf-8 -*-
# © Copyright 2018 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from openerp import api, fields, models


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    reserved_quantity = fields.Float('Reserved Quantity',
                                     compute='_compute_reserved_qty')

    @api.multi
    def _compute_reserved_qty(self):
        quants = self.quant_ids.filtered(
            lambda q: q.location_id.usage in ['internal', 'transit'])
        self.reserved_quantity = sum(quants.mapped('reserved_quantity'))

    @api.multi
    def action_related_picking(self):
        self.ensure_one()
        move_lines = self.env['stock.move.line'].search(
            [('lot_id', '=', self.id)])
        picking_ids = move_lines.mapped('picking_id').ids
        action = self.env.ref('stock.action_picking_tree_all').read()[0]
        action['domain'] = [('id', 'in', picking_ids)]
        return action

    @api.multi
    def action_related_mo(self):
        self.ensure_one()
        move_lines = self.env['stock.move.line'].search(
            [('lot_id', '=', self.id)])
        mo = move_lines.mapped('production_id').ids
        action = self.env.ref('mrp.mrp_production_action').read()[0]
        action['domain'] = [('id', 'in', mo)]
        action['context'] = False
        return action
