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
import base64
import io
import xlsxwriter
from odoo import fields, models, api,_
from odoo.exceptions import UserError

class SiteOperationReportWizard(models.TransientModel):
    _name = 'site.operation.report.wizard'
    _description = "Site Operation Report"

    project_id = fields.Many2one(
        'project.project',
        string='Project'
    )

    start_date = fields.Date(
        string="Start Date"
    )

    end_date = fields.Date(
        string="End Date"
    )

    def action_print_xlsx(self):
        domain = []
        if self.start_date:
            domain.append(
                ('date','>=',self.start_date),
            )
        if self.end_date:
            domain.append(
                ('date','<=', self.end_date),
            )
        domain.append(
            ('project_id', '=', self.project_id)
        )
        site_report_ids = self.env['site.operation.report'].search(domain)
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet('Site Operation Report')
        title_format = workbook.add_format({
            'bold': True, 'align': 'center', 'valign': 'vcenter',
            'font_size': 16, 'bg_color': '#0A66C2', 'font_color': 'white'
        })
        header_format = workbook.add_format({
            'bold': True, 'bg_color': '#D9E1F2', 'border': 1, 'align': 'center'
        })
        header2_format = workbook.add_format({
            'bold': True, 'bg_color': '#c6dbf3', 'border': 1, 'align': 'center'
        })
        header3_format = workbook.add_format({
            'bold': True, 'bg_color': '#9eb0c4', 'border': 1, 'align': 'center'
        })
        header4_format = workbook.add_format({
            'bold': True, 'bg_color': '#81b1e3', 'border': 1, 'align': 'center'
        })
        header5_format = workbook.add_format({
            'bold': True, 'bg_color': '#97c3e6', 'border': 1, 'align': 'center'
        })
        header6_format = workbook.add_format({
            'bold': True, 'bg_color': '#94cbf7', 'border': 1, 'align': 'center'
        })
        cell_format = workbook.add_format({'border': 1, 'align': 'center'})
        worksheet.set_column('A:A', 20)
        worksheet.set_column('B:B', 20)
        worksheet.set_column('C:C', 25)
        worksheet.set_column('D:D', 25)
        worksheet.set_column('E:E', 25)
        worksheet.set_column('F:F', 25)
        worksheet.set_column('G:G', 25)
        worksheet.set_column('H:H', 25)
        worksheet.set_column('I:I', 25)
        worksheet.set_column('J:J', 25)
        worksheet.merge_range('C1:F3', "Site Operation Report",
                              title_format)
        row = 5
        worksheet.write(row, 2, "Project", header_format)
        worksheet.write(row, 3, self.project_id.name, header_format)
        row = row +1
        worksheet.write(row, 2, "Start Date", header_format)
        worksheet.write(row, 3,str(self.start_date), header_format)
        row = row + 1
        worksheet.write(row, 2, "End Date", header_format)
        worksheet.write(row, 3,str(self.end_date), header_format)
        row = row + 3
        worksheet.merge_range(row, 2,row,4, "Work Progress", header2_format)
        row = row + 2
        worksheet.write(row, 2, "Task", header3_format)
        worksheet.write(row, 3, "Planned Qty", header3_format)
        worksheet.write(row, 4, "Completed Qty", header3_format)
        for site in site_report_ids:
            for s_line in site.progress_line_ids:
                row = row + 1
                worksheet.write(row, 2,s_line.task_id.name, cell_format)
                worksheet.write(row, 3,s_line.planned_qty, cell_format)
                worksheet.write(row, 4,s_line.completed_qty, cell_format)
        row = row + 3
        worksheet.merge_range(row, 2, row, 4, "Labour Attendance", header4_format)
        row = row + 2
        worksheet.write(row, 2, "Employee", header3_format)
        worksheet.write(row, 3, "Job", header3_format)
        worksheet.write(row, 4, "Hours", header3_format)
        for site in site_report_ids:
            for s_line in site.labor_line_ids:
                row = row + 1
                worksheet.write(row, 2, s_line.employee_id.name, cell_format)
                worksheet.write(row, 3, s_line.job_id.name, cell_format)
                worksheet.write(row, 4, s_line.hours, cell_format)
        row = row + 3
        worksheet.merge_range(row, 2, row, 4, "Equipments",
                              header5_format)
        row = row + 2
        worksheet.merge_range(row, 2,row,3 ,"Vehicle", header3_format)
        worksheet.write(row, 4, "Hours", header3_format)
        for site in site_report_ids:
            for s_line in site.equipment_line_ids:
                row = row + 1
                worksheet.merge_range(row, 2,row,3, s_line.vehicle_id.name, cell_format)
                worksheet.write(row, 4, s_line.total_hour, cell_format)
        row = row + 3
        worksheet.merge_range(row, 2, row, 4, "Material Consumption",
                              header6_format)
        row = row + 2
        worksheet.write(row, 2, "Product", header3_format)
        worksheet.write(row, 3, "Qty", header3_format)
        worksheet.write(row, 4, "Uom", header3_format)
        for site in site_report_ids:
            for s_line in site.material_line_ids:
                row = row + 1
                worksheet.write(row, 2, s_line.product_id.name, cell_format)
                worksheet.write(row, 3, s_line.qty, cell_format)
                worksheet.write(row, 4, s_line.uom_id.name, cell_format)
        workbook.close()
        output.seek(0)
        attachment = self.env['ir.attachment'].create({
            'name': 'Site Operation Report.xlsx',
            'type': 'binary',
            'datas': base64.b64encode(output.read()),
            'mimetype': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })
        return {
            'type': 'ir.actions.act_url',
            'url': '/web/content/%s?download=true' % attachment.id,
            'target': 'self'
        }
