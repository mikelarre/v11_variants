# Copyright 2018 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models
from odoo.exceptions import UserError

class MrpProductProduce(models.TransientModel):
    _inherit = 'mrp.product.produce'

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        lot_obj = self.env['stock.production.lot']
        stock_obj = self.env['stock.move']
        product_obj = self.env['product.product']
        for line in res.get('produce_line_ids', []):
            line = line[2]
            if not line.get('lot_id'):
                product_id = product_obj.browse(line['product_id'])
                move = stock_obj.browse(line['move_id'])
                production_product_line = move.production_product_line_id
                attributes = production_product_line.product_attribute_ids
                line['lot_id'] = lot_obj._find_lot(product_id, attributes)
        return res

    @api.multi
    def check_finished_move_lots(self):
        try:
            return super().check_finished_move_lots()
        except UserError:
            lot_obj = self.env['stock.production.lot']
            attributes = self.production_id.product_attribute_ids
            self.lot_id = lot_obj._create_lot(self.product_id, attributes)
            return super().check_finished_move_lots()

    # @api.multi
    # def check_finished_move_lots(self):
    #     produce_move = self.production_id.move_finished_ids.filtered(lambda x: x.product_id == self.product_id and x.state not in ('done', 'cancel'))
    #     if produce_move and produce_move.product_id.tracking != 'none':
    #         if not self.lot_id:
    #             raise UserError(_('You need to provide a lot for the finished product'))
    #         existing_move_line = produce_move.move_line_ids.filtered(lambda x: x.lot_id == self.lot_id)
    #         if existing_move_line:
    #             if self.product_id.tracking == 'serial':
    #                 raise UserError(_('You cannot produce the same serial number twice.'))
    #             existing_move_line.product_uom_qty += self.product_qty
    #             existing_move_line.qty_done += self.product_qty
    #         else:
    #             vals = {
    #               'move_id': produce_move.id,
    #               'product_id': produce_move.product_id.id,
    #               'production_id': self.production_id.id,
    #               'product_uom_qty': self.product_qty,
    #               'product_uom_id': produce_move.product_uom.id,
    #               'qty_done': self.product_qty,
    #               'lot_id': self.lot_id.id,
    #               'location_id': produce_move.location_id.id,
    #               'location_dest_id': produce_move.location_dest_id.id,
    #             }
    #             self.env['stock.move.line'].create(vals)