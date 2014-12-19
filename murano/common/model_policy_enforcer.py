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

from murano.openstack.common import log as logging

LOG = logging.getLogger(__name__)

class ValidationError(Exception):
    """Raised for validation errors."""

class ModelPolicyEnforcer(object):

    def __init__(self, environment):
        self._environment = environment
        self._client_manager = environment.clients

    def validate(self, model):
        """Validate model using Congress rule engine"""

        LOG.info('Validating model')

        client = self._client_manager.get_congress_client(self._environment)
        validation_result = client.execute_policy_action("classification", "simulate",
                                              {'query': 'is_valid_model(x)', 'action_policy': 'action',
                                               'sequence': 'create_env+("todo")'})
        if validation_result["result"]:
            raise ValidationError("Model validation failed!")
        pass
