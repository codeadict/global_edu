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
from openerp.exceptions import except_orm, Warning, RedirectWarning, ValidationError
import time
from calendar import monthrange
from datetime import datetime
from openerp.addons.global_edu.utils.date import week_of_month

CYCLE_CHOICES = [
    ('A', 'A'),
    ('B', 'B')
]


class HomeworkSheet(models.Model):
    """
    Class homework Sheet
    """
    _description = 'Evaluación Tarea'
    _name = 'homework.sheet'

    date = fields.Date('Fecha', default=lambda *a: time.strftime('%Y-%m-%d'))
    name = fields.Char('Semana', size=32)
    course_id = fields.Many2one('global.course', 'Horario', required=True)
    level_id = fields.Many2one('global.level', 'Nivel', required=True)
    student_ids = fields.One2many('homework.line', 'sheet_id', 'Asistencia')
    # user_id = fields.Many2one('hr.employee', 'Profesor')

    @api.model
    def create(self, vals):
        child = ''
        if vals:
            if vals.get('date', False):
                vals['name'] = week_of_month(datetime.strptime(vals['date'], '%Y-%m-%d'))
            if 'student_ids' in vals.keys():
                child = vals.pop('student_ids')
        ret_val = super(HomeworkSheet, self).create(vals)
        if child != '':
            ret_val.write({'student_ids': child})
        return ret_val

    @api.multi
    def onchange_course_id(self, course_id):
        res = {}
        student_list = []
        stud_obj = self.env['global.student']
        if course_id:
            self._cr.execute("""select id from global_student where course_id=%s""", (course_id,))
            stud_ids = self._cr.fetchall()
            for stud_id in stud_ids:
                student_ids = stud_obj.browse(stud_id)
                student_list.append({'identification': student_ids.identification, 'stud_id': stud_id})
            res.update({'value': {'student_ids': student_list}})
        return res


class AttendanceLine(models.Model):
    """
    Defining Class Attendance Sheet Line Information
    """
    _description = 'Asistencia Diaria'
    _name = 'homework.line'
    _order = 'identification'
    _rec_name = 'identification'

    identification = fields.Integer('Identificación', required=True, help='Identificación')
    sheet_id = fields.Many2one('homework.sheet', 'Homework')
    stud_id = fields.Many2one('global.student', 'Estudiante', required=True)
    rating = fields.Float('Nota', required=True)


class GeneralCourseSheet(models.Model):
    """
    Class homework Sheet
    """
    _description = 'Evaluación General'
    _name = 'qualification.sheet'
    _rec_name = 'course_id'

    course_id = fields.Many2one('global.course', 'Horario', required=True)
    level_id = fields.Many2one('global.level', 'Nivel', required=True)
    cycle = fields.Selection(CYCLE_CHOICES, 'Ciclo', required=True)
    seminary_ammount = fields.Integer('Candidad de Seminarios', required=True)
    quiz_ids = fields.One2many('quiz.line', 'sheet_id', 'Quizes')
    homework_ids = fields.One2many('hw.line', 'sheet_id', 'Quizes')
    seminary_ids = fields.One2many('seminary.line', 'sheet_id', 'Quizes')
    test_ids = fields.One2many('test.line', 'sheet_id', 'Quizes')
    # user_id = fields.Many2one('hr.employee', 'Profesor')

    @api.model
    def create(self, vals):
        child = ''
        hw = ''
        sem = ''
        test = ''
        if vals:
            if 'quiz_ids' in vals.keys():
                child = vals.pop('quiz_ids')
            if 'homework_ids' in vals.keys():
                hw = vals.pop('homework_ids')
            if 'seminary_ids' in vals.keys():
                sem = vals.pop('seminary_ids')
            if 'test_ids' in vals.keys():
                test = vals.pop('test_ids')
        ret_val = super(GeneralCourseSheet, self).create(vals)
        if child != '':
            ret_val.write({'quiz_ids': child})
        if hw != '':
            ret_val.write({'homework_ids': hw})
        if sem != '':
            ret_val.write({'seminary_ids': sem})
        if test != '':
            ret_val.write({'test_ids': test})
        return ret_val

    @api.multi
    def action_fill_data(self):
        error = 'Debe seleccionar el horario, nivel, ciclo y cantidad de seminarios para generar la Hoja de Evaluación'
        res = {}
        student_list = []
        student_sem_list = []
        stud_obj = self.env['global.student']
        if not self.course_id and not self.level_id and not self.cycle:
            raise ValidationError(_(error))
        else:
            self._cr.execute("""select id from global_student where course_id=%s and level_id=%s""",
                             (self.course_id.id, self.level_id.id,))
            stud_ids = self._cr.fetchall()
            print "ESTUDIANTEEES"
            print stud_ids
            for stud_id in stud_ids:
                student_ids = stud_obj.browse(stud_id)
                student_list.append({'identification': student_ids.identification, 'stud_id': stud_id})
                for i in range(0, self.seminary_ammount):
                    student_sem_list.append({'identification': student_ids.identification, 'stud_id': stud_id,
                                         'seminary_name': "Seminario %s" % str(i + 1)})
            self.quiz_ids = student_list
            self.test_ids = student_list
            self.homework_ids = student_list
            self.seminary_ids = student_sem_list
        return True


class QuizLine(models.Model):
    """
    Defining Class Quizzes
    """
    _description = 'Quizzes'
    _name = 'quiz.line'
    _order = 'identification'
    _rec_name = 'identification'

    @api.one
    @api.depends('quiz_1', 'quiz_2', 'quiz_3', 'quiz_4')
    def _avg(self):
        avg = (self.quiz_1 + self.quiz_2 + self.quiz_3 + self.quiz_4)
        self.quiz_avg = avg

    identification = fields.Integer('Identificación', required=True, help='Identificación')
    sheet_id = fields.Many2one('qualification.sheet', 'Homework')
    stud_id = fields.Many2one('global.student', 'Estudiante', required=True)
    quiz_1 = fields.Float('Quiz 1-2')
    quiz_2 = fields.Float('Quiz 3-4')
    quiz_3 = fields.Float('Quiz 5-6')
    quiz_4 = fields.Float('Quiz 7-8')
    quiz_avg = fields.Float(compute="_avg", method=True, store=True, string='Promedio Quizzes')


class HomeworkLine(models.Model):
    """
    Defining Class Quizzes
    """
    _description = 'Quizzes'
    _name = 'hw.line'
    _order = 'identification'
    _rec_name = 'identification'

    @api.one
    @api.depends('homework_interchange', 'homework_practice')
    def _avg(self):
        avg = (self.homework_interchange + self.homework_practice) / 2
        self.homework_avg = avg

    identification = fields.Integer('Identificación', required=True, help='Identificación')
    sheet_id = fields.Many2one('qualification.sheet', 'Homework')
    stud_id = fields.Many2one('global.student', 'Estudiante', required=True)
    homework_interchange = fields.Float('Homework Interchange')
    homework_practice = fields.Float('Homework Practice')
    homework_avg = fields.Float(compute="_avg", method=True, store=True, string='Promedio Homeworks')


class TestLine(models.Model):
    """
    Defining General Tests
    """
    _description = 'Test'
    _name = 'test.line'
    _order = 'identification'
    _rec_name = 'identification'

    identification = fields.Integer('Identificación', required=True, help='Identificación')
    sheet_id = fields.Many2one('qualification.sheet', 'Homework')
    stud_id = fields.Many2one('global.student', 'Estudiante', required=True)
    test_a = fields.Float('Test B')
    test_b = fields.Float('Test A')


class SeminaryLine(models.Model):
    """
    Defining seminary lines
    """
    _description = 'Seminario'
    _name = 'seminary.line'
    _order = 'identification'
    _rec_name = 'identification'

    @api.one
    @api.depends('oral', 'vocabulary', 'reading')
    def _avg(self):
        avg = (self.oral + self.vocabulary + self.reading) / 3
        self.test_avg = avg

    identification = fields.Integer('Identificación', required=True, help='Identificación')
    sheet_id = fields.Many2one('qualification.sheet', 'Homework')
    stud_id = fields.Many2one('global.student', 'Estudiante', required=True)
    seminary_name = fields.Char('Seminario', required=True)
    oral = fields.Float('Oral')
    vocabulary = fields.Float('Vocabulary')
    reading = fields.Float('Reading')
    test_avg = fields.Float(compute="_avg", method=True, store=True, string='Promedio Test')
