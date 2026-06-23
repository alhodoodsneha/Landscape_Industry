#############################################################################
#    Alhodood Technologies.
#    Copyright (C) 2024-TODAY Alhodood Technologies(<https://www.alhodood.com>)
#    Author: Alhodood Technologies(<https://www.alhodood.com>)
#    You can modify it under the terms of the GNU Affero General Public License
#    (AGPL v3), Version 3.
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
from odoo import models, fields, api


class SiteOperationReport(models.Model):
    _name = 'site.operation.report'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'name'
    _description = 'Daily Site Operation Report'

    name = fields.Char(
        copy=False
    )

    date = fields.Date(
        default=fields.Date.today,
        required=True
    )

    project_id = fields.Many2one(
        'project.project',
        required=True
    )

    site_engineer_id = fields.Many2one(
        'hr.employee',
        string='Site Engineer'
    )

    notes = fields.Text(string="Notes")

    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved')
    ], default='draft',string="State")

    progress_line_ids = fields.One2many(
        'site.operation.progress.line',
        'report_id',
        string="Operation Progress"
    )

    labor_line_ids = fields.One2many(
        'site.operation.labor.line',
        'report_id',
        string="Labors"
    )

    equipment_line_ids = fields.One2many(
        'site.operation.equipment.line',
        'report_id',
        string="Equipments"
    )

    material_line_ids = fields.One2many(
        'site.operation.material.line',
        'report_id',
        string="Materials"
    )

    issue_line_ids = fields.One2many(
        'site.operation.issue.line',
        'report_id',
        string="Issues"
    )

    def action_submit(self):
        self.state = 'submitted'

    def action_approve(self):
        self.state = 'approved'


class SiteOperationProgressLine(models.Model):
    _name = 'site.operation.progress.line'

    report_id = fields.Many2one(
        'site.operation.report',
        string="Site Report"
    )

    task_id = fields.Many2one(
        'project.task',
        string="Task"
    )

    planned_qty = fields.Float(
        string="Planned Qty"
    )

    completed_qty = fields.Float(
        string="Completed Qty"
    )

    remarks = fields.Char(
        string="Remarks"
    )


class SiteOperationLaborLine(models.Model):
    _name = 'site.operation.labor.line'

    report_id = fields.Many2one(
        'site.operation.report',
        string="Site Report"
    )

    employee_id = fields.Many2one(
        'hr.employee',
        string="Employee"
    )

    job_id = fields.Many2one(
        'hr.job',
        string="Job"
    )

    hours = fields.Float(
        string="Hours"
    )

    status = fields.Selection([
        ('present', 'Present'),
        ('absent', 'Absent')
    ], default='present',
        string="Status"
    )


class SiteOperationEquipmentLine(models.Model):
    _name = 'site.operation.equipment.line'

    report_id = fields.Many2one(
        'site.operation.report',
        string="Site Report"
    )

    vehicle_id = fields.Many2one(
        'fleet.vehicle',
        string='Vehicle'
    )

    start_hour = fields.Float(
        string="Start Hour"
    )

    end_hour = fields.Float(
        string="End Hour"
    )

    total_hour = fields.Float(
        compute='_compute_total_hour',
        string='Total Hour'
    )

    @api.depends('start_hour', 'end_hour')
    def _compute_total_hour(self):
        for rec in self:
            rec.total_hour = rec.end_hour - rec.start_hour


class SiteOperationMaterialLine(models.Model):
    _name = 'site.operation.material.line'

    report_id = fields.Many2one(
        'site.operation.report',
        string="Site Report"
    )

    product_id = fields.Many2one(
        'product.product',
        string="Product"
    )

    qty = fields.Float(
        string="Quantity"
    )

    uom_id = fields.Many2one(
        'uom.uom',
        string="Uom"
    )


class SiteOperationIssueLine(models.Model):
    _name = 'site.operation.issue.line'

    report_id = fields.Many2one(
        'site.operation.report',
        string="Site Report"
    )

    issue_type = fields.Selection([
        ('material', 'Material'),
        ('equipment', 'Equipment'),
        ('labor', 'Labor'),
        ('client', 'Client')
    ],string="Issue Type"
    )

    description = fields.Text(
        string="Issue Details"
    )

    priority = fields.Selection([
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ],
    string="Priority")