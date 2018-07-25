# Copyright 2018 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, exceptions, fields, models, _


class StockMove(models.Model):
    _inherit = 'stock.move'

    line_lots_ids = fields.Many2many(comodel_name="stock.production.lot",
                                     compute="_compute_line_lots")

    @api.depends('active_move_line_ids')
    def _compute_line_lots(self):
        for line in self:
            line.line_lots_ids = line.active_move_line_ids.mapped('lot_id')
