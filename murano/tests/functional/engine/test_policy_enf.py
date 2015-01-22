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

import common
import testtools
import time
import uuid

import keystoneclient.openstack.common.apiclient.exceptions \
    as keystone_exceptions
import muranoclient.common.exceptions as murano_exceptions


CONGRESS_RULES = ['invalid_flavor_name("really.bad.flavor")',
                  'predeploy_error(eid, obj_id, msg):-'
                  'murano:objects(obj_id, eid, type),'
                  'murano:properties(obj_id, "flavor", flavor_name),'
                  'invalid_flavor_name(flavor_name),'
                  'murano:properties(obj_id, "name", obj_name),'
                  'concat(obj_name, ": bad flavor", msg)',
                  'predeploy_error(eid, obj_id, msg):-'
                  'murano:objects(obj_id, eid, type),'
                  'murano:properties(obj_id, "keyname", key_name),'
                  'missing_key(key_name),'
                  'murano:properties(obj_id, "name", obj_name),'
                  'concat(obj_name, ": missing key", msg)',
                  'missing_key("")']


class PolicyEnforcement(testtools.TestCase, common.DeployTestMixin):

    @classmethod
    def create_policy_req(cls, policy_name):
        return {'abbreviation': None, 'kind': None,
                'name': policy_name,
                'description': None}

    @classmethod
    def setUpClass(cls):
        super(PolicyEnforcement, cls).setUpClass()

        with common.ignored(Exception):
            cls.congress_client().create_policy(
                cls.create_policy_req('murano_system'))
        with common.ignored(Exception):
            cls.congress_client().create_policy(
                cls.create_policy_req('murano'))

        with common.ignored(murano_exceptions.HTTPInternalServerError):
            cls.upload_telnet()

    @classmethod
    def tearDownClass(cls):
        cls.purge_uploaded_packages()

    def setUp(self):
        super(PolicyEnforcement, self).setUp()
        self.rules = []

        rule_posts = [{"rule": rule} for rule in CONGRESS_RULES]
        for rule_post in rule_posts:
            with common.ignored(keystone_exceptions.Conflict):
                self.rules.append(self.congress_client().create_policy_rule(
                    'murano_system',
                    rule_post))

    def tearDown(self):
        super(PolicyEnforcement, self).tearDown()
        self.purge_environments()

        for rule in self.rules:
            self.congress_client().delete_policy_rule(
                "murano_system", rule["id"])

    def _wait_for_final_status(self, environment):
        start_time = time.time()
        status = environment.manager.get(environment.id).status
        while u'deploying' == status:
            if time.time() - start_time > 300:
                self.fail('Deployment not finished in 300 seconds')
            time.sleep(5)
            status = environment.manager.get(environment.id).status
        dep = environment.manager.api.deployments.list(environment.id)
        reports = environment.manager.api.deployments.reports(environment.id,
                                                              dep[0].id)

        return status, ", ".join([r.text for r in reports])

    def _create_env_body(self, flavor, key):
        return {
            "instance": {
                "flavor": flavor,
                "keyname": key,
                "image": common.CONF.murano.linux_image,
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

    def _check_deploy_failure(self, post_body, expected_text):
        environment_name = 'Telnetenv' + uuid.uuid4().hex[:5]
        env = self.deploy_apps(environment_name, post_body)
        status = self._wait_for_final_status(env)
        self.assertIn("failure", status[0], "Unexpected status : " + status[0])
        self.assertIn(expected_text, status[1].lower(),
                      "Unexpected status : " + status[1])

    def test_deploy_policy_fail_flavor(self):
        """test expects failure due to blacklisted flavor"""

        self._check_deploy_failure(
            self._create_env_body(flavor="really.bad.flavor",
                                  key="test-key"),
            "bad flavor")

    def test_deploy_policy_fail_key(self):
        """test expects failure due to empty key name"""

        self._check_deploy_failure(
            self._create_env_body(key="",
                                  flavor="m1.small"),
            "missing key")
