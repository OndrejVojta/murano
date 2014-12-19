# Copyright (c) 2014 OpenStack Foundation.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
import congressclient

import mock

import murano.common.config as config
import murano.common.engine as engine
import murano.common.model_policy_enforcer as model_policy_enforcer
from murano.engine import client_manager
from murano.tests.unit import base


class TestModelPolicyEnforcer(base.MuranoTestCase):
    model = {'Objects': None}

    task = {
        'action': 'action',
        'model': model,
        'token': 'token',
        'tenant_id': 'environment.tenant_id',
        'id': 'environment.id'
    }

    def setUp(self):
        super(TestModelPolicyEnforcer, self).setUp()
        self.congress_client_mock = \
            mock.Mock(spec=congressclient.v1.client.Client)

        self.client_manager_mock = mock.Mock(spec=client_manager.ClientManager)

        self.client_manager_mock.get_congress_client.return_value = \
            self.congress_client_mock

        self.environment = mock.Mock()
        self.environment.clients = self.client_manager_mock

    def test_enforcer_disabled(self):
        executor = engine.TaskExecutor(self.task)

        # replace call to inner method to do nothing
        executor._execute = mock.Mock()
        executor._model_policy_enforcer = mock.Mock()

        executor.execute()

        self.assertFalse(executor._model_policy_enforcer.validate.called)

    def test_enforcer_enabled(self):
        executor = engine.TaskExecutor(self.task)

        # replace call to inner method to do nothing
        executor._execute = mock.Mock()
        executor._model_policy_enforcer = mock.Mock()

        config.CONF.engine.enable_model_policy_enforcer = True
        executor.execute()

        executor._model_policy_enforcer \
            .validate.assert_called_once_with(self.model)

    def test_validation_pass(self):
        self.congress_client_mock.execute_policy_action.return_value = \
            {"result": []}

        enforcer = model_policy_enforcer.ModelPolicyEnforcer(self.environment)
        enforcer.validate(None)

    def test_validation_failure(self):
        self.congress_client_mock.execute_policy_action.return_value = \
            {"result": ["failure"]}

        enforcer = model_policy_enforcer.ModelPolicyEnforcer(self.environment)
        self.assertRaises(model_policy_enforcer.ValidationError,
                          enforcer.validate, None)
