# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
# from openerp import models, fields, api
# import cStringIO
# from openerp import tools
from openerp import pooler, SUPERUSER_ID
import logging
_logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    pool = pooler.get_pool(cr.dbname)
    lang_read = pool['res.lang'].search_read(
        cr, SUPERUSER_ID, [
            '&', ('active', '=', True), ('translatable', '=', True),
            ('code', '!=', 'en_US')], ['code'], limit=1)
    if not lang_read:
        # no need to sync translations, only en_us language
        return True
    lang_code = lang_read[0]['code']
    models_fields = [
        ('product.template', 'description_sale'),
        ('product.template', 'description_purchase'),
        ('product.template', 'description'),
        ('product.template', 'name'),
        ('product.category', 'name'),
        ('product.attribute', 'name'),
        ('product.attribute.value', 'name'),
        ('product.uom.categ', 'name'),
        ('product.uom', 'name'),
        ('product.ul', 'name'),
    ]
    for model_name, field_name in models_fields:
        sync_field(cr, SUPERUSER_ID, lang_code, model_name, field_name)


def sync_field(cr, uid, lang_code, model_name, field_name):
    _logger.info('Syncking translations for model %s, field %s' % (
        model_name, field_name))
    pool = pooler.get_pool(cr.dbname)
    translations = pool['ir.translation'].search_read(
        cr, SUPERUSER_ID, [
            ('name', '=', '%s,%s' % (model_name, field_name)),
            ('type', '=', 'model'),
            ('lang', '=', 'es_AR')],
        ['res_id', 'value'])
    for translation in translations:
        table = model_name.replace('.', '_')
        value = translation['value']
        res_id = translation['res_id']
        # just in case some constraint block de renaiming
        # try:
        # no nos anduvo, arrojamos el error y listo
        cr.execute(
            "UPDATE %s SET %s='%s' WHERE id=%s" % (
                table,
                field_name,
                value,
                res_id
            ))
        # except Exception, e:
        #     _logger.warning(
        #         'Could not update translation on table %s for res_id %s, '
        #         'field %s, with value %s. This is what we get %s' % (
        #             table, res_id, field_name, value, e))
