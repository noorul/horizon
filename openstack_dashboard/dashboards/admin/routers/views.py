# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012,  Nachi Ueno,  NTT MCL,  Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
Views for managing Neutron Routers.
"""

import logging

from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import exceptions
from openstack_dashboard import api
from openstack_dashboard.dashboards.admin.networks import views as n_views
from openstack_dashboard.dashboards.project.routers import views as r_views

from openstack_dashboard.dashboards.admin.routers.ports.tables \
    import PortsTable
from openstack_dashboard.dashboards.admin.routers.tables import RoutersTable


LOG = logging.getLogger(__name__)


class IndexView(r_views.IndexView, n_views.IndexView):
    table_class = RoutersTable
    template_name = 'admin/routers/index.html'

    def _get_routers(self, search_opts=None):
        try:
            routers = api.neutron.router_list(self.request,
                                              search_opts=search_opts)
        except:
            routers = []
            exceptions.handle(self.request,
                              _('Unable to retrieve router list.'))
        if routers:
            tenant_dict = self._get_tenant_list()
            ext_net_dict = self._list_external_networks()
            for r in routers:
                 # Set tenant name
                tenant = tenant_dict.get(r.tenant_id, None)
                r.tenant_name = getattr(tenant, 'name', None)
                # If name is empty use UUID as name
                r.set_id_as_name_if_empty()
                # Set external network name
                self._set_external_network(r, ext_net_dict)
        return routers

    def get_data(self):
        routers = self._get_routers()
        return routers


class DetailView(r_views.DetailView):
    table_classes = (PortsTable, )
    template_name = 'admin/routers/detail.html'
    failure_url = reverse_lazy('horizon:admin:routers:index')
