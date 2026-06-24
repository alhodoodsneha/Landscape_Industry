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

{
    'name': 'Landscape Customization',
    'version': '19.0.0.0.1',
    'category': 'Sales/CRM',
    'summary': 'Landscape Customization',
    'description': 'Landscape Customization',
    'author': 'Alhodood Technologies',
    'depends': [
        'crm', 'mail', 'project', 'hr_timesheet', 'stock',
        'sale_management', 'purchase', 'hr', 'account','sale_crm','project_mrp',
        'sale_project','account_analytic_parent','project_purchase','sale_pdf_quote_builder','fleet','maintenance'
    ],
    'data': [
        'data/ir_sequence.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/inspection_team.xml',
        'views/ir_action_report.xml',
        'views/design_team.xml',
        'views/estimation_team.xml',
        'views/product_product.xml',
        'views/hr_job.xml',
        'views/crm_lead.xml',
        'views/project_project.xml',
        'views/project_milestone.xml',
        'views/project_task.xml',
        'views/sale_order.xml',
        'views/material_request.xml',
        'views/account_move.xml',
        'views/purchase_order.xml',
        'views/maintenance_equipment.xml',
        'views/site_operation.xml',
        'views/inspectionl_report_template.xml',
        'wizard/estimation_refuse_reason.xml',
        'wizard/advance_invoice_wizard.xml',
        'wizard/site_operation_wizard.xml',
    ],
    'assets': {},
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
