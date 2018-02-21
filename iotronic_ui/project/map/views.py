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

import json
import logging

from horizon import exceptions
from horizon import views

from openstack_dashboard.api import iotronic
from openstack_dashboard import policy

LOG = logging.getLogger(__name__)


class IndexView(views.APIView):
    # A very simple class-based view...
    template_name = 'project/map/index.html'

    def get_data(self, request, context, *args, **kwargs):
        boards = []
        result = {'list': []}

        # Admin_iot_project
        if policy.check((("iot", "iot:list_project_boards"),), self.request):
            try:
                boards = iotronic.board_list(self.request, None, None)
                # LOG.debug('MAP data INFO: %s', boards)

                for i in range(len(boards)):
                    result["list"].append(boards[i]._info)

            except Exception:
                exceptions.handle(self.request,
                                  _('Unable to retrieve project boards list.'))

        # LOG.debug('MAP board list: %s', json.dumps(result))
        context["boards"] = json.dumps(result)
        return context
