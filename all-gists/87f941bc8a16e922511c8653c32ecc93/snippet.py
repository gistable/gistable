#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to bootstrap an Odoo database (8.0)."""
import odoorpc

# Odoo connection
SUPER_PWD = 'admin'
HOST = 'localhost'
PORT = 8069
DB = 'my_db'
USER = 'admin'
PWD = 'password'
LANG = 'en_US'
COMPANY = u"ABF OSIELL"
TIMEZONE = u"Europe/Paris"
MODULES_TO_INSTALL = [
    'sale',
    'purchase',
    'account_accountant',
    'l10n_fr',
]


def get_session(login=True):
    odoo = odoorpc.ODOO(HOST, port=PORT)
    odoo.config['timeout'] = None
    if login:
        odoo.login(DB, USER, PWD)
    return odoo


def create_database():
    odoo = get_session(login=False)
    if DB not in odoo.db.list():
        odoo.db.create(
            SUPER_PWD, DB, demo=False, lang=LANG, admin_password=PWD)


def uninstall_modules():
    odoo = get_session()
    Module = odoo.env['ir.module.module']
    module_names = ['im_chat', 'im_livechat', 'im_odoo_support']
    for module_name in module_names:
        module_ids = Module.search(
            [('name', '=', module_name),
             ('state', 'in', ['installed', 'to upgrade',
                              'to remove', 'to install'])])
        if module_ids:
            Module.button_immediate_uninstall(module_ids)


def update_company():
    odoo = get_session()
    company = odoo.env.user.company_id
    company.name = COMPANY


def update_admin_user():
    odoo = get_session()
    admin = odoo.env.user
    group_technical_feature = odoo.env.ref('base.group_no_one')
    group_sale_manager = odoo.env.ref('base.group_sale_manager')
    if group_technical_feature not in admin.groups_id:
        admin.groups_id += group_technical_feature
    if group_sale_manager not in admin.groups_id:
        admin.groups_id += group_sale_manager
    if not admin.tz:
        admin.tz = TIMEZONE


def install_modules():
    odoo = get_session()
    # Installation
    Module = odoo.env['ir.module.module']
    for module_name in MODULES_TO_INSTALL:
        module_ids = Module.search(
            [('name', '=', module_name),
             ('state', 'not in', ['installed', 'to upgrade'])])
        if module_ids:
            Module.button_immediate_install(module_ids)


def configure_account():
    odoo = get_session()
    #   account.installer
    Wizard = odoo.env['account.installer']
    config = Wizard.default_get(list(Wizard.fields_get()))
    config['charts'] = 'l10n_fr'
    wiz_id = Wizard.create(config)
    Wizard.action_next([wiz_id])
    #   wizard.multi.charts.accounts
    Wizard = odoo.env['wizard.multi.charts.accounts']
    config = Wizard.default_get(list(Wizard.fields_get()))
    config['chart_template_id'] = odoo.env.ref(
        'l10n_fr.l10n_fr_pcg_chart_template').id
    values = Wizard.onchange_chart_template_id(
        [], config['chart_template_id'])['value']
    config.update(values)
    config['sale_tax'] = odoo.env.ref('l10n_fr.tva_normale').id
    config['purchase_tax'] = odoo.env.ref('l10n_fr.tva_acq_normale').id
    config['code_digits'] = 8
    del config['bank_accounts_id']
    wiz_id = Wizard.create(config)
    try:
        Wizard.action_next([wiz_id])
    except odoorpc.error.RPCError:
        print "Accounting already configured"


def main():
    create_database()
    uninstall_modules()
    update_company()
    update_admin_user()
    install_modules()
    configure_account()


if __name__ == '__main__':
    main()