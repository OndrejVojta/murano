# Copyright (c) 2015 OpenStack Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import congressclient.v1.client as cclient
import contextlib
import keystoneclient
import keystoneclient.openstack.common.apiclient.exceptions \
    as keystone_exceptions
import testtools
import time
import uuid

from keystoneclient.v2_0 import client as ksclient
from muranoclient import client as mclient

import murano.tests.functional.engine.config as cfg

#TODO(ovo) create policy 'murano' and 'murano_system'

CONGRESS_RULES = ['invalid_flavor_name("really.bad.flavor")',
                  'predeploy_error(obj_id) :- '
                  'murano_property(obj_id, "flavor", prop_value), '
                  'invalid_flavor_name(prop_value)',
                  'predeploy_error(obj_id) :- '
                  'murano_property(obj_id, "keyname", prop_value), '
                  'missing_key(prop_value)',
                  'missing_key("")']


@contextlib.contextmanager
def ignored(*exceptions):
    try:
        yield
    except exceptions:
        pass

CONF = cfg.cfg.CONF


class PolicyEnforcement(testtools.TestCase):

    @classmethod
    def setUpClass(cls):
        super(PolicyEnforcement, cls).setUpClass()

        cfg.load_config()

        keystone_client = ksclient.Client(username=CONF.murano.user,
                                          password=CONF.murano.password,
                                          tenant_name=CONF.murano.tenant,
                                          auth_url=CONF.murano.auth_url)

        auth = keystoneclient.auth.identity.v2.Password(
            auth_url=CONF.murano.auth_url,
            username=CONF.murano.user,
            password=CONF.murano.password,
            tenant_name=CONF.murano.tenant)
        session = keystoneclient.session.Session(auth=auth)
        cls.congress_client = cclient.Client(session=session,
                                             service_type='policy')

        cls.muranoclient = mclient.Client('1',
                                          endpoint=CONF.murano.murano_url,
                                          token=keystone_client.auth_token)

    def setUp(self):
        super(PolicyEnforcement, self).setUp()
        self.rules = []
        self.environments = []

        rule_posts = [{"rule": rule} for rule in CONGRESS_RULES]
        for rule_post in rule_posts:
            with ignored(keystone_exceptions.Conflict):
                self.rules.append(self.congress_client.create_policy_rule(
                    'murano_system',
                    rule_post))

    def tearDown(self):
        super(PolicyEnforcement, self).tearDown()

        for rule in self.rules:
            self.congress_client.delete_policy_rule(
                "murano_system", rule["id"])
        for env in self.environments:
            with ignored(Exception):
                self.muranoclient.environments.delete(env.id)

    def _wait_for_final_status(self, environment):
        start_time = time.time()
        status = environment.manager.get(environment.id).status
        while u'deploying' == status:
            if time.time() - start_time > 300:
                self.fail('Deployment not finished in 300 seconds')
            time.sleep(5)
            status = environment.manager.get(environment.id).status
        return status

    def _deploy_app(self, name, app):
        environment = self.muranoclient.environments.create({'name': name})
        self.environments.append(environment)

        session = self.muranoclient.sessions.configure(environment.id)

        self.muranoclient.services.post(environment.id,
                                        path='/',
                                        data=app,
                                        session_id=session.id)

        self.muranoclient.sessions.deploy(environment.id, session.id)
        return environment

    def _create_env_body(self, flavor="really.bad.flavor", key="test-key"):
        return {
            "instance": {
                "flavor": flavor,
                "keyname": key,
                "image": CONF.murano.linux_image,
                "assignFloatingIp": True,
                "?": {
                    "type": "io.murano.resources.LinuxMuranoInstance",
                    "id": str(uuid.uuid4())
                },
                "name": "testMurano"
            },
            "name": "teMurano",
            "?": {
                "type": "io.murano.apps.linux.Telnet",
                "id": str(uuid.uuid4())
            }
        }

    def _check_deploy_failure(self, post_body):
        environment_name = 'Telnetenv' + uuid.uuid4().hex[:5]
        env = self._deploy_app(environment_name, post_body)
        status = self._wait_for_final_status(env)
        self.assertIn("failure", status, "Unexpected status : " + status)

    def test_deploy_policy_fail_flavor(self):
        self._check_deploy_failure(self._create_env_body())

    def test_deploy_policy_fail_key(self):
        self._check_deploy_failure(self._create_env_body(key="",
                                                       flavor="m1.small"))
