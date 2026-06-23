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


class EstimationRejectionWizard(models.TransientModel):
    _name = 'estimation.rejection.wizard'
    _description = "Estimation Rejection Feedback"

    feedback = fields.Text('Feedback',required=True)

    def action_add_feedback(self):
        project_task = self.env['project.task'].browse(self.env.context['active_id'])
        project_task.refuse_reason = self.feedback


class QuotationRejectionWizard(models.TransientModel):
    _name = 'quotation.rejection.wizard'
    _description = "Quotation Rejection Feedback"

    feedback = fields.Text('Feedback',required=True)

    def action_add_feedback(self):
        sales_order = self.env['sale.order'].browse(
            self.env.context['active_id'])
        sales_order.state = 'revision'
        sales_order.estimated_task.estimation_status = 'refuse_estimation'
        sales_order.estimated_task.refuse_reason = self.feedback
        sales_order.estimated_task.state = '1_canceled'
        sales_order.crm_id.quotation_type = 'quotation_revised'
        sales_order.estimated_task.revision_count = sales_order.estimated_task.revision_count + 1
        if sales_order.estimated_task.estimation_parent_id:
            estimation_parent_id = sales_order.estimated_task.estimation_parent_id
        else:
            estimation_parent_id = sales_order.estimated_task
        subtask = self.env['project.task'].sudo().create({
            'name': f'Revision {sales_order.estimated_task.sequence_code} - {sales_order.estimated_task.revision_count}',
            'project_id': sales_order.estimated_task.project_id.id,
            'sequence_code': sales_order.estimated_task.sequence_code,
            'parent_id': sales_order.estimated_task.id,
            'crm_lead_id': sales_order.crm_id.id,
            'sales_profit': sales_order.estimated_task.sales_profit,
            'design_charge': sales_order.design_charge,
            'revision_count': sales_order.estimated_task.revision_count,
            'estimation_parent_id': estimation_parent_id.id,
            '_revision_task': True,
            'user_ids': [
                (6, 0, [user.id for user in sales_order.estimated_task.user_ids])],
            'partner_id': sales_order.partner_id.id,
            'material_estimation_ids': [(0, 0, {
                'name': line.name,
                'product_id': line.product_id.id,
                'description': line.description,
                'qty': line.qty,
                'uom_id': line.uom_id.id,
                'unit_price': line.unit_price,
            }) for line in sales_order.estimated_task.material_estimation_ids],
            'labour_estimation_ids': [(0, 0, {
                'name': line.name,
                'labour_id': line.labour_id.id,
                'description': line.description,
                'qty': line.qty,
                'hour': line.hour,
                'unit_price': line.unit_price,
            }) for line in sales_order.estimated_task.labour_estimation_ids],

            'other_over_head_ids': [(0, 0, {
                'name': line.name,
                'service_product': line.service_product.id,
                'description': line.description,
                'qty': line.qty,
                'unit_price': line.unit_price,
                'subtotal': line.subtotal,
            }) for line in sales_order.estimated_task.other_over_head_ids],
        })
