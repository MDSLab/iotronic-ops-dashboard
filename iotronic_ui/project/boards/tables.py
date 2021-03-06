# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import logging

from django import template
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy

from horizon import tables

from openstack_dashboard import api

LOG = logging.getLogger(__name__)


class CreateBoardLink(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Board")
    url = "horizon:project:boards:create"
    classes = ("ajax-modal",)
    icon = "plus"
    # policy_rules = (("iot", "iot:create_board"),)


class EditBoardLink(tables.LinkAction):
    name = "edit"
    verbose_name = _("Edit")
    url = "horizon:project:boards:update"
    classes = ("ajax-modal",)
    icon = "pencil"
    # policy_rules = (("iot", "iot:update_board"),)

    """
    def allowed(self, request, role):
        return api.keystone.keystone_can_edit_role()
    """


class RestoreServices(tables.BatchAction):
    name = "restoreservices"

    @staticmethod
    def action_present(count):
        return u"Restore Services"

    @staticmethod
    def action_past(count):
        return u"Restore Services"

    def allowed(self, request, board=None):
        return True

    def action(self, request, board_id):
        api.iotronic.restore_services(request, board_id)


class RemovePluginsLink(tables.LinkAction):
    name = "removeplugins"
    verbose_name = _("Remove Plugin(s)")
    url = "horizon:project:boards:removeplugins"
    classes = ("ajax-modal",)
    icon = "plus"
    # policy_rules = (("iot", "iot:create_board"),)


class DeleteBoardsAction(tables.DeleteAction):
    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete Board",
            u"Delete Boards",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Deleted Board",
            u"Deleted Boards",
            count
        )
    # policy_rules = (("iot", "iot:delete_board"),)

    """
    def allowed(self, request, role):
        return api.keystone.keystone_can_edit_role()
    """

    def delete(self, request, board_id):
        api.iotronic.board_delete(request, board_id)


class BoardFilterAction(tables.FilterAction):

    # If uncommented it will appear the select menu list of fields
    # and filter button
    """
    filter_type = "server"
    filter_choices = (("name", _("Board Name ="), True),
                      ("type", _("Type ="), True),
                      ("status", _("Status ="), True))
    """

    def filter(self, table, boards, filter_string):
        """Naive case-insensitive search."""
        q = filter_string.lower()
        return [board for board in boards
                if q in board.name.lower()]

def show_services(board_info):
    template_name = 'project/boards/_cell_services.html'
    context = board_info._info
    # LOG.debug("CONTEXT: %s", context)
    return template.loader.render_to_string(template_name,
                                            context)


class BoardsTable(tables.DataTable):
    name = tables.WrappingColumn('name', link="horizon:project:boards:detail",
                                 verbose_name=_('Board Name'))
    type = tables.Column('type', verbose_name=_('Type'))
    # mobile = tables.Column('mobile', verbose_name=_('Mobile'))
    uuid = tables.Column('uuid', verbose_name=_('Board ID'))
    # code = tables.Column('code', verbose_name=_('Code'))
    status = tables.Column('status', verbose_name=_('Status'))
    # location = tables.Column('location', verbose_name=_('Geo'))
    services = tables.Column(show_services, verbose_name=_('Services'))
    # extra = tables.Column('extra', verbose_name=_('Extra'))

    # Overriding get_object_id method because in IoT service the "id" is
    # identified by the field UUID
    def get_object_id(self, datum):
        return datum.uuid

    class Meta(object):
        name = "boards"
        verbose_name = _("boards")
        row_actions = (EditBoardLink, RestoreServices, 
                       RemovePluginsLink, DeleteBoardsAction)
        table_actions = (BoardFilterAction, CreateBoardLink, 
                         RestoreServices, DeleteBoardsAction)
