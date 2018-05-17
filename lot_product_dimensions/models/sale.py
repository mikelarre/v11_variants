# Copyright 2018 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    diameter = fields.Float(string='Diameter')
    length = fields.Float(string='Length')
    material_type = fields.Many2one(comodel_name='product.material',
                                    string='Material type')
    casting = fields.Char(string='Casting')
    finish = fields.Many2one(comodel_name='material.finish', string='Finish')
    homologation_type = fields.Many2one(comodel_name='homologation.type')
    weight = fields.Float(string="Weight", compute="_compute_weight")

    @api.depends("length", "product_id.weight", "product_id.volume")
    def _compute_weight(self):
        self.weight = self.product_id.calculate_weight(self.length)
