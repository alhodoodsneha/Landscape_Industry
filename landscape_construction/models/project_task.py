# -*- coding: utf-8 -*-
#############################################################################
#    Alhodood Technologies.
#
#    Copyright (C) 2024-TODAY Alhodood Technologies(<https://www.alhodood.com>)
#    Author: Alhodood Technologies(<https://www.alhodood.com>)
#
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


class ProjectTask(models.Model):
    _inherit = 'project.task'

    sequence_code = fields.Char(
        string="Sequence"
    )
    crm_lead_id = fields.Many2one(
        'crm.lead',
        string="Crm"
    )
    _is_inspection_task = fields.Boolean(
        string="Inspection Task",
        default=False
    )
    _is_design_task = fields.Boolean(
        string="Design Task",
        default=False
    )
    is_completed = fields.Boolean(
        string='Complete',
        default=False
    )
    inspection_attachment_ids = fields.One2many(
        'inspection.attachment',
        'task_id',
        string="Inspection Attachment"
    )
    is_design_completed = fields.Boolean(
        string="Design Completed",
        default=False,
    )
#
    design_attachment_ids = fields.One2many(
        'design.attachment',
        'task_id',
        string="Design Attachment"
    )
    _is_estimation_task = fields.Boolean(
        string="Is Estimation",
        default=False
    )
    _revision_task = fields.Boolean(
        string="Is Revision",
        default=False
    )
    revision_count = fields.Integer(
        string="Revision Count",
        default=0
    )
    material_estimation_ids = fields.One2many(
        'material.estimation',
        'task_id',
        string="Material Estimation Line"
    )
    labour_estimation_ids = fields.One2many(
        'labour.estimation',
        'task_id',
        string="Labour Estimation Line"
    )
    other_over_head_ids = fields.One2many(
        'other.over.head',
        'task_id',
        string=" Other Over Head"
    )

    total_material_estimation = fields.Float(
        string="Total",
        compute='_compute_total__material_est'
    )
    total_labour_estimation = fields.Float(
        string="Total",
        compute='_compute_total__labour_est'
    )
    total_over_head = fields.Float(
        string="Total",
        compute='_compute_total_over_head'
    )

    total_estimation = fields.Float(
        string="Estimation Total",
        compute='_compute_total_estimation'
    )

    sales_profit = fields.Float(
        string="Sales Profit(%)",
        default=lambda self: self.env.company.sales_profit
    )
#
    total_sales = fields.Float(
        string="Total Amount",
        compute='_compute_total_sales'
    )

    estimation_status = fields.Selection(
        [('under_estimation', 'Under Estimation'),
         ('approve', 'Approve Estimation'),
         ('refuse_estimation', 'Refuse Estimation'), ('cancel', 'Cancel')],
        string="Estimation Status",
        default='under_estimation'
    )
#
    refuse_reason = fields.Text(
        string="Refuse Reason"
    )
    estimation_parent_id = fields.Many2one(
        'project.task',
        string="Estimation Parent"
    )

    design_charge = fields.Float(
        string="Design charge"
    )
#     is_production = fields.Boolean(
#         string="Production Task",
#         default=False
#     )
#     is_installation = fields.Boolean(
#         string="Installation Task",
#         default=False
#     )
#     is_delivery = fields.Boolean(
#         string="Delivery Task",
#         default=False
#     )
#     is_qa_qc = fields.Boolean(
#         string="QA/QC Task",
#         default=False
#     )
#
#     is_qa_qc_completed = fields.Boolean(
#         string="Design Completed",
#         default=False,
#     )
#
#     production_line_ids = fields.One2many(
#         'mrp.production',
#         'production_task',
#         string="Mrp Lines"
#     )
#
    @api.depends('material_estimation_ids')
    def _compute_total__material_est(self):
        for rec in self:
            if rec.material_estimation_ids:
                rec.total_material_estimation = sum(
                    line.subtotal for line in rec.material_estimation_ids)
            else:
                rec.total_material_estimation = 0.0

    @api.depends('labour_estimation_ids')
    def _compute_total__labour_est(self):
        for rec in self:
            if rec.labour_estimation_ids:
                rec.total_labour_estimation = sum(
                    line.subtotal for line in rec.labour_estimation_ids)
            else:
                rec.total_labour_estimation = 0.0

    @api.depends('other_over_head_ids')
    def _compute_total_over_head(self):
        for rec in self:
            if rec.other_over_head_ids:
                rec.total_over_head = sum(
                    line.subtotal for line in rec.other_over_head_ids)
            else:
                rec.total_over_head = 0.0


    @api.depends('other_over_head_ids', 'labour_estimation_ids',
                 'material_estimation_ids')
    def _compute_total_estimation(self):
        for rec in self:
            rec.total_estimation = rec.total_material_estimation + rec.total_labour_estimation + rec.total_over_head

    @api.depends('total_sales', 'sales_profit', 'total_estimation')
    def _compute_total_sales(self):
        for rec in self:
            if rec.total_estimation > 0 and rec.sales_profit > 0:
                rec.total_sales = rec.total_estimation + (
                        (rec.total_estimation * rec.sales_profit) / 100)
            else:
                rec.total_sales = rec.total_estimation

    def action_completed_inspection(self):
        if not self.inspection_attachment_ids:
            raise UserError(_("Please Add Some Inspection Lines"))
        design_team = self.env['design.team.member'].sudo().search([], limit=1)
        if not design_team:
            raise UserError(_("Please Configure the Design Team"))
        sequence_est_task = self.env['ir.sequence'].next_by_code(
            'project.task.design')
        project_task = self.env['project.task'].sudo().create({
            'name': 'Design For - ' + self.crm_lead_id.sudo().job_name,
            'sequence_code': sequence_est_task,
            'user_ids': [(6, 0, [design_team.team_manager_id.id])],
            'partner_id': self.partner_id.id,
            '_is_design_task': True,
            'project_id': self.project_id.id,
            'description': self.description,
            'date_deadline': self.date_deadline,
            'crm_lead_id': self.crm_lead_id.id,
        })
        self.is_completed = True
        self.state = '1_done'
        self.crm_lead_id.sudo().quotation_type = 'design_review'

    def action_completed_design(self):
        if not self.design_attachment_ids:
            raise UserError(_("Please Add Some Design Lines"))
        estimation_team = self.env['estimation.team.member'].sudo().search([],
                                                                           limit=1)
        if not estimation_team:
            raise UserError(_("Please Configure The Estimation Team"))
        sequence_est_task = self.env['ir.sequence'].next_by_code(
            'project.task.estimation')
        project_task = self.env['project.task'].sudo().create({
            'name': 'Estimation For - ' + self.crm_lead_id.sudo().job_name,
            'sequence_code': sequence_est_task,
            'user_ids': [(6, 0, [estimation_team.team_manager_id.id])],
            'partner_id': self.partner_id.id,
            '_is_estimation_task': True,
            'project_id': self.project_id.id,
            'description': self.description,
            'date_deadline': self.date_deadline,
            'crm_lead_id': self.crm_lead_id.id,
        })
        self.is_design_completed = True
        self.state = '1_done'
        self.crm_lead_id.sudo().quotation_type = 'waiting_for_estimation'

    def action_approve_estimation(self):
        if not self.material_estimation_ids or not self.labour_estimation_ids or not self.other_over_head_ids:
            raise UserError(
                "Please add at least some estimation line before approving the estimation.")
        product_template_id = self.env['product.template'].search(
            [('estimation_ok', '=', True)], limit=1)
        if not product_template_id:
            raise UserError("Please Configure A Estimation Product.")
        if self.parent_id:
            parent_task = self.estimation_parent_id
        else:
            parent_task = self
        sale_order = self.env['sale.order'].sudo().create({
            'partner_id': self.crm_lead_id.partner_id.id,
            'parent_task': parent_task.id,
            'estimated_task': self.id,
            'estimated_amount': self.total_sales,
            'design_charge': self.design_charge,
            'crm_id': self.crm_lead_id.id,
            'order_line': [(0, 0, {
                'product_id': product.id,
                'product_uom_qty': 1,
                'price_unit': self.total_sales,
            }) for product in product_template_id.product_variant_id]
        })
        self.estimation_status = 'approve'
        self.crm_lead_id.sudo().quotation_type = 'quote_submitted'

#     def action_approve_revision_estimation(self):
#         if not self.material_estimation_ids or not self.labour_estimation_ids or not self.other_over_head_ids or not self.machinery_products_ids:
#             raise UserError(
#                 "Please add at least some estimation line before approving the estimation.")
#         if self.parent_id:
#             parent_task = self.estimation_parent_id
#         else:
#             parent_task = self
#         product_template_id = self.env['product.template'].search(
#             [('estimation_ok', '=', True)], limit=1)
#         if not product_template_id:
#             raise UserError("Please Configure A Estimation Product.")
#         sale_order = self.env['sale.order'].sudo().create({
#             'partner_id': self.crm_lead_id.partner_id.id,
#             'parent_task': parent_task.id,
#             'estimated_task': self.id,
#             'design_charge': self.design_charge,
#             'crm_id': self.crm_lead_id.id,
#             'estimated_amount': self.total_sales,
#             'order_line': [(0, 0, {
#                 'product_id': product.id,
#                 'product_uom_qty': 1,
#                 'price_unit': self.total_sales,
#             }) for product in product_template_id.product_variant_id]
#         })
#         self.estimation_status = 'approve'
#         self.crm_lead_id.sudo().quotation_type = 'quote_submitted'
#
#     def action_refuse_estimation(self):
#         self.estimation_status = 'refuse_estimation'
#         self.state = '1_canceled'
#         self.revision_count = self.revision_count + 1
#         self.crm_lead_id.sudo().quotation_type = 'estimation_completed'
#         if self.estimation_parent_id:
#             estimation_parent_id = self.estimation_parent_id
#         else:
#             estimation_parent_id = self
#         subtask = self.env['project.task'].sudo().create({
#             'name': f'Revision {self.sequence_code} - {self.revision_count}',
#             'project_id': self.project_id.id,
#             'parent_id': self.id,
#             'crm_lead_id': self.crm_lead_id.id,
#             'sequence_code': self.sequence_code,
#             'revision_count': self.revision_count,
#             'sales_profit': self.sales_profit,
#             'design_charge': self.design_charge,
#             'estimation_parent_id': estimation_parent_id.id,
#             '_revision_task': True,
#             'user_ids': [(6, 0, [user.id for user in self.user_ids])],
#             'partner_id': self.partner_id.id,
#             'material_estimation_ids': [(0, 0, {
#                 'name': line.name,
#                 'product_id': line.product_id.id,
#                 'description': line.description,
#                 'qty': line.qty,
#                 'uom_id': line.uom_id.id,
#                 'unit_price': line.unit_price,
#             }) for line in self.material_estimation_ids],
#
#             'labour_estimation_ids': [(0, 0, {
#                 'name': line.name,
#                 'labour_id': line.labour_id.id,
#                 'description': line.description,
#                 'qty': line.qty,
#                 'hour': line.hour,
#                 'unit_price': line.unit_price,
#             }) for line in self.labour_estimation_ids],
#
#             'other_over_head_ids': [(0, 0, {
#                 'name': line.name,
#                 'service_product': line.service_product.id,
#                 'description': line.description,
#                 'qty': line.qty,
#                 'unit_price': line.unit_price,
#                 'subtotal': line.subtotal,
#             }) for line in self.other_over_head_ids],
#
#             'machinery_products_ids': [(0, 0, {
#                 'name': line.name,
#                 'days': line.days,
#                 'unit_price': line.unit_price,
#             }) for line in self.machinery_products_ids],
#         })
#         return {
#             'name': 'Estimation Rejection Feedback',
#             'type': 'ir.actions.act_window',
#             'view_mode': 'form',
#             "view_type": "form",
#             'res_model': 'estimation.rejection.wizard',
#             'target': 'new',
#             'context': {'active_id': self.id,
#                         }
#         }
#
    def action_refuse_revision_estimation(self):
        self.estimation_status = 'refuse_estimation'
        self.state = '1_canceled'
        self.revision_count = self.revision_count + 1
        self.crm_lead_id.sudo().quotation_type = 'estimation_completed'
        if self.estimation_parent_id:
            estimation_parent_id = self.estimation_parent_id
        else:
            estimation_parent_id = self
        subtask = self.env['project.task'].create({
            'name': f'Revision {self.sequence_code}  - {self.revision_count}',
            'sequence_code': self.sequence_code,
            'project_id': self.project_id.id,
            'parent_id': self.id,
            'crm_lead_id': self.crm_lead_id.id,
            'sales_profit': self.sales_profit,
            'revision_count': self.revision_count,
            'estimation_parent_id': estimation_parent_id.id,
            'design_charge': self.design_charge,
            '_revision_task': True,
            'user_ids': [(6, 0, [user.id for user in self.user_ids])],
            'partner_id': self.partner_id.id,
            'material_estimation_ids': [(0, 0, {
                'name': line.name,
                'product_id': line.product_id.id,
                'description': line.description,
                'qty': line.qty,
                'uom_id': line.uom_id.id,
                'unit_price': line.unit_price,
            }) for line in self.material_estimation_ids],
            'labour_estimation_ids': [(0, 0, {
                'name': line.name,
                'labour_id': line.labour_id.id,
                'description': line.description,
                'qty': line.qty,
                'hour': line.hour,
                'unit_price': line.unit_price,
            }) for line in self.labour_estimation_ids],

            'other_over_head_ids': [(0, 0, {
                'name': line.name,
                'service_product': line.service_product.id,
                'description': line.description,
                'qty': line.qty,
                'unit_price': line.unit_price,
                'subtotal': line.subtotal,
            }) for line in self.other_over_head_ids],
        })
        return {
            'name': 'Estimation Rejection Feedback',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            "view_type": "form",
            'res_model': 'estimation.rejection.wizard',
            'target': 'new',
            'context': {'active_id': self.id,
                        }
        }

    def action_open_related_sale_order(self):
        sale_order_ids = self.env['sale.order'].search(
            [('parent_task', '=', self.id)])
        return {
            'name': 'Sale Order',
            'view_type': 'list',
            'view_mode': 'list,form',
            'res_model': 'sale.order',
            'domain': [('id', 'in', sale_order_ids.ids)],
            'type': 'ir.actions.act_window',
        }

    def action_related_sale_order(self):
        sale_order_ids = self.env['sale.order'].search(
            [('estimated_task', '=', self.id)])
        return {
            'name': 'Sale Order',
            'view_type': 'list',
            'view_mode': 'list,form',
            'res_model': 'sale.order',
            'domain': [('id', 'in', sale_order_ids.ids)],
            'type': 'ir.actions.act_window',
        }
#
#     def action_complete_qa_qc(self):
#         if not self.timesheet_ids:
#             raise UserError(_("Please Add Timesheet"))
#         self.is_qa_qc_completed = True

class InspectionAttachment(models.Model):
    _name = 'inspection.attachment'

    description = fields.Text(
        string="Title"
    )
    images = fields.Binary(
        string="Images"
    )
    task_id = fields.Many2one(
        'project.task',
        string='Task'
    )
    is_completed = fields.Boolean(
        string='Complete',
        default=False,
        related='task_id.is_completed'
    )

    def unlink(self):
        if self.is_completed:
            raise UserError(
                _("You do not have the access to delete records !!"))
        else:
            return super(InspectionAttachment, self).unlink()


class DesignAttachment(models.Model):
    _name = 'design.attachment'

    description = fields.Text(
        string="Title"
    )
    images = fields.Binary(
        string="Images"
    )
    task_id = fields.Many2one(
        'project.task',
        string='Task'
    )
    is_design_completed = fields.Boolean(
        string='Design Complete Task',
        default=False,
        related='task_id.is_design_completed'
    )

    def unlink(self):
        if self.is_design_completed:
            raise UserError(
                _("You do not have the access to delete records !!"))
        else:
            return super(DesignAttachment, self).unlink()
