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

from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext_lazy

from horizon import tables

from openstack_dashboard import api
from openstack_dashboard import policy

LOG = logging.getLogger(__name__)


class CreatePluginLink(tables.LinkAction):
    name = "create"
    verbose_name = _("Create Plugin")
    url = "horizon:project:plugins:create"
    classes = ("ajax-modal",)
    icon = "plus"
    # policy_rules = (("iot", "iot:create_board"),)


class EditPluginLink(tables.LinkAction):
    name = "edit"
    verbose_name = _("Edit")
    url = "horizon:project:plugins:update"
    classes = ("ajax-modal",)
    icon = "pencil"
    # policy_rules = (("iot", "iot:update_board"),)

    """
    def allowed(self, request, plugin):

        # LOG.debug("MELO ALLOWED: %s %s %s", self, request, plugin)
        # LOG.debug("MELO user: %s", request.user.id)

        return True
    """


class InjectPluginLink(tables.LinkAction):
    name = "inject"
    verbose_name = _("Inject")
    url = "horizon:project:plugins:inject"
    classes = ("ajax-modal",)
    icon = "plus"
    # policy_rules = (("iot", "iot:create_board"),)


class StartPluginLink(tables.LinkAction):
    name = "start"
    verbose_name = _("Start")
    url = "horizon:project:plugins:start"
    classes = ("ajax-modal",)
    icon = "plus"
    # policy_rules = (("iot", "iot:create_board"),)


class StopPluginLink(tables.LinkAction):
    name = "stop"
    verbose_name = _("Stop")
    url = "horizon:project:plugins:stop"
    classes = ("ajax-modal",)
    icon = "plus"
    # policy_rules = (("iot", "iot:create_board"),)


class CallPluginLink(tables.LinkAction):
    name = "call"
    verbose_name = _("Call")
    url = "horizon:project:plugins:call"
    classes = ("ajax-modal",)
    icon = "plus"
    # policy_rules = (("iot", "iot:create_board"),)


class RemovePluginLink(tables.LinkAction):
    name = "remove"
    verbose_name = _("Remove from board(s)")
    url = "horizon:project:plugins:remove"
    classes = ("ajax-modal",)
    icon = "plus"
    # policy_rules = (("iot", "iot:create_board"),)


class DeletePluginsAction(tables.DeleteAction):
    @staticmethod
    def action_present(count):
        return ungettext_lazy(
            u"Delete Plugin",
            u"Delete Plugins",
            count
        )

    @staticmethod
    def action_past(count):
        return ungettext_lazy(
            u"Deleted Plugin",
            u"Deleted Plugins",
            count
        )
    # policy_rules = (("iot", "iot:delete_board"),)

    """
    def allowed(self, request, role):
        return api.keystone.keystone_can_edit_role()
    """

    def delete(self, request, plugin_id):
        api.iotronic.plugin_delete(request, plugin_id)


class PluginFilterAction(tables.FilterAction):

    def filter(self, table, plugins, filter_string):
        """Naive case-insensitive search."""
        q = filter_string.lower()
        return [plugin for plugin in plugins
                if q in plugin.name.lower()]


class PluginsTable(tables.DataTable):
    name = tables.WrappingColumn('name', link="horizon:project:plugins:detail",
                                 verbose_name=_('Plugin Name'))
    uuid = tables.Column('uuid', verbose_name=_('Plugin ID'))
    owner = tables.Column('owner', verbose_name=_('Owner'))
    public = tables.Column('public', verbose_name=_('Public'))
    callable = tables.Column('callable', verbose_name=_('Callable'))

    # Overriding get_object_id method because in IoT service the "id" is
    # identified by the field UUID
    def get_object_id(self, datum):
        # LOG.debug("MELO datum %s", datum)
        return datum.uuid

    # Overriding get_row_actions method because we need to discriminate
    # between Sync and Async plugins
    def get_row_actions(self, datum):
        actions = super(PluginsTable, self).get_row_actions(datum)

        selected_row_actions = []
        if not policy.check((("iot", "iot_user"),), self.request):

            common_actions = ["edit", "inject", "remove"]
            sync_actions = ["call"]
            async_actions = ["start", "stop"]

            for action in actions:
                if action.name in common_actions:
                    selected_row_actions.append(action)

                elif datum.callable == True and action.name in sync_actions:
                    selected_row_actions.append(action)

                elif datum.callable == False and action.name in async_actions:
                    selected_row_actions.append(action)

                elif datum.public == False and action.name == "delete":
                    selected_row_actions.append(action)

        return selected_row_actions

    # Overriding get_table_actions method because we need to discriminate
    # between user_iot and other users
    def get_table_actions(self):
        actions = super(PluginsTable, self).get_table_actions()

        selected_table_actions = []
        if not policy.check((("iot", "iot_user"),), self.request):
            selected_table_actions = actions

        return selected_table_actions

    class Meta(object):
        name = "plugins"
        verbose_name = _("plugins")

        row_actions = (EditPluginLink, InjectPluginLink, StartPluginLink,
                       StopPluginLink, CallPluginLink, RemovePluginLink,
                       DeletePluginsAction,)
        table_actions = (PluginFilterAction, CreatePluginLink,
                         DeletePluginsAction)
