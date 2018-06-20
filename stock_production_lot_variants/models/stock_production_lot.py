# Copyright 2018 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
from odoo import api, fields, models, _


class StockProductionLot(models.Model):
    _inherit = ['stock.production.lot', 'product.configurator']
    _name = 'stock.production.lot'

    attribute_value_ids = fields.Many2many(
        'product.attribute.value', string='Attributes',
        compute='_compute_attribute_value_ids')

    @api.depends('product_attribute_ids')
    def _compute_attribute_value_ids(self):
        self.attribute_value_ids = self.product_attribute_ids.mapped(
            'value_id')

    @api.model
    def _build_attributes_domain(self, product_id,
                                 product_attributes):
        domain = []
        cont = 0
        value_obj = self.env['product.attribute.value']
        if product_id:
            domain.append(('product_id', '=', product_id.id))
            for attr_line in product_attributes:
                if isinstance(attr_line, dict):
                    value_id = attr_line.get('value_id')
                else:
                    value_id = attr_line.value_id.id
                if value_id:
                    domain.append(('attribute_value_ids', '=', value_id))
                    cont += 1
        return domain, cont

    @api.multi
    def _find_lot(self, product_id, attributes):
        if product_id:
            domain, cont = self._build_attributes_domain(
                product_id, attributes)
            lots = self.search(domain)
            # Filter the product with the exact number of attributes values
            for lot in lots:
                if len(lot.attribute_value_ids) == cont:
                    return lot.id
        return False

    @api.multi
    def _create_lot(self, product_id, attributes):
        attribute_lines = []
        template_id = product_id.product_tmpl_id

        lot_id = self.create({
            'product_tmpl_id': template_id.id,
            'product_id': product_id.id,
            'name': 'LOT//' + product_id.name
        })
        for attribute in attributes:
            attribute_lines.append(
                (0, 0, {
                    'owner_id': lot_id.id,
                    'owner_model': 'stock.production.lot',
                    'product_tmpl_id': template_id.id,

                    'attribute_id': attribute.attribute_id.id,
                    'value_id': attribute.value_id.id,
                    'custom_value': attribute.custom_value
                }))
        lot_id.write({'product_attribute_ids': attribute_lines})
        return lot_id
