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

from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from horizon import forms
from horizon import messages

from openstack_dashboard.api import iotronic
from openstack_dashboard import policy

LOG = logging.getLogger(__name__)


class UpdateBoardForm(forms.SelfHandlingForm):
    uuid = forms.CharField(label=_("Board ID"), widget=forms.HiddenInput)
    name = forms.CharField(label=_("Board Name"))
    mobile = forms.BooleanField(label=_("Mobile"), required=False)

    latitude = forms.FloatField(label=_("Latitude"))
    longitude = forms.FloatField(label=_("Longitude"))
    altitude = forms.FloatField(label=_("Altitude"))

    def __init__(self, *args, **kwargs):

        super(UpdateBoardForm, self).__init__(*args, **kwargs)

        # LOG.debug("MELO INITIAL: %s", kwargs["initial"])

        LOG.debug("MELO Manager: %s", policy.check((("iot", "iot_manager"),),
                                                   self.request))
        LOG.debug("MELO Admin: %s", policy.check((("iot", "iot_admin"),),
                                                 self.request))

        # Admin
        if policy.check((("iot", "iot:update_boards"),), self.request):
            # LOG.debug("MELO ADMIN")
            pass

        # Manager or Admin of the iot project
        elif (policy.check((("iot", "iot_manager"),), self.request) or
              policy.check((("iot", "iot_admin"),), self.request)):
            # LOG.debug("MELO NO-edit IOT ADMIN")
            pass

        # Other users
        else:
            if self.request.user.id != kwargs["initial"]["owner"]:
                # LOG.debug("MELO IMMUTABLE FIELDS")
                self.fields["name"].widget.attrs = {'readonly': 'readonly'}
                self.fields["mobile"].widget.attrs = {'disabled': 'disabled'}

                self.fields["latitude"].widget.attrs = {'readonly': 'readonly'}
                self.fields["longitude"].widget.attrs = {'readonly':
                                                         'readonly'}
                self.fields["altitude"].widget.attrs = {'readonly': 'readonly'}

    def handle(self, request, data):
        try:

            data["location"] = [{"latitude": str(data["latitude"]),
                                 "longitude": str(data["longitude"]),
                                 "altitude": str(data["altitude"])}]
            iotronic.board_update(request, data["uuid"],
                                  {"name": data["name"],
                                   "mobile": data["mobile"],
                                   "location": data["location"]})

            messages.success(request, _("Board updated successfully."))
            return True
        except Exception:
            exceptions.handle(request, _('Unable to update board.'))


class RemovePluginsForm(forms.SelfHandlingForm):

    uuid = forms.CharField(label=_("Board ID"), widget=forms.HiddenInput)

    name = forms.CharField(
        label=_('Board Name'),
        widget=forms.TextInput(attrs={'readonly': 'readonly'})
    )

    plugin_list = forms.MultipleChoiceField(
        label=_("Plugins List"),
        widget=forms.SelectMultiple(
            attrs={'class': 'switchable', 'data-slug': 'slug-remove-plugins'}),
        help_text=_("Select plugins in this pool ")
    )

    def __init__(self, *args, **kwargs):

        super(RemovePluginsForm, self).__init__(*args, **kwargs)
        # input=kwargs.get('initial',{})

        plugin_list = []
        for plugin in json.loads(kwargs["initial"]["plugin_list"]):
            plugin_list.append((plugin["plugin"], _(plugin["name"])))

        self.fields["plugin_list"].choices = plugin_list
        self.fields["plugin_list"].max_length = len(plugin_list)

    def handle(self, request, data):

        counter = 0

        for plugin in data["plugin_list"]:
            for key, value in self.fields["plugin_list"].choices:
                if key == plugin:

                    try:
                        board = None

                        # LOG.debug('INJECT: %s %s', plugin, value)
                        # board = iotronic.plugin_create(request, data["name"],
                        #                                data["public"],
                        #                                data["callable"],
                        #                                data["code"])
                        message_text = "Plugin " + str(value) \
                                       + " removed successfully."
                        messages.success(request, _(message_text))

                        if counter != len(data["plugin_list"]) - 1:
                            counter += 1
                        else:
                            return board
                    except Exception:
                        message_text = "Unable to remove plugin " \
                                       + str(value) + "."
                        exceptions.handle(request, _(message_text))

                    break