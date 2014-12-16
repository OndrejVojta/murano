from mock import Mock
from murano.common.engine import TaskExecutor
from murano.common import engine
from murano.common import config
from murano.tests.unit import base
from murano.common.model_policy_enforcer import ValidationException


class TestModelPolicyEnforcer(base.MuranoTestCase):

    model = {'Objects': None}

    task = {
        'action': 'action',
        'model': model,
        'token': 'token',
        'tenant_id': 'environment.tenant_id',
        'id': 'environment.id'
    }

    def test_enforcer_disabled(self):

        executor = TaskExecutor(self.task)
        executor._execute = Mock()  # replace call to inner method to do nothing
        executor._model_policy_enforcer = Mock()
        executor.execute()

        assert not executor._model_policy_enforcer.validate.called

    def test_enforcer_enabled(self):

        executor = TaskExecutor(self.task)
        executor._execute = Mock()  # replace call to inner method to do nothing
        executor._model_policy_enforcer = Mock()

        config.CONF.engine.enable_model_policy_enforcer = True
        executor.execute()

        executor._model_policy_enforcer.validate.assert_called_once_with(self.model)

    def test_validation_failed(self):

        ex = ValidationException('err')

        executor = TaskExecutor(self.task)
        executor._execute = Mock()  # replace call to inner method to do nothing
        executor._model_policy_enforcer.validate = Mock(side_effect=ex)

        engine.LOG = Mock()

        config.CONF.engine.enable_model_policy_enforcer = True
        executor.execute()

        engine.LOG.exception.assert_called_once_with(ex)
        #self.assertRaises(ValidationException, executor.execute)