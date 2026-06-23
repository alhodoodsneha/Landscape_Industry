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
from odoo import api, models, fields, _
from odoo.exceptions import UserError

class CRMLead(models.Model):
    _inherit = 'crm.lead'

    assigned = fields.Boolean(string="Assigned", default=False)
    quotation_type = fields.Selection([
        ('no_action_taken', 'No Action Taken'),
        ('site_inspection','Site Inspection'),
        ('design_review','Design Review'),
        ('waiting_for_estimation', 'Under Estimation'),
        ('estimation_completed', 'Estimation Revised'),
        ('quote_submitted', 'Quote Submitted'),
        ('quotation_revised','Quotation Revised'),
        ('approved', 'Quotation Approved'), ('cancel', 'Cancel')
    ], default='no_action_taken', string="Quotation Type")
    sequence_code = fields.Char(string="Sequence")
    job_name = fields.Char(string="Job Name")
    project_detail = fields.Text(string="Project Details")

    @api.model_create_multi
    def create(self, vals_list):
        res = super(CRMLead, self).create(vals_list)
        for rec in res:
            rec.sequence_code = self.env['ir.sequence'].next_by_code('crm.lead')
        return res

    def action_create_site_inspection(self):
        if not self.job_name:
            raise UserError(_("Please Add the job name"))
        inspection_manager = self.env['inspection.team.member'].search([],
                                                                       limit=1)
        if not inspection_manager:
            raise UserError(_("Please Configure The Inspection Team"))
        if not self.date_deadline:
            raise UserError(_("Please Add closing date"))
        is_internal_pr = self.env['project.project'].search([('is_internal','=',True),('company_id','=',self.company_id.id)])
        if not is_internal_pr:
            is_internal_pr = self.env['project.project'].sudo().create({
                'name': "Internal Work",
                'user_id': inspection_manager.team_manager_id.id,
                'allow_timesheets': True,
                'is_internal': True,
                'date_start': fields.Date.today(),
                'date': self.date_deadline,
                'company_id':self.company_id.id
            })
        sequence_insp_task = self.env['ir.sequence'].next_by_code(
            'project.task.inspection')
        project_task = self.env['project.task'].sudo().create({
            'name': 'Inspection For - ' + self.job_name,
            'sequence_code': sequence_insp_task,
            'user_ids': [(6, 0, [inspection_manager.team_manager_id.id])],
            'partner_id': self.partner_id.id,
            'description': self.project_detail,
            'project_id': is_internal_pr.id,
            '_is_inspection_task': True,
            'date_deadline': self.date_deadline,
            'crm_lead_id': self.id,
        })
        self.write({
            'assigned': True,
            'quotation_type': 'site_inspection',
        })