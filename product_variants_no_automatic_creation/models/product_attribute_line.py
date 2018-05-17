# Copyright 2015 Oihane Crucelaegui - AvanzOSC
# Copyright 2015-2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models


class ProductAttributeLine(models.Model):
    _inherit = 'product.attribute.line'

    _sql_constraints = [
        ('product_attribute_uniq', 'unique(product_tmpl_id, attribute_id)',
         'The attribute already exists for this product')
    ]
