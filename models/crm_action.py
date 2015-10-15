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
from openerp import models, fields, api


class CrmAction(models.Model):
    """

    """
    _name = 'global.crm.action'
    _description = 'Student Action'

    def search_action_types(self):
        return self.env['crm.action.type'].search(
            [('is_active', '=', True)], order='priority')

    def default_action_type(self):
        action_types = self.search_action_types()
        return action_types and action_types[0].id or False

    student_id = fields.Many2one('global.student', string='Student')
    date = fields.Date('Date', required=True, default=fields.Date.context_today)
    user_id = fields.Many2one('res.users', string='User', required=True, default=lambda self: self.env.user)
    action_type = fields.Many2one('crm.action.type', string='Type', required=True, default=default_action_type)
    details = fields.Text('Details')
