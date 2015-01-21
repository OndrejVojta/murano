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

from murano.policy_enf import congress_rules
import re

from murano.openstack.common import log as logging

LOG = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised for validation errors."""


class ModelPolicyEnforcer(object):
    """Policy Enforcer Implementation using Congress client

    Converts murano model to list of congress data rules:
        murano:object+(env_id, obj_id, type_name)
        murano:property+(obj_id, prop_name, prop_value)

    Then we ask congress using simulation api of congress rest client
    to resolve "murano_system:predeploy_error(env_id, obj_id, msg)"
    table along with congress data rules to return validation results.
    """

    def __init__(self, environment):
        self._environment = environment
        self._client_manager = environment.clients

    def validate(self, model, action_name, class_loader=None):
        """Validate model using Congress rule engine.

        @type model: dict
        @param model: Dictionary representation of model starting on
                      environment level (['Objects'])
        @type action_name: string
        @param action_name: name of the action for which validation is called
        @type class_loader: murano.dsl.class_loader.MuranoClassLoader
        @param class_loader: Optional. Used for evaluating parent class types
        @raises ValidationError in case validation was not successful
        """

        if model is None:
            return

        if action_name != 'deploy':
            LOG.debug("Skipping validation for action '{0}'"
                      .format(action_name))
            return

        client = self._client_manager.get_congress_client(self._environment)
        if not client:
            raise ValueError('Congress client is not configured!')

        LOG.info('Validating model')
        LOG.debug(model)

        rules = congress_rules.CongressRules() \
            .convert(model, class_loader, self._environment.tenant_id)

        rules_str = " ".join(map(str, rules))
        LOG.debug('Congress rules: \n  ' + "\n  ".join(map(str, rules)) + '\n')

        validation_result = client.execute_policy_action(
            "murano_system",
            "simulate",
            False,
            False,
            {'query': 'predeploy_error(eid, oid, msg)',
             'action_policy': 'action',
            'sequence': rules_str})

        if validation_result["result"]:
            result_str = self._result_to_str(validation_result["result"])
            raise ValidationError("Model validation failed:" + result_str)
        else:
            LOG.info('Model valid')

    def _result_to_str(self, results):
        s = ''
        regexp = 'predeploy_error\("([^"]*)",\s*"([^"]*)",\s*"([^"]*)"\)'
        for result in results:
            s += '\n  '
            match = re.search(regexp, result)
            if match:
                s += match.group(3).format(match.group(1), match.group(2))
            else:
                s += result
        return s