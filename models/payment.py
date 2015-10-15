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
import time
from openerp import models, fields, api


class Payment(models.Model):
    _name = "student.payment"
    _description = "Pago"

    PAYMENT_MONTHLY = 'monthly'
    PAYMENT_INSCRIPTION = 'inscription'

    CONCEPT_CHOICES = [
        (PAYMENT_MONTHLY, 'Pago Mensual'),
        (PAYMENT_INSCRIPTION, 'Pago Inscripción')
    ]

    @api.one
    @api.depends('student_id')
    def _compute_amount_due(self):
        """
        Calculate the amount due to pay
        :return: float Amount Due
        """
        if self.student_id:
            if self.student_id.monthly_amount and self.amount:
                self.amount_due = self.student_id.monthly_amount - self.amount

    student_id = fields.Many2one('global.student', 'Estudiante')
    course_id = fields.Many2one('global.course', 'Horario', required=True)
    level_id = fields.Many2one('global.level', 'Nivel', required=True)
    number = fields.Char('Número de Factura')
    #from_month = fields.Many2one('academic.month', 'Mes', required=True)
    concept = fields.Selection(CONCEPT_CHOICES, 'Concepto', required=True, default=PAYMENT_MONTHLY)
    date = fields.Date('Fecha', readonly=True, default=lambda *a: time.strftime('%Y-%m-%d'))
    amount = fields.Float("Valor Pagado", required=True)
    amount_due = fields.Float(compute='_compute_amount_due', string='Debe', readonly=True, method=True, store=True)

    _sql_constraints = [
        ('number_uniq', 'unique(number)', 'Este número de factura ya existe en otro pago!')
    ]

    @api.multi
    def fees_register_draft(self):
        self.write({'state': 'draft'})
        return True
