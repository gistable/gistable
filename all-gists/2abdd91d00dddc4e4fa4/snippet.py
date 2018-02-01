[program:odoo-longpolling]
command=/usr/local/src/odoo/openerp-gevent --config=/etc/odoo/odoo-server.conf --logfile=/var/log/odoo/odoo-server-longpolling.log
autostart=true
autorestart=true
user={{ODOO_USER}}
directory=/opt/{{ODOO_USER}}/
environment = HOME="/opt/{{ODOO_USER}}/",USER="{{ODOO_USER}}"

