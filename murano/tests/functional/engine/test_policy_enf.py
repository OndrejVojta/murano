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


INVALID_FLAVOR_RULE2 = {"rule": 'invalid_flavor_name("m1.small")'}

INVALID_FLAVOR_RULE1 = {"rule":
                        'is_valid_model(obj_id) :- '
                        'murano_property(obj_id, "flavor", prop_value), '
                        'invalid_flavor_name(prop_value)'}


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
        with ignored(keystone_exceptions.Conflict):
            self.rules.append(self.congress_client.create_policy_rule(
                'classification',
                INVALID_FLAVOR_RULE1))
            self.rules.append(self.congress_client.create_policy_rule(
                'classification',
                INVALID_FLAVOR_RULE2))

    def tearDown(self):
        super(PolicyEnforcement, self).tearDown()

        for rule in self.rules:
            self.congress_client.delete_policy_rule(
                "classification", rule["id"])

    def wait_for_failure(self, environment):
        start_time = time.time()
        while not 'failure' in environment.manager.get(environment.id).status:
            if time.time() - start_time > 300:
                self.fail('Deployment not finished in 300 seconds')
            time.sleep(5)

    def _quick_deploy(self, name, app):
        environment = self.muranoclient.environments.create({'name': name})

        session = self.muranoclient.sessions.configure(environment.id)

        self.muranoclient.services.post(environment.id,
                                        path='/',
                                        data=app,
                                        session_id=session.id)

        self.muranoclient.sessions.deploy(environment.id, session.id)
        return environment

    def test_deploy_telnet_policy_fail(self):
        post_body = {
            "instance": {
                "flavor": "m1.small",
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

        environment_name = 'Telnetenv' + uuid.uuid4().hex[:5]
        env = self._quick_deploy(environment_name, post_body)
        self.wait_for_failure(env)
