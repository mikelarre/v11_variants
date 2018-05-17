# Copyright 2014-2018 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    "name": "MRP - Product variants",
    "summary": "Customized product in manufacturing",
    "version": "11.0.1.0.0",
    "license": "AGPL-3",
    "depends": [
        "product",
        "product_variants_no_automatic_creation",
    ],
    "author": "OdooMRP team, "
              "AvanzOSC, "
              "Tecnativa, "
              "Serv. Tecnol. Avanzados - Pedro M. Baeza",
    "contributors": [
        "Oihane Crucelaegui <oihanecrucelaegi@avanzosc.es>",
        "Pedro M. Baeza <pedro.baeza@serviciosbaeza.com>",
        "Ana Juaristi <ajuaristio@gmail.com>",
    ],
    "category": "Manufacturing",
    "website": "http://www.odoomrp.com",
    "data": [
        "views/mrp_production_view.xml",
        "views/product_attribute_view.xml",
    ],
    "installable": True,
    "post_init_hook": "assign_product_template",
}
