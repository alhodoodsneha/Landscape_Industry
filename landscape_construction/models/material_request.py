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
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class MaterialRequestLineItem(models.Model):
    _name = 'material.request.line.item'
    _description = 'Material Request Line'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'item_id'

    item_id = fields.Many2one('product.product', string='Item',
                              domain=[('is_storable', '=', True)])
    description = fields.Text(sting='Description')
    quantity = fields.Float(string='Quantity')
    material_item_id = fields.Many2one('material.request', string="Item")
    project_id = fields.Many2one('project.project', string='Project',
                                 related='material_item_id.project_id')
    state = fields.Selection(
        [('new', 'Waiting For Approval'),
         ('approved', 'Approved'),
         ('reject', 'Reject')], string='State', default='new',
        related='material_item_id.state')

    uom_id = fields.Many2one('uom.uom', string="Uom")

    @api.onchange('uom_id')
    def _onchange_product(self):
        if self.item_id and self.item_id.uom_id:
            self.uom_id = self.item_id.uom_id.id

    def action_view_on_hand(self):
        self.ensure_one()
        if not self.item_id:
            raise UserError(_("No product is selected for this line item."))
        return {
            'name': _('On-Hand Stock'),
            'type': 'ir.actions.act_window',
            'view_mode': 'list',
            'res_model': 'stock.quant',
            'views': [(self.env.ref('stock.view_stock_quant_tree_editable').id,
                       'list')],
            'target': 'new',
            'domain': [('product_id', '=', self.item_id.id)],
            'context': {
                'search_default_group_by_location_id': 1,
                'search_default_internal_loc': 1,
                'search_default_on_hand': 1,
                'create': False,
                'delete': False,
                'edit': False
            },
        }


class MaterialRequest(models.Model):
    _name = 'material.request'
    _description = 'Material Request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'sequence_code'
    _order = 'id desc'

    sequence_code = fields.Char(
        string="Sequence Code",
        copy=False,
        readonly=True,
        index='trigram',
        default=lambda self: _('New'),
    )

    project_id = fields.Many2one(
        comodel_name='project.project',
        string="Project",
        copy=False,
    )
    user_id = fields.Many2one('res.users', string='User', tracking=True,
                              default=lambda self: self.env.user)

    date = fields.Date(string='Date', default=fields.Date.today(),
                       tracking=True)

    vendor_id = fields.Many2one('res.partner',
                                string="Vendor")

    state = fields.Selection(
        [('new', 'Waiting For Approval'),
         ('approved', 'Approved'),
         ('reject', 'Reject')],
        string='State',
        default='new',
        tracking=True)

    pm_approve_date = fields.Date(string="Approval Date", tracking=True)
    rejected_date = fields.Date(string='Reject Date', tracking=True)
    rejected_by = fields.Many2one('res.users', string='Reject By',
                                  tracking=True)
    approved_by = fields.Many2one('res.users', string='Approved By',
                                  tracking=True)

    request_line_ids = fields.One2many('material.request.line.item',
                                       'material_item_id',
                                       string="material Request")
    requisition_reason = fields.Text(string='Requisition Reason',
                                     tracking=True)
    rfq_create = fields.Boolean(string="RFQ Created", default=False)

    @api.model_create_multi
    def create(self, vals_list):
        """
        Auto set Material Code on creation
        """
        for vals in vals_list:
            if vals.get('sequence_code', _('New')) == _('New'):
                seq_date = fields.Datetime.context_timestamp(
                    self, fields.Datetime.to_datetime(vals['created_date']),
                ) if 'created_date' in vals else None
                vals['sequence_code'] = self.env['ir.sequence'].next_by_code(
                    'material.request.code', sequence_date=seq_date) or _(
                    'New')
        return super().create(vals_list)

    def action_create_rfq(self):
        if self.state != 'approved':
            raise UserError(_("Please Approve the request then proceed!!"))
        oder_line = []
        for rec in self.request_line_ids:
            oder_line.append((0, 0, {
                'product_id': rec.item_id.id,
                'product_qty': rec.quantity,
                'product_uom_id': rec.uom_id.id,
            }))
        self.env['purchase.order'].create({
            'partner_id': self.vendor_id.id,
            'project_id': self.project_id.id,
            'material_id': self.id,
            'order_line': oder_line,
            'purchase_analytic_id': self.project_id.material_analytic_id.id,
        })
        self.rfq_create = True

    def action_first_approve_request(self):
        self.state = 'approved'
        self.approved_by = self.env.user.id
        self.pm_approve_date = fields.Date.today()
        if not self.env.user.email:
            raise UserError(_("Please Configure Your Email"))
        if self.user_id.email:
            subject = f"Material Request {self.sequence_code} for {self.project_id.name} Approved"
            body = f"""
                         <p>Hello {self.user_id.name},</p>
                         <p>Material Request For Job  {self.project_id.name} is fully approved on {self.pm_approve_date}.</p>
                         <p>Best Regards,</p>
                         <p>{self.approved_by.name}</p>
                         """
            mail_values_employee = {
                'subject': subject,
                'body_html': body,
                'email_from': self.approved_by.email,
                'email_to': self.user_id.email,
            }
            mail_employee = self.env['mail.mail'].sudo().create(
                mail_values_employee)
            mail_employee.send()

    def action_reject_request(self):
        self.state = 'reject'
        self.rejected_by = self.env.user.id
        self.rejected_date = fields.Date.today()
        if not self.env.user.email:
            raise UserError(_("Please Configure Your Email"))
        if self.user_id.email:
            subject = f"Material Request {self.sequence_code} Rejected BY {self.env.user.name} "
            body = f"""
                                           <p>Hello {self.user_id.name},</p>
                                           <p>Material Request For Job  {self.project_id.name}is rejected by {self.env.user.name}.</p>
                                           <p>Best Regards,</p>
                                           <p>{self.env.user.name}</p>
                                           """
            mail_values_employee = {
                'subject': subject,
                'body_html': body,
                'email_from': self.env.user.email,
                'email_to': self.user_id.email,
            }
            mail_employee = self.env['mail.mail'].sudo().create(
                mail_values_employee)
            mail_employee.send()

    def action_view_project_material_request(self):
        return {
            'name': 'Material Request',
            'view_type': 'list',
            'view_mode': 'list,form',
            'res_model': 'purchase.order',
            'domain': [('material_id', '=', self.id)],
            'type': 'ir.actions.act_window',
            'context': {'default_project_id': self.project_id.id,
                        'delete': False,
                        }
        }


