# -*- coding: utf-8 -*-
###############################################################################
#
#    G&D Systems. All rights reserved.
#    Copyright (C) 2015 G&D Systems(<http://www.gydsystems.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
import openerp
from openerp import http, SUPERUSER_ID
from openerp.addons.web.controllers.main import Binary
import functools
from openerp.http import request, serialize_exception as _serialize_exception
from openerp.modules import get_module_resource
from cStringIO import StringIO
db_monodb = http.db_monodb


class BinaryCustom(Binary):
    @http.route([
        '/web/binary/company_logo',
        '/logo',
        '/logo.png',
    ], type='http', auth="none")
    def company_logo(self, dbname=None, company_id=None, **kw):
        imgname = 'logo.png'
        placeholder = functools.partial(get_module_resource, 'global_edu', 'static', 'src', 'img')
        uid = None
        if request.session.db:
            dbname = request.session.db
            uid = request.session.uid
        elif dbname is None:
            dbname = db_monodb()

        if not uid:
            uid = openerp.SUPERUSER_ID

        if not dbname:
            response = http.send_file(placeholder(imgname))
        else:
            try:
                # create an empty registry
                registry = openerp.modules.registry.Registry(dbname)
                with registry.cursor() as cr:
                    if company_id:
                        cr.execute("""SELECT c.logo_web, c.write_date
                                        FROM res_company c
                                       WHERE c.id = %s
                               """, (company_id,))
                    else:
                        cr.execute("""SELECT c.logo_web, c.write_date
                                        FROM res_users u
                                   LEFT JOIN res_company c
                                          ON c.id = u.company_id
                                       WHERE u.id = %s
                               """, (uid,))
                    row = cr.fetchone()
                    if row and row[0]:
                        image_data = StringIO(str(row[0]).decode('base64'))
                        response = http.send_file(image_data, filename=imgname, mtime=row[1])
                    else:
                        response = http.send_file(placeholder('logo.png'))
            except Exception, e:
                raise e
                response = http.send_file(placeholder(imgname))

        return response