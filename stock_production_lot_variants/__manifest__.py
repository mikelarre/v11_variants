# Copyright 2018 Mikel Arregi Etxaniz - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html
{
    "name": "Mrp production lot variants",
    "version": "11.0.2.0.0",
    "license": "AGPL-3",
    "depends": [
        "stock", "product_variants_no_automatic_creation",
    ],
    "author": "AvanzOSC",
    "website": "http://www.avanzosc.es",
    "category": "Manufacturing",
    "data": [
         "data/ir_sequence_data.xml",
         "views/stock_production_lot_views.xml",
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
