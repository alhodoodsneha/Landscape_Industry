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
from odoo import fields, models, api,_
from odoo.exceptions import UserError


class CreateInvoiceLines(models.TransientModel):
    _name = 'advance.invoice.line.wizard'
    _description = "Invoice Lines"

    name = fields.Char(
        string="Deliverables",
        store=True
    )
    dev_id = fields.Many2one('project.deliverables', string="Deliverables")
    subtotal = fields.Float(string="Subtotal", store=True)
    invoiced_percentage = fields.Float(string="Invoiced Percentage")
    balance_percentage = fields.Float(string="Balance Percentage")
    to_invoice_percentage = fields.Float(string="To Invoice %")
    invoice_price = fields.Float(string="To Invoice Price",
                                 compute='_compute_invoice_price')
    wizard_id = fields.Many2one('advance.invoice.wizard', string="Wizard")

    @api.depends('subtotal', 'to_invoice_percentage')
    def _compute_invoice_price(self):
        for rec in self:
            if rec.to_invoice_percentage > 0 and rec.subtotal > 0:
                rec.invoice_price = (rec.subtotal * rec.to_invoice_percentage) / 100
            else:
                rec.invoice_price = 0.0

    @api.onchange('to_invoice_percentage')
    def _onchange_to_invoice_percentage(self):
        if self.to_invoice_percentage > self.balance_percentage:
            raise UserError(
                _("Invoice Percentage Must Be Less Than Balance Percentage!!"))

class CreateInvoiceAdvance(models.TransientModel):
    _name = 'advance.invoice.wizard'
    _description = "Advance Invoice"

    project_id = fields.Many2one('project.project', string="Project")
    invoice_line_ids = fields.One2many('advance.invoice.line.wizard',
                                       'wizard_id', string="Invoice Line")

    def action_adv_create_adv(self):
        project_id = self.project_id
        invoice_lines = []
        total_inv_pr = 0
        analytic_id = project_id.account_id.id
        for rec in self.invoice_line_ids:
            if rec.to_invoice_percentage > 0:
                last_inv = False
                total_percentage = rec.to_invoice_percentage + rec.invoiced_percentage
                if total_percentage >= 100:
                    last_inv = True
                invoice_price = ((rec.subtotal * rec.to_invoice_percentage) / 100)
                if last_inv:
                    amount_last = sum(self.env['account.move.line'].search(
                            [('boq', '=', True),
                             ('move_id.move_type', '=', 'out_invoice'),
                             ('move_id.state', '=', 'posted'),
                             ('boq_line', '=', rec.dev_id.id)]).mapped('price_subtotal'))
                    amount_to_ls = amount_last + invoice_price
                    if rec.subtotal != amount_to_ls:
                        invoice_price = rec.subtotal - amount_last
                        total_inv_pr = total_inv_pr + invoice_price
                        invoice_lines.append((0, 0, {
                            'name': rec.dev_id.name,
                            'quantity': 1,
                            'price_unit': invoice_price,
                            'boq_line': rec.dev_id.id,
                            'boq': True,
                            'analytic_distribution': {
                                analytic_id: 100.0,
                            },
                            'invoice_per': rec.to_invoice_percentage,
                        }))
                    else:
                        total_inv_pr = total_inv_pr + invoice_price
                        invoice_lines.append((0, 0, {
                            'name':  rec.dev_id.name,
                            'quantity': 1,
                            'price_unit': invoice_price,
                            'boq_line': rec.dev_id.id,
                            'boq': True,
                            'analytic_distribution': {
                                analytic_id: 100.0,
                            },
                            'invoice_per': rec.to_invoice_percentage,
                        }))
                else:
                    total_inv_pr = total_inv_pr + invoice_price
                    invoice_lines.append((0, 0, {
                        'name':rec.dev_id.name,
                        'quantity': 1,
                        'price_unit': invoice_price,
                        'boq_line': rec.dev_id.id,
                        'boq': True,
                        'analytic_distribution': {
                            analytic_id: 100.0,
                        },
                        'invoice_per': rec.to_invoice_percentage,
                    }))
        account_move = self.env['account.move'].create({
            'partner_id': project_id.partner_id.id,
            'move_type': 'out_invoice',
            'is_prj_inv':True,
            'invoice_line_ids': invoice_lines,
            'project_id': project_id.id,
            'sale_inv_id': project_id.sale_order_id.id if project_id.sale_order_id else None,
            'user_id': project_id.sale_order_id.user_id.id if project_id.sale_order_id else None,
        })
