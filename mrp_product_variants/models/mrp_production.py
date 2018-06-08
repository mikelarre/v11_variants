# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import models, fields, api, exceptions, _


class MrpProduction(models.Model):
    _inherit = ['mrp.production', 'product.configurator']
    _name = 'mrp.production'

    product_id = fields.Many2one(required=False)

    @api.model
    def create(self, values):
        value_obj = self.env['product.attribute.value']
        for line in values.get('product_attribute_ids', []):
            value = value_obj.browse(line[2]['value_id'])
            line[2].update({'attribute_id': value.attribute_id.id})
        return super(MrpProduction, self).create(values)

    @api.multi
    def write(self, values):
        value_obj = self.env['product.attribute.value']
        for line in values.get('product_attribute_ids', []):
            if line[0] == 0:
                value = value_obj.browse(line[2]['value_id'])
                line[2].update({'attribute_id': value.attribute_id.id})

        return super(MrpProduction, self).write(values)

    @api.multi
    def bom_id_change(self, bom_id):
        res = super(MrpProduction, self).bom_id_change(bom_id)
        if bom_id:
            bom = self.env['mrp.bom'].browse(bom_id)
            if bom.product_id:
                res['value']['product_id'] = bom.product_id.id
            if 'domain' not in res:
                res['domain'] = {}
            res['domain']['routing_id'] = [('id', '=', bom.routing_id.id)]
        return res

    @api.multi
    def onchange_product_qty(self, product_id, product_qty):
        res = self.product_id_change(product_id, product_qty=product_qty)
        if res['value'].get('product_attribute_ids'):
            del res['value']['product_attribute_ids']
        return res

    @api.multi
    def product_id_change(self, product_id, product_qty=0):
        res = super(MrpProduction, self).product_id_change(
            product_id, product_qty=product_qty)
        new_value = self.onchange_product_id_product_configurator_old_api(
            product_id=product_id)
        value = res.setdefault('value', {})
        value.update(new_value)
        if 'name' in value:
            del value['name']
        return res

    @api.multi
    @api.onchange('product_id')
    def onchange_product_id_product_configurator(self):
        name = self.name
        res = super(MrpProduction,
                    self).onchange_product_id_product_configurator()
        self.name = name
        return res

    @api.multi
    @api.onchange('product_tmpl_id')
    def onchange_product_tmpl_id(self):
        res = super(MrpProduction, self).onchange_product_tmpl_id()
        self.product_uom = self.product_tmpl_id.uom_id
        self.bom_id = self.env['mrp.bom']._bom_find(
            product_tmpl=self.product_tmpl_id)
        self.routing_id = self.bom_id.routing_id
        res['domain'].update({
            'bom_id': [('product_tmpl_id', '=', self.product_tmpl_id.id)]})
        return res

    @api.multi
    @api.onchange('product_attribute_ids')
    def onchange_product_attribute_ids(self):
        name = self.name
        res = super(MrpProduction, self).onchange_product_attribute_ids()
        self.name = name
        return res

    @api.multi
    def _action_compute_lines(self, properties=None):
        results = self._action_compute_lines_variants(properties=properties)
        return results

    @api.multi
    def _action_compute_lines_variants(self, properties=None):
        """ Compute product_lines and workcenter_lines from BoM structure
        @return: product_lines
        """
        # if properties is None:
        #     properties = []
        results = []
        uom_obj = self.env['product.uom']
        prod_line_obj = self.env['mrp.production.product.line']
#        workcenter_line_obj = self.env['mrp.production.workcenter.line']
        for production in self:
            bom_obj = self.env['mrp.bom'].with_context(production=production)
            #  unlink product_lines
            production.product_lines.unlink()
            #  unlink workcenter_lines
            #production.workcenter_lines.unlink()
            #  search BoM structure and route
            bom_point = production.bom_id
            bom_id = production.bom_id.id
            if not bom_point:
                if not production.product_id:
                    bom_id = bom_obj._bom_find(
                        product_tmpl=production.product_tmpl_id.id,
                        properties=properties)
                else:
                    bom_id = bom_obj._bom_find(
                        product_id=production.product_id.id,
                        properties=properties)
                if bom_id:
                    bom_point = bom_obj.browse(bom_id)
                    routing_id = bom_point.routing_id.id or False
                    self.write({'bom_id': bom_id, 'routing_id': routing_id})

            if not bom_id:
                raise exceptions.Warning(
                    _('Error! Cannot find a bill of material for this'
                      ' product.'))
            # get components and workcenter_lines from BoM structure
            factor = self.product_uom_id._compute_quantity(
                self.product_qty, bom_point.product_uom_id)
            # product_lines, workcenter_lines
            # results, results2 = bom_point.with_context(
            #     production=production)._bom_explode(
            #         production.product_id, factor / bom_point.product_qty,
            #         properties, routing_id=production.routing_id.id)
            boms_done, lines_done = bom_point.explode(self.product_id, factor /
                                                      bom_point.product_qty)
            #  reset product_lines in production order
            product_obj = self.env['product.product']
            for line in lines_done:
                line_data = line[1]
                bom_line = line[0]

                product_tmpl = bom_line.product_tmpl_id
                product_attribute_ids = (
                    product_tmpl._get_product_attribute_ids_inherit_dict(
                        production.product_attribute_ids))
                product = bom_line.product_id or product_obj._product_find(
                        product_tmpl, product_attribute_ids) or product_obj
                for attr_line in product_attribute_ids:
                    attr_line['owner_model'] = 'mrp.production.product.line'
                    attr_line['product_tmpl_id'] = product_tmpl.id
                prod_line = {
                    'name': product.name,
                    'product_tmpl_id': product_tmpl.id,
                    'product_id': product.id,
                    'product_attribute_ids': [
                        (0, 0, x) for x in product_attribute_ids],
                    'product_qty': line_data['qty'],
                    'bom_line_id': bom_line.id,
                    'product_uom': bom_line.product_uom_id.id,
                    'production_id': production.id,
                }
                prod_line_obj.create(prod_line)
            #  reset workcenter_lines in production order
            # for line in results2:
            #     line['production_id'] = production.id
            #     workcenter_line_obj.create(line)
        return lines_done

    @api.model
    def _make_production_produce_line(self, production):
        if not production.product_tmpl_id and not production.product_id:
            raise exceptions.Warning(
                _("You can not confirm without product or variant defined."))
        if not production.product_id:
            product_obj = self.env['product.product']
            att_values_ids = [
                attr_line.value_id and attr_line.value_id.id or False
                for attr_line in production.product_attribute_ids]
            domain = [('product_tmpl_id', '=', production.product_tmpl_id.id)]
            for value in att_values_ids:
                if not value:
                    raise exceptions.Warning(
                        _("You can not confirm before configuring all"
                          " attribute values."))
                domain.append(('attribute_value_ids', '=', value))
            product = product_obj.search(domain)
            if not product:
                product = product_obj.create(
                    {'product_tmpl_id': production.product_tmpl_id.id,
                     'attribute_value_ids': [(6, 0, att_values_ids)]})
            production.product_id = product
        return super(MrpProduction,
                     self)._make_production_produce_line(production)

    @api.model
    def _make_production_consume_line(self, line):
        if not line.product_id:
            product_obj = self.env['product.product']
            att_values_ids = [
                attr_line.value_id and attr_line.value_id.id or False
                for attr_line in line.product_attribute_ids]
            domain = [('product_tmpl_id', '=', line.product_tmpl_id.id)]
            for value in att_values_ids:
                if not value:
                    raise exceptions.Warning(
                        _("You can not confirm before configuring all"
                          " attribute values."))
                domain.append(('attribute_value_ids', '=', value))
            product = product_obj.search(domain)
            if not product:
                product = product_obj.create(
                    {'product_tmpl_id': line.product_tmpl_id.id,
                     'attribute_value_ids': [(6, 0, att_values_ids)]})
            line.product_id = product
        return super(MrpProduction, self)._make_production_consume_line(line)

    @api.model
    def _prepare_lines(self, production, properties=None):
        obj = self.with_context(production=production)
        return super(MrpProduction, obj)._prepare_lines(
            production, properties=properties)


class MrpProductionProductLine(models.Model):
    _inherit = ['mrp.production.product.line', 'product.configurator']
    _name = 'mrp.production.product.line'

    product_id = fields.Many2one(required=False)

    @api.multi
    @api.onchange('product_tmpl_id')
    def onchange_product_tmpl_id(self):
        res = super(MrpProductionProductLine, self).onchange_product_tmpl_id()
        self.name = self.product_id.name or self.product_tmpl_id.name
        self.product_uom = self.product_tmpl_id.uom_id
        return res
