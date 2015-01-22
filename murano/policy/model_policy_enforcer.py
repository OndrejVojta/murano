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

import re

from murano.policy import congress_rules

from murano.openstack.common.gettextutils import _
from murano.openstack.common import log as logging

LOG = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised for validation errors."""
    pass


class ModelPolicyEnforcer(object):
    """Policy Enforcer Implementation using Congress client

    Converts murano model to list of congress data rules.

    We ask congress using simulation api of congress rest client
    to resolve "murano_system:predeploy_error(env_id, obj_id, msg)"
    table along with congress data rules to return validation results.
    """

    def __init__(self, environment):
        self._environment = environment
        self._client_manager = environment.clients

    def validate(self, model, class_loader=None):
        """Validate model using Congress rule engine.

        @type model: dict
        @param model: Dictionary representation of model starting on
                      environment level (['Objects'])
        @type class_loader: murano.dsl.class_loader.MuranoClassLoader
        @param class_loader: Optional. Used for evaluating parent class types
        @raises ValidationError in case validation was not successful
        """

        if model is None:
            return

        client = self._client_manager.get_congress_client(self._environment)
        if not client:
            raise ValueError(_('Congress client is not configured!'))

        LOG.info(_('Validating model'))
        LOG.debug(model)

        rules = congress_rules.CongressRulesManager() \
            .convert(model, class_loader,
                     self._environment.tenant_id)

        rules_str = " ".join(map(str, rules))
        LOG.debug(_('Congress rules: \n  ') +
                  '\n  '.join(map(str, rules)))

        validation_result = client.execute_policy_action(
            "murano_system",
            "simulate",
            False,
            False,
            {'query': 'predeploy_error(eid, oid, msg)',
             'action_policy': 'action',
            'sequence': rules_str})

        if validation_result["result"]:
            messages = self._parse_messages(validation_result["result"])
            result_str = "\n  ".join(map(str, messages))
            raise ValidationError(_("Model validation failed:") +
                                  "\n  " + result_str)
        else:
            LOG.info(_('Model valid'))

    def _parse_messages(self, results):
        """Transforms list of strings in format
            ['predeploy_error("env_id_1", "obj_id_1", "message1")',
            'predeploy_error("env_id_2", "obj_id_2", "message2")']
        to list of strings with message only
            ['message1', 'message2']
        """

        messages = []
        regexp = 'predeploy_error\("([^"]*)",\s*"([^"]*)",\s*"([^"]*)"\)'
        for result in results:
            match = re.search(regexp, result)
            if match:
                messages.append(match.group(3))
            else:
                # If we didn't find 'predeploy_error' add whole string.
                # It may be some problem in congress.
                messages.append(result)

        return messages