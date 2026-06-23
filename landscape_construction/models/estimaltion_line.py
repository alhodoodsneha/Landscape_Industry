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

class LabourEstimation(models.Model):
    _name = 'labour.estimation'
    _description = 'Labour Estimation'
    _rec_name = 'name'

    name = fields.Char(string="Name")
    task_id = fields.Many2one('project.task', string="Task")
    labour_id = fields.Many2one('hr.job', string="Labour")
    project_id = fields.Many2one('project.project', string="Project", related='task_id.project_id', store=True)
    description = fields.Text(string="Description")
    qty = fields.Float(string="Quantity")
    hour = fields.Float(string="Hour")
    total_hour = fields.Float(string="Total Hour", compute='_compute_total_hour')
    unit_price = fields.Float(string="Unit Price", default=0.0)
    subtotal = fields.Float(string="SubTotal", compute='_compute_subtotal')

    @api.onchange('labour_id')
    def _onchange_job_id(self):
        if self.labour_id:
            self.unit_price = self.labour_id.hour_rate
        else:
            self.unit_price = 0.0

    @api.depends('project_id', 'qty', 'hour')
    def _compute_total_hour(self):
        for rec in self:
            rec.total_hour = rec.qty * rec.hour

    @api.depends('project_id', 'qty', 'unit_price', 'total_hour')
    def _compute_subtotal(self):
        for rec in self:
            rec.subtotal = rec.total_hour * rec.unit_price


class MaterialEstimation(models.Model):
    _name = 'material.estimation'
    _description = 'Material Estimation'
    _rec_name = 'name'

    name = fields.Char(string="Name")
    task_id = fields.Many2one('project.task', string="Task")
    project_id = fields.Many2one('project.project', string="Project", related='task_id.project_id', store=True)
    product_id = fields.Many2one('product.product', string="Material",)
    description = fields.Text(string="Description")
    qty = fields.Float(string="Quantity")
    unit_price = fields.Float(string="Unit Price", default=0.0)
    uom_id = fields.Many2one('uom.uom', string="Units")
    subtotal = fields.Float(string="SubTotal", compute='_compute_subtotal')

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.unit_price = self.product_id.standard_price
            if self.product_id.uom_id:
                self.uom_id = self.product_id.uom_id.id
        else:
            self.unit_price = 0.0

    @api.depends('project_id', 'qty', 'unit_price')
    def _compute_subtotal(self):
        for rec in self:
            rec.subtotal = rec.qty * rec.unit_price



class OtherOverHead(models.Model):
    _name = 'other.over.head'
    _description = 'Other Over Head'
    _rec_name = 'name'

    name = fields.Char(string="Name")
    task_id = fields.Many2one('project.task', string="Task")
    project_id = fields.Many2one('project.project', string="Project", related='task_id.project_id', store=True)
    service_product = fields.Many2one('product.product', domain="[('type', '=', 'service')]",string="Service")
    description = fields.Text(string="Description")
    qty = fields.Float(string="Quantity")
    unit_price = fields.Float(string="Unit Price", default=0.0)
    subtotal = fields.Float(string="SubTotal", compute='_compute_subtotal')

    @api.onchange('service_product')
    def _onchange_product_id(self):
        if self.service_product:
            self.unit_price = self.service_product.standard_price
        else:
            self.unit_price = 0.0

    @api.depends('service_product', 'qty', 'unit_price')
    def _compute_subtotal(self):
        for rec in self:
            rec.subtotal = rec.qty * rec.unit_price
