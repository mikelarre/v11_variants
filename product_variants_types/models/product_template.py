# Copyright 2015 Oihane Crucelaegui - AvanzOSC
# Copyright 2015-2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _get_product_attributes_dict(self):
        product_attributes, template_attributes = super(
            ProductTemplate, self)._get_product_attributes_dict()
        for attribute in product_attributes + template_attributes:
            line = self.env['product.attribute.line'].search(
                [('attribute_id', '=', attribute['attribute_id']),
                 ('product_tmpl_id', '=', self.id)], limit=1)
            attribute.update({'value_id': line.default.id})
        return product_attributes, template_attributes
