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

{
    'name': 'Gestion Colegio Global',
    'version': '0.0.1',
    'category': 'Education',
    "sequence": 3,
    'summary': 'Gestiona estudiantes, pagos, asistencia y notas',
    'complexity': "easy",
    'description': """
        Este modulo gestiona los procesos del proyecto educativo Global del Ecuador,
        cubriendo las siguientes áreas:
            * Admisiones
            * Pagos
            * Cursos
            * Profesores
            * Notas
            * Asistencia
    """,
    'author': 'Dairon Medina C.',
    'website': 'http://www.gydsystems.com',
    'depends': ['base_action_rule',
                'base_setup', 'mail', 'board',
                'web_tip',
                ],
    'data': [
        'views/student.xml',
        'views/attendance.xml',
        'views/evaluation.xml',
        'views/configuration.xml',
        'views/menus.xml',
        'views/branding.xml',
    ],
    'demo': [],
    'css': [
        'static/src/css/style.css',
    ],
    'qweb': [
        'static/src/xml/skype.xml',
    ],
    'js': [
        'static/src/js/skype.js'
    ],
    'images': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
