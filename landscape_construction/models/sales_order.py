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
from odoo import models, fields,_,api
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _default_new_sale_id(self):
        return self.id if self else False

    design_charge = fields.Float(
        string="Design Charge"
    )
    parent_task = fields.Many2one(
        'project.task',
        string="Parent Task",
    )
    estimated_task = fields.Many2one(
        'project.task',
        string="Estimation Task",
    )
    estimated_amount = fields.Float(
        string="Estimation Amount",
    )

    state = fields.Selection(
        selection_add=[('revision', 'Revision')]
    )
    old_sale_ids = fields.One2many(
        'sale.order',
        'new_sale_id',
        string="Old Sale Orders",
        compute='_compute_parent_task_sale_orders'
    )
    new_sale_id = fields.Many2one(
        'sale.order',
        string="New Sale Order",
        default=lambda self: self._default_new_sale_id()
    )
    crm_id = fields.Many2one(
        'crm.lead',
        string="Enquiry",
    )
    create_pr = fields.Boolean(
        string="Create Project",
        default=False
    )
    # invoice_paid_ok = fields.Boolean(
    #     compute="_compute_invoice_paid_ok",
    #     string="Invoice Paid OK",
    # )
    project_creation_approved = fields.Boolean(
        string="Project Creation Approved",
        default=False,
        copy=False
    )
    job_name = fields.Char(
        string="Job Name"
    )
    # project_id = fields.Many2one(
    #     'project.project',
    #     string="Project"
    # )



    # @api.depends("invoice_ids.payment_state")
    # def _compute_invoice_paid_ok(self):
    #     for order in self:
    #         order.invoice_paid_ok = any(
    #             inv.payment_state in ["paid","partial"] for inv in order.invoice_ids)

    @api.depends('parent_task')
    def _compute_parent_task_sale_orders(self):
        for sale_order in self:
            if sale_order.parent_task != sale_order.estimated_task:
                parent_tasks = []
                current_task = sale_order.estimated_task
                while current_task.parent_id:  # Assuming 'parent_id' is the field for parent task
                    parent_tasks.append(current_task.parent_id.id)
                    current_task = current_task.parent_id
                parent_sale_order = self.env['sale.order'].search([
                    ('estimated_task', 'in', parent_tasks)
                ])
                sale_order.old_sale_ids = parent_sale_order
            else:
                sale_order.old_sale_ids = False

    def action_confirm(self):
        for order in self:
            self.estimated_task.sudo().state = '1_done'
            self.crm_id.sudo().quotation_type = 'approved'
            self.crm_id.sudo().action_set_won_rainbowman()
        return super(SaleOrder, self).action_confirm()


    def action_refuse_task_estimation(self):
        return {
            'name': 'Quotation Rejection Feedback',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            "view_type": "form",
            'res_model': 'quotation.rejection.wizard',
            'target': 'new',
            'context': {'active_id': self.id,
                        }
        }

    # def action_create_project(self):
    #     for order in self:
    #         if not order.invoice_paid_ok and not order.project_creation_approved:
    #             raise UserError(
    #                 _("Advance payment is not received. Please request approval before creating the project."))
    #         if not order.job_name:
    #             raise UserError(
    #                 _("Please Add A Job Name !!."))
    #         project = self.env["project.project"].sudo().create({
    #             "name": order.job_name,
    #             "partner_id": order.partner_id.id,
    #             "sales_order": order.id,
    #             "crm_lead_id": order.crm_id.id,
    #             "quote_amount": order.amount_total,
    #         })
    #         order.create_pr =True
    #         order.project_id = project.id
    #         task_ids = self.env['project.task'].sudo().search([('crm_lead_id','=',order.crm_id.id)])
    #         for task in task_ids:
    #             task.project_id = project.id
    #         order.message_post(body=_("Project %s created.") % project.name)

    # def action_approve_project_creation(self):
    #     for order in self:
    #         if not self.env.user.has_group(
    #                 "al_mayoof_customizatioon.group_project_creation_wo_advance"):
    #             raise UserError(
    #                 _("You are not allowed to approve project creation without advance payment."))
    #         order.project_creation_approved = True
    #         order.message_post(
    #             body=_("Project creation approved by %s") % self.env.user.name)

    # def _create_invoices(self, grouped=False, final=False, date=None):
    #     """Link timesheets to the created invoices. Date interval is injected in the
    #     context in sale_make_invoice_advance_inv wizard.
    #     """
    #     moves = super()._create_invoices(grouped=grouped, final=final,
    #                                      date=date)
    #     if self.project_id:
    #         moves.project_id = self.id
    #     return moves
