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

Converts murano model to list of congress rules:
    murano_object+(env_id, obj_id, type_name)
    murano_property+(obj_id, prop_name, prop_value)

Then we ask congress to resolve "is_valid_model(x)" table to return validation
results.

Example:
Using these commands we can create rules in congress to disable instances with
"m1.small" flavor:

>congress policy rule create classification "invalid_flavor_name(\"m1.small\")"
>congress policy rule create classification
    "is_valid_model(obj_id) :- murano_property(obj_id, \"flavor\", prop_value),
    invalid_flavor_name(prop_value)"

"""

import congress_rules

from murano.openstack.common import log as logging

LOG = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised for validation errors."""


class ModelPolicyEnforcer(object):

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

        client = self._client_manager.get_congress_client(self._environment)
        if not client:
            raise ValueError('Congress client is not configured!')

        LOG.info('Validating model')
        LOG.debug(model)

        rules = congress_rules.CongressRules().convert(model, class_loader)
        rules_str = " ".join(map(str, rules))
        LOG.debug('Congress rules: \n  ' + "\n  ".join(map(str, rules)) + '\n')

        validation_result = client.execute_policy_action(
            "classification",
            "simulate",
            {'query': 'is_valid_model(x)', 'action_policy': 'action',
            'sequence': rules_str})

        if validation_result["result"]:
            raise ValidationError("Model validation failed!")
        else:
            LOG.info('Model valid')
