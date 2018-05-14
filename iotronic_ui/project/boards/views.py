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

from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
# from horizon import messages
from horizon import tables
from horizon import tabs
from horizon.utils import memoized

from openstack_dashboard.api import iotronic
from openstack_dashboard import policy

from openstack_dashboard.dashboards.project.boards \
    import forms as project_forms
from openstack_dashboard.dashboards.project.boards \
    import tables as project_tables
from openstack_dashboard.dashboards.project.boards \
    import tabs as project_tabs

LOG = logging.getLogger(__name__)


class IndexView(tables.DataTableView):
    table_class = project_tables.BoardsTable
    template_name = 'project/boards/index.html'
    page_title = _("Boards")

    def get_data(self):
        boards = []

        # Admin
        if policy.check((("iot", "iot:list_all_boards"),), self.request):
            try:
                boards = iotronic.board_list(self.request, None, None)

            except Exception:
                exceptions.handle(self.request,
                                  _('Unable to retrieve boards list.'))

        # Admin_iot_project
        elif policy.check((("iot", "iot:list_project_boards"),), self.request):
            try:
                boards = iotronic.board_list(self.request, None, None)

            except Exception:
                exceptions.handle(self.request,
                                  _('Unable to retrieve user boards list.'))

        # Other users
        else:
            try:
                boards = iotronic.board_list(self.request, None, None)

            except Exception:
                exceptions.handle(self.request,
                                  _('Unable to retrieve user boards list.'))

        for board in boards:
            board_services = iotronic.services_on_board(self.request, board.uuid, True)

            # board.__dict__.update(dict(services=board_services))
            board._info.update(dict(services=board_services))
        return boards


class CreateView(forms.ModalFormView):
    template_name = 'project/boards/create.html'
    modal_header = _("Create Board")
    form_id = "create_board_form"
    form_class = project_forms.CreateBoardForm
    submit_label = _("Create Board")
    submit_url = reverse_lazy("horizon:project:boards:create")
    success_url = reverse_lazy('horizon:project:boards:index')
    page_title = _("Create Board")


class UpdateView(forms.ModalFormView):
    template_name = 'project/boards/update.html'
    modal_header = _("Update Board")
    form_id = "update_board_form"
    form_class = project_forms.UpdateBoardForm
    submit_label = _("Update Board")
    submit_url = "horizon:project:boards:update"
    success_url = reverse_lazy('horizon:project:boards:index')
    page_title = _("Update Board")

    @memoized.memoized_method
    def get_object(self):
        try:
            return iotronic.board_get(self.request, self.kwargs['board_id'],
                                      None)
        except Exception:
            redirect = reverse("horizon:project:boards:index")
            exceptions.handle(self.request,
                              _('Unable to get board information.'),
                              redirect=redirect)

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        args = (self.get_object().uuid,)
        context['submit_url'] = reverse(self.submit_url, args=args)
        return context

    def get_initial(self):
        board = self.get_object()
        location = board.location[0]

        return {'uuid': board.uuid,
                'name': board.name,
                'mobile': board.mobile,
                'owner': board.owner,
                'latitude': location["latitude"],
                'longitude': location["longitude"],
                'altitude': location["altitude"]}


class RemovePluginsView(forms.ModalFormView):
    template_name = 'project/boards/removeplugins.html'
    modal_header = _("Remove Plugins from board")
    form_id = "remove_boardplugins_form"
    form_class = project_forms.RemovePluginsForm
    submit_label = _("Remove Plugins from board")
    # submit_url = reverse_lazy("horizon:project:boards:removeplugins")
    submit_url = "horizon:project:boards:removeplugins"
    success_url = reverse_lazy('horizon:project:boards:index')
    page_title = _("Remove Plugins from board")

    @memoized.memoized_method
    def get_object(self):
        try:
            return iotronic.board_get(self.request, self.kwargs['board_id'],
                                      None)
        except Exception:
            redirect = reverse("horizon:project:boards:index")
            exceptions.handle(self.request,
                              _('Unable to get board information.'),
                              redirect=redirect)

    def get_context_data(self, **kwargs):
        context = super(RemovePluginsView, self).get_context_data(**kwargs)
        args = (self.get_object().uuid,)
        context['submit_url'] = reverse(self.submit_url, args=args)
        return context

    def get_initial(self):
        board = self.get_object()

        # Populate plugins
        # TO BE DONE.....filter by available on this board!!!
        # plugins = iotronic.plugin_list(self.request, None, None)
        plugins = iotronic.plugins_on_board(self.request, board.uuid)

        plugins.sort(key=lambda b: b.name)

        plugin_list = []
        for plugin in plugins:
            plugin_list.append((plugin.uuid, _(plugin.name)))

        return {'uuid': board.uuid,
                'name': board.name,
                'plugin_list': plugin_list}


class DetailView(tabs.TabView):
    tab_group_class = project_tabs.BoardDetailTabs
    template_name = 'horizon/common/_detail.html'
    page_title = "{{ board.name|default:board.uuid }}"

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        board = self.get_data()
        context["board"] = board
        context["url"] = reverse(self.redirect_url)
        context["actions"] = self._get_actions(board)

        return context

    def _get_actions(self, board):
        table = project_tables.BoardsTable(self.request)
        return table.render_row_actions(board)

    @memoized.memoized_method
    def get_data(self):
        board_id = self.kwargs['board_id']
        try:

            board_services = []
            board_plugins = []

            board = iotronic.board_get(self.request, board_id, None)
            board_services = iotronic.services_on_board(self.request, board_id, True)
            board._info.update(dict(services=board_services))

            board_plugins = iotronic.plugins_on_board(self.request, board_id)
            board._info.update(dict(plugins=board_plugins))
            # LOG.debug("BOARD: %s\n\n%s", board, board._info)

        except Exception:
            msg = ('Unable to retrieve board %s information') % {'name':
                                                                 board.name}
            exceptions.handle(self.request, msg, ignore=True)
        return board

    def get_tabs(self, request, *args, **kwargs):
        board = self.get_data()
        return self.tab_group_class(request, board=board, **kwargs)


class BoardDetailView(DetailView):
    redirect_url = 'horizon:project:boards:index'

    def _get_actions(self, board):
        table = project_tables.BoardsTable(self.request)
        return table.render_row_actions(board)
