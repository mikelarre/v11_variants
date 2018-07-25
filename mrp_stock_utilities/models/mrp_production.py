# Copyright 2018 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'


    @api.multi
    def write(self, values):
        move_lines = self.env['stock.move.line']
        move_lines_after = self.env['stock.move.line']
        for production in self:
            move_lines |= production.move_raw_ids.mapped(
                'active_move_line_ids')
        res = super(MrpProduction, self).write(values)
        for production in self:
            move_lines_after = production.move_raw_ids.mapped(
                'active_move_line_ids')
        new_move_lines = move_lines_after - move_lines
        quant_obj = self.env['stock.quant']
        for line in new_move_lines:
            product_id = line.product_id
            location_id = line.location_id
            lot_id = line.lot_id
            package_id = line.package_id
            quantity = line.product_uom_qty
            owner_id = line.owner_id
            quant = quant_obj.search(
                [('product_id', '=', product_id.id),
                 ('location_id', '=', location_id.id),
                 ('lot_id', '=', lot_id.id),
                 ('package_id', '=', package_id.id),
                 ('owner_id', '=', owner_id.id)]
            )
            if len(quant) == 1:
                res = quant._update_reserved_quantity(product_id, location_id,
                                                quantity,
                                                lot_id=lot_id,
                                                package_id=package_id,
                                                owner_id=owner_id)
                for value in res:
                    value[0].reserved_quantity = value[1]
