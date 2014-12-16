# Copyright (c) 2014 OpenStack Foundation.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
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
Policy Enforcer Implementation using Congress client
"""

from congressclient.v1 import client


class ModelPolicyEnforcer:

    def __init__(self):
        pass

    def validate(self, model):
        """Process model validation using Congress client"""

        # auth = keystoneclient.auth.identity.v2.Password(
        #     auth_url=AUTH_URL, username=USERNAME,
        #     password=PASSWORD, tenant_name=TENANT_NAME)
        # session = keystoneclient.session.Session(auth=auth)
        # congress = client.Client(session=session,
        #                          auth=None,
        #                          interface='publicURL',
        #                          service_type='policy',
        #                          region_name='RegionOne')

        congress = client.Client()

        body = congress.execute_policy_action('policy_name', 'action')

        if True:  # depending on congress result
            raise ValidationException('model not valid...')


class ValidationException(Exception):
    pass