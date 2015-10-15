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
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
import time
from calendar import monthrange
from datetime import datetime

from openerp.addons.global_edu.utils.date import week_of_month


class AttendanceSheet(models.Model):
    """
    Class attendance Sheet
    """
    _description = 'Hoja de Asistencia'
    _name = 'attendance.sheet'

    @api.one
    @api.depends('student_ids')
    def _total(self):
        count = 0
        if self.student_ids:
            for att in self.student_ids:
                count += 1
            self.total_student = count
        else:
            self.total_student = count

    @api.one
    @api.depends('student_ids')
    def _present(self):
        count = 0
        if self.student_ids:
            for att in self.student_ids:
                if att.is_present == True:
                    count += 1
            self.total_presence = count
        else:
            self.total_presence = count

    @api.one
    @api.depends('student_ids')
    def _absent(self):
        count_fail = 0
        if self.student_ids:
            for att in self.student_ids:
                if att.is_present == False:
                    count_fail += 1
            self.total_absent = count_fail
        else:
            self.total_absent = count_fail

    @api.one
    @api.depends('student_ids')
    def _late(self):
        count_fail = 0
        if self.student_ids:
            for att in self.student_ids:
                if att.is_late == True:
                    count_fail += 1
            self.total_late = count_fail
        else:
            self.total_late = count_fail

    date = fields.Date('Fecha', default=lambda *a: time.strftime('%Y-%m-%d'))
    name = fields.Char('Semana', size=32)
    course_id = fields.Many2one('global.course', 'Horario', required=True)
    level_id = fields.Many2one('global.level', 'Nivel', required=True)
    student_ids = fields.One2many('daily.attendance.line', 'sheet_id', 'Asistencia')
    # user_id = fields.Many2one('hr.employee', 'Profesor')
    # Totals
    total_student = fields.Integer(compute="_total", method=True, store=True, string='Total de Estudiantes')
    total_presence = fields.Integer(compute="_present", method=True, store=True, string='Estudiantes Presentes')
    total_absent = fields.Integer(compute="_absent", method=True, store=True, string='Estudiantes Ausentes')
    total_late = fields.Integer(compute="_late", method=True, store=True, string='Estudiantes Retrasados')

    @api.model
    def create(self, vals):
        child = ''
        if vals:
            if vals.get('date', False):
                vals['name'] = week_of_month(datetime.strptime(vals['date'], '%Y-%m-%d'))
            if 'student_ids' in vals.keys():
                child = vals.pop('student_ids')
        ret_val = super(AttendanceSheet, self).create(vals)
        if child != '':
            ret_val.write({'student_ids': child})
        return ret_val

    @api.multi
    def onchange_course_id(self, course_id):
        res={}
        student_list = []
        stud_obj = self.env['global.student']
        if course_id:
            self._cr.execute("""select id from global_student where course_id=%s""",(course_id,))
            stud_ids = self._cr.fetchall()
            for stud_id in stud_ids:
                student_ids = stud_obj.browse(stud_id)
                student_list.append({'identification':student_ids.identification,'stud_id':stud_id})
            res.update({'value': {'student_ids': student_list}})
        return res


class AttendanceLine(models.Model):
    """
    Defining Class Attendance Sheet Line Information
    """
    _description = 'Asistencia Diaria'
    _name = 'daily.attendance.line'
    _order = 'identification'
    _rec_name = 'identification'

    identification = fields.Integer('Identificación', required=True, help='Identificación')
    sheet_id = fields.Many2one('attendance.sheet', 'Hoja de Asistencia')
    stud_id = fields.Many2one('global.student', 'Estudiante', required=True)
    is_present = fields.Boolean('Presente')
    is_late = fields.Boolean('Atrasado')
