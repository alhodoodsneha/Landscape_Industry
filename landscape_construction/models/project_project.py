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


class ProjectDeliverables(models.Model):
    _name = 'project.deliverables'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Project Deliverables'
    _rec_name = 'name'
    _order = 'id asc'

    name = fields.Char(
        string="Deliverables",
        tracking=True
    )

    project_id = fields.Many2one(
        'project.project',
        string="Project"
    )

    description = fields.Text(
        string="Description",
        tracking=True
    )

    status = fields.Selection(
        [('pending','Pending'),
         ('in_progress','In Progress'),
         ('completed','Completed')
         ],string="Status",
        tracking=True,
        default='pending'
    )

    remark = fields.Char(
        string="Remarks"
    )

    per_of_weight = fields.Float(
        string="% weight",
        default=0.0
    )

    total_amount = fields.Float(
        string="Total amount",
        compute='_compute_total_amount'

    )

    invoiced_per = fields.Float(
        string="Invoiced %",
        compute='_compute_total_inv_per'
    )

    balance_per = fields.Float(
        string="Balance %",
        compute='_compute_total_bal_per'
    )

    invoiced_amount = fields.Float(
        string="Invoiced amount",
    )

    balance_amount = fields.Float(
        string="Balance Amount",

    )

    @api.depends('name','project_id','per_of_weight','project_id.quote_amount')
    def _compute_total_amount(self):
        for rec in self:
            rec.total_amount = 0.0
            if rec.project_id.quote_amount > 0:
                rec.total_amount = (rec.project_id.quote_amount * rec.per_of_weight)/100

    @api.depends('name','project_id','per_of_weight')
    def _compute_total_inv_per(self):
        for rec in self:
            invoice = self.env['account.move'].search(
                [('project_id', '=', rec.project_id.id),
                 ('move_type', '=', 'out_invoice'),
                 ('is_prj_inv', '=', True),
                 ('state', '=', 'posted')])
            if invoice:
                lines = self.env['account.move.line'].search(
                    [('move_id', 'in', invoice.ids),
                     ('boq_line', '=', rec.id)])
                if lines:
                    inv_per = sum(lines.mapped('invoice_per'))
                    if inv_per > 100:
                        rec.invoiced_per = 100
                    else:
                        rec.invoiced_per = inv_per
                else:
                    rec.invoiced_per = 0.0
            else:
                rec.invoiced_per = 0.0

    @api.depends('name','project_id','per_of_weight','invoiced_per')
    def _compute_total_bal_per(self):
        for rec in self:
            if rec.invoiced_per:
                rec.balance_per = 100 - rec.invoiced_per
            else:
                rec.balance_per = 100



class Project(models.Model):
    _inherit = 'project.project'

    is_internal = fields.Boolean(
        string="Internal",
        default=False
    )

    crm_lead_id = fields.Many2one(
        'crm.lead',
        string="Crm"
    )

    sales_order = fields.Many2one(
        'sale.order',
        string="Sales Order"
    )

    sequence_code = fields.Char(
        string="Sequence"
    )

    project_loc = fields.Many2one(
        'stock.location',
        string='Location'
    )
    subcontract_analytic_id = fields.Many2one(
        'account.analytic.account',
        string='Subcontract'
    )

    labour_analytic_id = fields.Many2one(
        'account.analytic.account',
        string="Labour"
    )

    material_analytic_id = fields.Many2one(
        'account.analytic.account',
        string="material"
    )
    service_analytic_id = fields.Many2one(
        'account.analytic.account',
        string="Service"
    )

    quote_amount = fields.Float(
        string="Quote Amount",
    )
    is_allow_invoice = fields.Boolean(
        string="Is Allow Invoicing",
        compute='_compute_is_allow_invoice'
    )

    prd_task = fields.Many2one(
        'project.task',
        string="PRD Task"
    )
    ins_task = fields.Many2one(
        'project.task',
        string="Ins Task"
    )
    del_task = fields.Many2one(
        'project.task',
        string="Del Task"
    )
    qa_qc_task = fields.Many2one(
        'project.task',
        string="QA/QC Task"
    )

    is_project_manager = fields.Boolean(
        compute="_compute_is_project_manager",
        string="Is Project Manager"
    )

    project_deliverable_ids = fields.One2many(
        'project.deliverables',
        'project_id',
        string="Project Deliverables"
    )

    total_invoiced_amount = fields.Monetary(string="Total Invoiced Amount",
                                            currency_field='currency_id',
                                            compute="_compute_invoice_details", )

    total_balance_amount = fields.Monetary(string="Total Balance Amount",
                                           currency_field='currency_id',
                                           compute="_compute_invoice_details", )
    total_invoiced_amount_with_tax = fields.Monetary(
        string="Total Invoiced Amount With Tax",
        currency_field='currency_id',
        compute="_compute_invoice_details")

    pending_invoice_amount = fields.Monetary(string="Due Invoice Amount",
                                             currency_field='currency_id',
                                             compute="_compute_invoice_pending", )

    @api.model
    def create(self, vals):
        res = super(Project, self).create(vals)
        res.sequence_code = self.env['ir.sequence'].next_by_code(
            'project.sequence')
        res.allow_billable = True
        prd_task = self.env['project.task'].sudo().create({
            'name': res.name + 'Production',
            'is_production': True,
            'project_id': res.id,
        })
        ins_task = self.env['project.task'].sudo().create({
            'name': res.name + 'Installation',
            'is_installation': True,
            'project_id': res.id,
        })
        del_task = self.env['project.task'].sudo().create({
            'name': res.name + 'Delivery',
            'is_delivery': True,
            'project_id': res.id,
        })
        qa_qc_task = self.env['project.task'].sudo().create({
            'name': res.name + 'QA/QC',
            'is_qa_qc': True,
            'project_id': res.id,
        })
        res.prd_task = prd_task.id
        res.ins_task = ins_task.id
        res.del_task = del_task.id
        res.qa_qc_task = qa_qc_task.id
        location_vals = {
            'name': res.name,
            'location_id': self.env.ref('stock.stock_location_stock').id,
            'usage': 'internal',
        }
        location = self.env['stock.location'].sudo().create(location_vals)
        res.project_loc = location.id
        if res.account_id:
            labour_id = self.env['account.analytic.account'].create({
                'name': 'LAB - ' + res.sequence_code,
                'plan_id': res.account_id.plan_id.id,
                'parent_id': res.account_id.id,
                'partner_id': res.account_id.partner_id.id,
                'code': '01'
            })
            res.labour_analytic_id = labour_id.id
            subcontract = self.env['account.analytic.account'].create({
                'name': 'SUB - ' + res.sequence_code,
                'plan_id': res.account_id.plan_id.id,
                'parent_id': res.account_id.id,
                'partner_id': res.account_id.partner_id.id,
                'code': '02'
            })
            res.subcontract_analytic_id = subcontract.id
            material = self.env['account.analytic.account'].create({
                'name': 'MTl - ' + res.sequence_code,
                'plan_id': res.account_id.plan_id.id,
                'parent_id': res.account_id.id,
                'partner_id': res.account_id.partner_id.id,
                'code': '03'
            })
            res.material_analytic_id = material.id
            service = self.env['account.analytic.account'].create({
                'name': 'SRV - ' + res.sequence_code,
                'plan_id': res.account_id.plan_id.id,
                'parent_id': res.account_id.id,
                'partner_id': res.account_id.partner_id.id,
                'code': '04'
            })
            res.service_analytic_id = service.id
        return res

    @api.depends('quote_amount', 'user_id', 'name', 'total_balance_amount',
                 'total_invoiced_amount_with_tax')
    def _compute_invoice_details(self):
        for record in self:
            record.total_invoiced_amount = 0.0
            record.total_invoiced_amount_with_tax = 0.0
            record.total_balance_amount = 0.0
            invoices = self.env['account.move'].search(
                [('project_id', '=', record.id), ('is_prj_inv', '=', True),
                 ('move_type', '=', 'out_invoice'), ('state', '=', 'posted')])
            if invoices:
                record.total_invoiced_amount = sum(
                    invoices.mapped('amount_untaxed_signed'))
                record.total_balance_amount = record.quote_amount - sum(
                    invoices.mapped('amount_untaxed_signed'))
                record.total_invoiced_amount_with_tax = sum(
                    invoices.mapped('amount_total_signed'))

    @api.depends('total_invoiced_amount', 'user_id', 'pending_invoice_amount')
    def _compute_invoice_pending(self):
        for record in self:
            record.pending_invoice_amount = 0.0
            invoices = self.env['account.move'].search(
                [('project_id', '=', record.id), ('is_prj_inv', '=', True),
                 ('move_type', '=', 'out_invoice'), ('state', '!=', 'cancel')])
            if invoices:
                record.pending_invoice_amount = sum(
                    invoices.mapped('amount_residual'))

    @api.depends('user_id', 'name')
    def _compute_is_project_manager(self):
        for rec in self:
            if rec.user_id.id == self.env.user.id:
                rec.is_project_manager = True
            else:
                rec.is_project_manager = False

    @api.depends('user_id', 'name')
    def _compute_is_allow_invoice(self):
        for rec in self:
            if self.env.user.has_group(
                    'landscape_construction.group_allow_create_invoice'):
                rec.is_allow_invoice = True
            else:
                rec.is_allow_invoice = False

    def action_create_invoices(self):
        invoice = self.env['account.move'].search(
            [('project_id', '=', self.id),('is_prj_inv','=',True),
             ('move_type', '=', 'out_invoice'), ('state', '=', 'draft')])
        if invoice:
            raise UserError(
                _("Already Pending Invoices Are There Please Post Or Cancel It !!"))
        val_list = []
        if self.project_deliverable_ids:
            total_weight = sum(self.project_deliverable_ids.mapped('per_of_weight'))
            if total_weight > 100:
                raise UserError(
                    _("Total Deliverables weight cannot be exceed 100"))
            if total_weight < 100:
                raise UserError(
                    _("Total Deliverables weight cannot be less than 100"))
            remaining_lines = self.project_deliverable_ids.filtered(
                lambda l: l.balance_per > 0)

            if not remaining_lines:
                raise UserError(
                    _("There is nothing to invoice. All deliverables are fully invoiced."))
            for rec in self.project_deliverable_ids:
                if rec.balance_per > 0:
                    val_list.append((0, 0, {
                        'name': rec.name,
                        'dev_id': rec.id,
                        'subtotal': rec.total_amount,
                        'invoiced_percentage': rec.invoiced_per,
                        'balance_percentage': rec.balance_per,
                    }))
            verify_wizard = self.env['advance.invoice.wizard'].create({
                'project_id': self.id,
                'invoice_line_ids': val_list,
            })
            return {
                'name': 'Create Invoice',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                "view_type": "form",
                'res_model': 'advance.invoice.wizard',
                'res_id': verify_wizard.id,
                'target': 'new',
                'context': {
                    'active_id': self.id,
                }
            }
        else:
            raise UserError(
                _("Missing Deliverable Lines !!"))

    def action_view_invoices(self):
        return {
            'name': 'Customer Invoices',
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'view_mode': 'list,form',
            'domain': [('project_id', '=', self.id),
                       ('move_type', 'in', ('out_invoice', 'out_refund'))],
            'target': 'current',
        }

    def action_view_project_material_request(self):
        return {
            'name': 'Material Request',
            'view_type': 'list',
            'view_mode': 'list,form',
            'res_model': 'material.request',
            'domain': [('project_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'context': {'default_project_id': self.id,
                        'delete': False,
                        }
        }

    def action_view_project_purchase_order(self):
        return {
            'name': 'Purchase Order',
            'view_type': 'list',
            'view_mode': 'list,form',
            'res_model': 'purchase.order',
            'domain': [('project_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'context': {'default_project_id': self.id,
                        'delete': False,
                        }
        }

    def action_view_daily_site_report(self):
        return {
            'name': 'Daily Site Report',
            'view_type': 'list',
            'view_mode': 'list,form',
            'res_model': 'site.operation.report',
            'domain': [('project_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'context': {'default_project_id': self.id,
                        'delete': False,
                        }
        }