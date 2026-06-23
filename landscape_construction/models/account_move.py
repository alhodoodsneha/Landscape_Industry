# -*- coding: utf-8 -*-
#############################################################################
#    Alhodood Technologies.
#
#    Copyright (C) 2024-TODAY Alhodood Technologies(<https://www.alhodood.com>)
#    Author: Alhodood Technologies(<https://www.alhodood.com>)
#
#    You can modify it under the terms of the GNU Affero General Public License (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License (AGPL v3) for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
from odoo import api, models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    project_id = fields.Many2one(
        'project.project',
        string="Project"
    )

    is_prj_inv = fields.Boolean(
        string="Is Project Adv",
        default=False
    )

    sale_inv_id = fields.Many2one(
        'sale.order',
        string="Sales Order"
    )


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    boq = fields.Boolean(string="Boq",default=False)
    boq_line = fields.Many2one('project.deliverables', string="Boq Line")
    invoice_per = fields.Float(string="Invoice Percentage", copy=False)

