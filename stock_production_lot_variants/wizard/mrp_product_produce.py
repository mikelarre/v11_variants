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
