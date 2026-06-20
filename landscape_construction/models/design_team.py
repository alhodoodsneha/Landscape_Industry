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
from odoo import models,fields, api


class DesignTeamMember(models.Model):
    _name = 'design.team.member'
    _description = 'Design Team'
    _rec_name = 'name'

    name = fields.Char(string="Name")
    team_manager_id  = fields.Many2one(
        'res.users',
        string='Design Manager',
        domain=lambda self: [('id', 'in', self._get_group_user_ids())]
    )
    team_member_ids  = fields.Many2many(
        'res.users',
        string="Members",
        domain=lambda self: [('id', 'in', self._get_group_ist_user_ids())]
    )

    @api.model
    def _get_group_user_ids(self):
        group = self.env.ref('landscape_construction.group_design_manager')
        return group.user_ids.ids if group else []

    @api.model
    def _get_group_ist_user_ids(self):
        group = self.env.ref('landscape_construction.group_design_user')
        return group.user_ids.ids if group else []

