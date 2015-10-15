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
import time
import openerp
import datetime
from datetime import date
from datetime import datetime
from openerp.exceptions import ValidationError, except_orm
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, image_colorize, \
    image_resize_image_big


class Horario(models.Model):
    """
    Define un horario o curso
    """
    _name = "global.course"
    _description = "Horario"

    code = fields.Char('Código', required=True, help='Código del curso')
    name = fields.Char('Nombre', required=True, help='Ej. Jueves de 13h a 14h')
    description = fields.Text('Descripción')


class Nivel(models.Model):
    """
    Define un nivel
    """
    _name = "global.level"
    _description = "Nivel"

    code = fields.Char('Código', required=True, help='Código del curso')
    name = fields.Char('Nombre', required=True, help='Ej. Jueves de 13h a 14h')


class Student(models.Model):
    """
    Defines a student profile
    """
    _name = 'global.student'
    _description = 'Estudiante'
    _table = "global_student"
    _inherits = {'res.users': 'user_id'}
    _order = "registration_date,id desc"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _mail_mass_mailing = _('Estudiantes')

    GENDER_CHOICES = [
        ('male', 'Masculino'),
        ('female', 'Femenino'),
        ('other', 'Otro'),
    ]

    ID_CHOICES = [
        ('cedula', 'Cédula'),
        ('ruc', 'RUC'),
        ('passport', 'Pasaporte')
    ]

    OPERATOR_CHOICES = [
        ('claro', 'Claro'),
        ('movistar', 'Movistar'),
        ('allegro', 'Allegro'),
        ('cnt', 'CNT'),
        ('tuenti', 'Tuenti')
    ]

    STATUS_CHOICES = [
        ('draft', 'Registrado'),
        ('registered', 'Inscrito'),
        ('alumni', 'Estudiante Activo'),
        ('inactive', 'Estudiante Inactivo'),
        ('terminate', 'Estudiante Aprobado')
    ]

    CYCLE_CHOICES = [
        ('A', 'A'),
        ('B', 'B')
    ]

    MONITORING_CHOICES = [
        ('O', 'Obligatorio'),
        ('B', 'Voluntario')
    ]

    def _check_cedula(self, identification):
        if len(identification) == 13 and not identification[10:13] == '001':
            return False
        else:
            if len(identification) < 10:
                return False
        coef = [2, 1, 2, 1, 2, 1, 2, 1, 2]
        cedula = identification[:9]
        suma = 0
        for c in cedula:
            val = int(c) * coef.pop()
            suma += val > 9 and val - 9 or val
        result = 10 - ((suma % 10) != 0 and suma % 10 or 10)
        if result == int(identification[9:10]):
            return True
        else:
            return False

    def _check_ruc(self, ruc):
        if not len(ruc) == 13:
            return False
        if ruc[2:3] == '9':
            coef = [4, 3, 2, 7, 6, 5, 4, 3, 2, 0]
            coef.reverse()
            verificador = int(ruc[9:10])
        elif ruc[2:3] == '6':
            coef = [3, 2, 7, 6, 5, 4, 3, 2, 0, 0]
            coef.reverse()
            verificador = int(ruc[8:9])
        else:
            raise ValidationError('RUC Incorrecto')
        suma = 0
        for c in ruc[:10]:
            suma += int(c) * coef.pop()
        result = 11 - (suma > 0 and suma % 11 or 11)
        if result == verificador:
            return True
        else:
            return False

    @api.one
    @api.depends('date_of_birth')
    def _calc_age(self):
        self.age = 0
        if self.date_of_birth:
            start = datetime.strptime(self.date_of_birth, DEFAULT_SERVER_DATE_FORMAT)
            end = datetime.strptime(time.strftime(DEFAULT_SERVER_DATE_FORMAT), DEFAULT_SERVER_DATE_FORMAT)
            self.age = ((end - start).days / 365)

    @api.model
    def create(self, vals):
        if vals.get('identification', False):
            vals['login'] = vals['identification']
            vals['password'] = vals['identification']
        else:
            raise except_orm(_('Error!'), _('Debe proveer una identificación para poder guardar.'))
        result = super(Student, self).create(vals)
        return result

    @api.model
    def _get_default_image(self, is_company, colorize=False):
        image = image_colorize(open(openerp.modules.get_module_resource('base', 'static/src/img', 'avatar.png')).read())
        return image_resize_image_big(image.encode('base64'))

    # Define fields here
    id = fields.Integer('ID', readonly=True)
    color = fields.Integer('Color', default=0)
    user_id = fields.Many2one('res.users', string='Usuario', ondelete="cascade", select=True, required=True)
    student_name = fields.Char(related='user_id.name', string='Nombres', store=True, readonly=True)
    registration_date = fields.Date('Fecha de Registro', readonly=True, default=lambda *a: time.strftime('%Y-%m-%d'))
    admission_date = fields.Date('Fecha de Inscripción')
    reg_code = fields.Char('No. de Afiche')
    admission_number = fields.Char('Registro en la carpeta de cupos')

    photo = fields.Binary('Foto',
                          default=lambda self: self._get_default_image(self._context.get('default_is_company', False)))
    last_name = fields.Char('Apellidos', required=True, states={'done': [('readonly', True)]})
    identification_type = fields.Selection(ID_CHOICES, 'Tipo Identificación', required=True, default='cedula',
                                           states={'done': [('readonly', True)]})
    identification = fields.Char('No. Identificación', size=13, required=True)

    gender = fields.Selection(GENDER_CHOICES, 'Género', states={'done': [('readonly', True)]})
    date_of_birth = fields.Date('Fecha de Nacimiento', required=True, states={'done': [('readonly', True)]})
    age = fields.Integer(compute='_calc_age', string='Edad', readonly=True)

    wear_glasses = fields.Boolean('Usa Lentes?')
    plain_feet = fields.Boolean('Tiene Pies Planos?')

    street = fields.Char('Dirección Exacta', size=256, states={'done': [('readonly', True)]})
    phone = fields.Integer('Teléfono del Domicilio', size=7, states={'done': [('readonly', True)]})

    mobile = fields.Char('Celular', size=10, required=True, states={'done': [('readonly', True)]})
    mobile_operator = fields.Selection(OPERATOR_CHOICES, 'Operadora', required=True,
                                       states={'done': [('readonly', True)]})

    email = fields.Char('Correo Electrónico', size=256, states={'done': [('readonly', True)]},
                        help_text='Correo del representante, si es menor de edad')

    notes = fields.Text('Observaciones')

    # Course Info
    course_id = fields.Many2one('global.course', 'Horario', required=True)
    level_id = fields.Many2one('global.level', 'Nivel', required=True)
    cycle = fields.Selection(CYCLE_CHOICES, 'Ciclo', required=True)

    monthly_amount = fields.Float("Valor Mensual", help_text="Valor a pagar mensualmente", required=True)
    payment_notes = fields.Char('Observaciones Pago', size=256)
    payment_day = fields.Integer('Día Compromiso de Pago', required=True, default=1)

    # Monitoring
    monitoring_type = fields.Selection(MONITORING_CHOICES, 'Tipo de Monitoreo')

    # Social
    facebook = fields.Char('ID Facebook', size=64)
    twitter = fields.Char('ID Twitter', size=64)
    skype = fields.Char('Skype',  size=128, select=True)

    # relationship fields
    parent_name = fields.Char('Nombre del Representante', size=256, states={'done': [('readonly', True)]},
                              help_text='Si es menor de edad')
    contact_time = fields.Float('Hora preferida de contacto')

    reference_ids = fields.One2many('student.reference', 'student_id', string='References',
                                    states={'done': [('readonly', True)]})
    payment_ids = fields.One2many('student.payment', 'student_id', string='Payments',
                                  states={'done': [('readonly', True)]})
    history_ids = fields.One2many('student.history', 'student_id', string='History')

    referred_by = fields.Many2one('global.referred.sources', 'Cómo se enteró del programa')
    called_by = fields.Char('Persona que le llamó', size=255)
    prev_institute_id = fields.Many2one('global.institutes.master', 'Institución o Universidad en la que estudia')

    state = fields.Selection(STATUS_CHOICES, 'State', readonly=True, default='draft')

    _sql_constraints = [
        ('identification_unique', 'unique(identification)', 'Ya existe un estudiante con esta identificacion!')
    ]

    @api.one
    @api.constrains('identification')
    def _check_identification(self):
        if self.identification:
            if self.identification_type == 'cedula':
                # validate cedula
                if self._check_cedula(self.identification):
                    raise ValidationError(_('Cédula Incorrecta.'))
            elif self.identification_type == 'ruc':
                if self._check_ruc(self.identification):
                    raise ValidationError(_('RUC Incorrecto.'))
            return True

    @api.one
    @api.constrains('payment_day')
    def _check_payment_day(self):
        if self.payment_day:
            if self.payment_day < 1 or self.payment_day > 31:
                raise ValidationError(_('El día de pago debe estar entre 1 y 31.'))
            return True

    @api.multi
    def set_to_draft(self):
        self.write({'state': 'draft'})
        return True

    @api.multi
    def admission_draft(self):
        self.write({'state': 'draft'})
        return True

    @api.multi
    def admission_done(self):
        """
        Check that student met the following rules:
         1. Has paid inscription fee at least partially.
         2. Has delivered course materials
        """
        for student_data in self:
            reg_code = self.env['ir.sequence'].get('student.registration')
            registration_code = str(reg_code)
        self.write({'state': 'registered', 'admission_date': time.strftime('%Y-%m-%d'), 'reg_code': registration_code})
        return True

    @api.multi
    def set_alumni(self):
        self.write({'state': 'alumni'})
        return True

    @api.multi
    def set_inactive(self):
        self.write({'state': 'inactive'})
        return True

    @api.multi
    def set_terminate(self):
        self.write({'state': 'terminate'})
        return True


class StudentHistory(models.Model):
    _name = "student.history"
    _description = "Historial"

    student_id = fields.Many2one('global.student', 'Estudiante')
    course_id = fields.Many2one('global.course', 'Horario', required=True)
    level_id = fields.Many2one('global.level', 'Nivel', required=True)
    percentage = fields.Float("Nota Final", readonly=True)
    result = fields.Char(string='Resultado', readonly=True, store=True)


class Reference(models.Model):
    """
    Defining a student reference information
    """
    _name = "student.reference"
    _description = "Referencia"

    student_id = fields.Many2one('global.student', 'Estudiante')
    name = fields.Char('Nombres', required=True)
    last = fields.Char('Apellidos', required=True)
    relation = fields.Many2one('student.relation.master', string='Tipo de Relación', required=True)
    phone = fields.Char('Teléfono', required=True)
    mobile = fields.Char('Celular', required=True)
    email = fields.Char('E-Mail')


class Relationship(models.Model):
    """
    Student Relation Information
    """
    _name = "student.relation.master"
    _description = "Relaciones"

    name = fields.Char('Nombre', required=True, help="Nombre de la relacion. Ej. Madre, Amigo...")


class StudentMaterial(models.Model):
    """
    Materiales del Estudiante
    """
    _name = 'student.material'

    student_id = fields.Many2one('global.student', 'Estudiante')
    relation = fields.Many2one('student.material.master', string='Material', required=True)
    delivered = fields.Boolean('Entregado', default=True)


class Material(models.Model):
    _name = 'student.material.master'

    name = fields.Char('Nombre', size=256, required=True)


class ReferenceSource(models.Model):
    _name = 'global.referred.sources'

    name = fields.Char('Fuente de Referencia', size=256, required=True)


class Institution(models.Model):
    _name = 'global.institutes.master'

    name = fields.Char('Institución o Universidad', size=256, required=True)
