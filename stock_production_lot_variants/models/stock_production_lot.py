# Copyright 2018 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models, _


class StockProductionLot(models.Model):
    _inherit = ['stock.production.lot', 'product.configurator']
    _name = 'stock.production.lot'

