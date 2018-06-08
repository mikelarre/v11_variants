# Copyright 2015 Oihane Crucelaegui - AvanzOSC
# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, models


class ProcurementOrder(models.Model):
    _inherit = 'procurement.rule'

    @api.model
    def _prepare_mo_vals(self, product_id, product_qty, product_uom,
                         location_id, name, origin, values, bom):
        result = super(ProcurementOrder, self)._prepare_mo_vals(
            product_id, product_qty, product_uom, location_id, name, origin,
            values, bom)
        result['product_tmpl_id'] = product_id.product_tmpl_id.id
        product_attribute_ids = \
            product_id._get_product_attributes_values_dict()
        result['product_attribute_ids'] = list(map(
            lambda x: (0, 0, x), product_attribute_ids))
        for val in result['product_attribute_ids']:
            val = val[2]
            val['product_tmpl_id'] = product_id.product_tmpl_id.id
            val['owner_model'] = 'mrp.production'
            try:
                move_dest_id = values.get('move_dest_ids', self.env[
                    'stock.move'])
                sale_line = move_dest_id.sale_line_id
                attr_lines = sale_line.product_attribute_ids.filtered(
                    lambda x: x.attribute_id.id == val['attribute_id'])
                if attr_lines:
                    val['custom_value'] = attr_lines[:1].custom_value
            except Exception:
                pass
        return result
