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

import inspect
import json
import os.path
import unittest2 as unittest

import murano.policy_enf.congress_rules as congress


class TestModelPolicyEnforcer(unittest.TestCase):

    def _load_file(self, file_name):
        model_file = os.path.join(
            os.path.dirname(inspect.getfile(self.__class__)), file_name)
        return json.load(open(model_file))

    def test_convert_simple_app(self):

        model = self._load_file('model.json')

        congress_rules = congress.CongressRules()
        rules = congress_rules.convert(model)
        rules_str = ", \n".join(map(str, rules))
        print rules_str

        self.assertFalse("\"instance\"" in rules_str)

        self.assertTrue(
            'murano_object+("0c810278-7282-4e4a-9d69-7b4c36b6ce6f",'
            ' "c86104748a0c4907b4c5981e6d3bce9f", '
            '"io.murano.apps.linux.Git")' in rules_str)

        self.assertTrue(
            'murano_property+("0c810278-7282-4e4a-9d69'
            '-7b4c36b6ce6f", "name", "git1")' in rules_str)

        self.assertTrue(
            'murano_object+("b840b71e-1805-46c5-9e6f-5a3d2c8d773e",'
            ' "c86104748a0c4907b4c5981e6d3bce9f", '
            '"io.murano.resources.LinuxMuranoInstance")'
            in rules_str)

        self.assertTrue('murano_property+("b840b71e-1805-46c5-9e6f'
                        '-5a3d2c8d773e", "name", '
                        '"whjiyi3uzhxes6")' in rules_str)

    def test_convert_model_two_instances(self):

        model = self._load_file('model_two_instances.json')

        congress_rules = congress.CongressRules()
        rules = congress_rules.convert(model)
        rules_str = ", \n".join(map(str, rules))
        print rules_str

        self.assertFalse("\"instances\"" in rules_str)

        self.assertTrue(
            'murano_property+("824b1718-09d8-4dd3-be32-9886f0d146d7",'
            ' "flavor", "m1.medium")' in rules_str)

        self.assertTrue(
            'murano_property+("afa3266c-e2a7-4822-a176-11a48cdd7949",'
            ' "flavor", "m1.medium")' in rules_str)

    def test_convert_model_with_relations(self):

        model = self._load_file('model_with_relations.json')

        congress_rules = congress.CongressRules()
        rules = congress_rules.convert(model)
        rules_str = ", \n".join(map(str, rules))
        print rules_str