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
