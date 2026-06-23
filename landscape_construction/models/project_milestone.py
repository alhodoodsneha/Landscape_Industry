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
from email.policy import default

from odoo import api, models, fields,_
from odoo.exceptions import UserError
from datetime import date, timedelta


class ProjectMilestone(models.Model):
    _inherit = 'project.milestone'

    start_date = fields.Date(string="Start Date")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed')
    ], string="Status", default='draft', tracking=True)

    starting_delay = fields.Integer(string="Starting Delay", compute="_compute_delays", store=True)
    closing_delay = fields.Integer(string="Closing Delay", compute="_compute_delays", store=True)
    progress = fields.Float("Progress", compute='_compute_total_milestone_progress',  aggregator="avg")
    duration = fields.Integer(
        string="Duration (Days)",
        compute="_compute_duration",
        store=True
    )

    remark = fields.Text(
        string="Remark",
        tracking=True
    )

    planned_start_date = fields.Date(
        string="planned Start Date"
    )

    planned_end_date = fields.Date(
        string="planned End Date"
    )

    per_of_weight = fields.Float(
        string="% weight",
        default=0.0
    )

    invoiced_per = fields.Float(
        string="Invoiced %",
        default=0.0
    )

    balance_per = fields.Float(
        string="Balance %",
        default=0.0
    )

    total_amount = fields.Float(
        string="Total amount",
        default=0.0
    )

    invoiced_amount = fields.Float(
        string="Invoiced amount",
        default=0.0
    )

    balance_amount = fields.Float(
        string="Balance Amount",
        default=0.0
    )
    project_verified = fields.Boolean(string="Project Verified", default=False)


    def action_verify_project(self):
        self.project_verified = True

    def cron_check_milestone_delay(self):
        today = date.today()
        milestones = self.search([
            ('deadline', '<', today),
            ('state', '!=', 'completed')
        ])
        for milestone in milestones:
            project = milestone.project_id
            recipients = [project.user_id.partner_id.id]
            if recipients:
                subject = f"Milestone Delay Reminder -  {milestone.name} ❗️"
                body = f""" <p>Dear<strong> {project.user_id.name}</strong>, </p>
                              <p>The milestone <b>{milestone.name}</b> on project<b>{project.name}</b> is delayed.Deadline: {milestone.deadline}.</p>
                              <p>Please take the necessary actions to complete this milestone at the earliest.</p>
                              <p>Regards,<br/>
                                   Project Monitoring System</p>
                                          """
                mail_values = {
                    'subject': subject,
                    'body_html': body,
                    'email_to': project.user_id.email,
                }
                self.env['mail.mail'].create(mail_values).send()

    @api.depends('start_date', 'deadline', 'state')
    def _compute_delays(self):
        today = fields.Date.today()
        for record in self:
            if record.start_date and record.state in ('draft', 'pending') and today > record.start_date:
                record.starting_delay = (today - record.start_date).days
            else:
                record.starting_delay = 0
            if record.deadline and record.state != 'completed' and today > record.deadline:
                record.closing_delay = (today - record.deadline).days
            else:
                record.closing_delay = 0

    def action_set_pending(self):
        self.state = 'pending'

    def action_set_in_progress(self):
        self.state = 'in_progress'

    def action_set_completed(self):
        not_done_tasks = self.task_ids.filtered(lambda t: not t.stage_id.is_done)
        if not_done_tasks:
            raise UserError("Please complete all tasks before completing the milestone.!!")
        self.state = 'completed'
        self.is_reached = True

    def action_view_tasks_milestones(self):
        return {
            'name': 'Milestone Tasks',
            'type': 'ir.actions.act_window',
            'view_mode': 'list',
            'res_model': 'project.task',
            'views': [(self.env.ref('milestone_project.view_project_task_tree_milestone').id, 'list')],
            'domain': [('milestone_id', '=', self.id), ('project_id', '=', self.project_id.id)],
            'target': 'new',
            'context': {
                'create': False,
                'delete': False,
                'edit': False
            },

        }

    @api.depends('task_ids','name', 'project_id', 'start_date','task_ids.effective_hours', 'task_ids.allocated_hours')
    def _compute_total_milestone_progress(self):
        for record in self:
            total_effective_hours = 0.0
            total_allocated_hours = 0.0
            if record.task_ids:
                for task in record.task_ids:
                    total_effective_hours += task.effective_hours or 0.0
                    total_allocated_hours += task.allocated_hours or 0.0
                if total_allocated_hours > 0:
                    record.progress = round(total_effective_hours / total_allocated_hours,2)
                else:
                    record.progress = 0.0
            else:
                record.progress = 0.0


    @api.depends('start_date', 'deadline')
    def _compute_duration(self):
        for rec in self:
            if rec.start_date and rec.deadline:
                rec.duration = (rec.deadline - rec.start_date).days + 1
            else:
                rec.duration = 0

    @api.onchange('start_date', 'deadline')
    def _onchange_check_on_project_dates(self):
        for rec in self:
            if not rec.project_id:
                continue
            project = rec.project_id
            if not project.date_start or not project.date:
                raise UserError(
                    _("Please Add  Project Start Date And End Date !!"))
            if rec.start_date and rec.start_date < project.date_start:
                raise UserError(
                    _("Please Choose Start Date With in Project Start Date  !!"))
            if rec.start_date and rec.start_date > project.date:
                raise UserError(
                    _("Please Choose Start Date With in Project End Date  !!"))
            if rec.deadline and rec.deadline > project.date:
                raise UserError(
                    _("Please Choose End Date With in Project End Date  !!"))
            if rec.deadline and rec.deadline < project.date_start:
                raise UserError(
                    _("Please Choose End Date With in Project Start Date  !!"))
