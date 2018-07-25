# Copyright 2018 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo.addons.mrp.tests.common import TestMrpCommon


class TestMrpStockUtilities(TestMrpCommon):


    def test_quant_reservation(self):
        mo, bom_1, product_to_build, product_to_use_1, product_to_use_2 = \
            self.generate_mo(tracking_final='lot', tracking_base_1='lot',
                         tracking_base_2='lot', qty_final=5, qty_base_1=4,
                         qty_base_2=1)
        location = self.ref('stock.stock_location_14')
        mo.move_raw_ids.mapped('active_move_line_ids')
        move = mo.move_raw_ids[0]
        product_id = move.product_id.id
        lot_id = self.env['stock.production.lot'].create({
            'name': '0000000000001',
            'product_id': product_id,
        })
        quant1 = self.env['stock.quant'].create({
            'product_id': product_id,
            'location_id': location.id,
            'quantity': 10.0,
            'lot_id': lot_id})
        mo.move_raw_ids[0].active_move_line_ids = [(0, 0, {
            'location_id': location.id, 'product_id': product_id,
            'lot_id': lot_id,
        })]


        pass
