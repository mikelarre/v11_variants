# Copyright 2018 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, exceptions, fields, models, _


class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"

    diameter = fields.Float(string='Diameter')
    length = fields.Float(string='Length')
    material_type = fields.Many2one(comodel_name='product.material',
                                    string='Material type')
    casting = fields.Char(string='Casting')
    finish = fields.Many2one(comodel_name='material.finish', string='Finish')
    homologation_type = fields.Many2one(comodel_name='homologation.type')
    division_line_ids = fields.One2many(comodel_name='division.line',
                                        inverse_name='lot_id',
                                        string='Division lines')
    weight = fields.Float(string="Weight", compute="_compute_weight")

    @api.depends("length", "product_id.weight", "product_id.volume")
    def _compute_weight(self):
        self.weight = self.product_id.calculate_weight(self.length)

    @api.multi
    def split_lots(self):
        if self.product_qty <= sum(self.division_line_ids.mapped('qty')):
            for lot in self:
                lot.division_line_ids.create_lot()
        else:
            raise exceptions.Warning(_('Not enough product quantity'))


class ProductMaterial(models.Model):
    _name = "product.material"

    name = fields.Char(string='Code')
    description = fields.Char(string='Description')


class HomologationType(models.Model):
    _name = "homologation.type"

    name = fields.Char(string="Code")
    description = fields.Char(string='Description')


class MaterialFinish(models.Model):
    _name = "material.finish"

    name = fields.Char(string="Code")
    description = fields.Char(string="Description")


class DivisionLine(models.Model):
    _name = "division.line"

    name = fields.Char(string='Nº')
    lot_id = fields.Many2one(comodel_name='stock.production.lot',
                             string='Lot')
    qty = fields.Integer(string="Quantity")
    length = fields.Integer(string="Length")
    created_lot_id = fields.Many2one(
        comodel_name='stock.production.lot', string='Created lot')

    @api.multi
    def create_lot(self):
        for line in self:
            lot = self.lot_id.copy({'product_qty': self.qty, 'length':
                self.length})

