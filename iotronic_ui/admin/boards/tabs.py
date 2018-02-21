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

# from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

# from horizon import exceptions
from horizon import messages
from horizon import tabs

LOG = logging.getLogger(__name__)

"""
import inspect
LOG.debug('MELO CLASSES: %s',
          inspect.getmembers(tabs, predicate=inspect.isclass))
"""


class OverviewTab(tabs.Tab):
    name = _("Overview")
    slug = "overview"
    template_name = ("admin/boards/_detail_overview.html")

    def get_context_data(self, request):
        # FROM
        """
        return {"board": self.tab_group.kwargs['board'],
                "is_superuser": request.user.is_superuser}
        """
        # TO
        plugins = []
        try:
            plugins = self.tab_group.kwargs['board']._info['plugins']

        except Exception:
            msg = ('No plugins injected in the board')
            messages.warning(self.request, msg)

        location = self.tab_group.kwargs['board']._info['location'][0]

        return {"board": self.tab_group.kwargs['board'],
                "location": location,
                "plugins": plugins,
                "is_superuser": request.user.is_superuser}


class BoardDetailTabs(tabs.TabGroup):
    slug = "board_details"
    # tabs = (OverviewTab, LogTab, ConsoleTab, AuditTab)
    tabs = (OverviewTab,)
    sticky = True