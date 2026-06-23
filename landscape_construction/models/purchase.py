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
from odoo import api, models, fields


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    allowed_analytic_ids = fields.Many2many(
        'account.analytic.account',
        compute='_compute_allowed_analytic_ids'
    )
    purchase_analytic_id = fields.Many2one(
        'account.analytic.account',
        domain="[('id', 'in', allowed_analytic_ids)]",
        string="Analytic")

    material_id = fields.Many2one('material.request',
                                  string="Material Request")

    sales_order_id = fields.Many2one(
        'sale.order',
        string="Sales Order",
    )


    @api.depends('project_id')
    def _compute_allowed_analytic_ids(self):
        for order in self:
            ids = []
            if order.project_id:
                if order.project_id.material_analytic_id:
                    ids.append(order.project_id.material_analytic_id.id)
                if order.project_id.subcontract_analytic_id:
                    ids.append(order.project_id.subcontract_analytic_id.id)
                if order.project_id.service_analytic_id:
                    ids.append(order.project_id.service_analytic_id.id)
            order.allowed_analytic_ids = [(6, 0, ids)]

    def _prepare_invoice(self):
        res = super()._prepare_invoice()
        if self.project_id:
            res.update({
                'project_id': self.project_id.id,
            })
        return res


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def _prepare_account_move_line(self, move=False):
        res = super()._prepare_account_move_line(move)
        if self.order_id.purchase_analytic_id:
            res['analytic_distribution'] = {
                self.order_id.purchase_analytic_id.id: 100.0, }
        return res
