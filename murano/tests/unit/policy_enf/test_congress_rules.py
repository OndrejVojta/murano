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
import mock
import os.path
import unittest2 as unittest
import yaml

import murano.policy_enf.congress_rules as congress


class TestCongressRules(unittest.TestCase):

    def _load_file(self, file_name):
        model_file = os.path.join(
            os.path.dirname(inspect.getfile(self.__class__)), file_name)

        with open(model_file) as stream:
            return yaml.load(stream)

    def _create_rules_str(self, model_file):
        model = self._load_file(model_file)

        congress_rules = congress.CongressRules()
        rules = congress_rules.convert(model)
        rules_str = ", \n".join(map(str, rules))
        print rules_str

        return rules_str

    def test_convert_simple_app(self):
        rules_str = self._create_rules_str('model.yaml')

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
        rules_str = self._create_rules_str('model_two_instances.yaml')

        self.assertFalse("\"instances\"" in rules_str)

        self.assertTrue(
            'murano_property+("824b1718-09d8-4dd3-be32-9886f0d146d7",'
            ' "flavor", "m1.medium")' in rules_str)

        self.assertTrue(
            'murano_property+("afa3266c-e2a7-4822-a176-11a48cdd7949",'
            ' "flavor", "m1.medium")' in rules_str)

    def test_convert_model_with_relations(self):
        rules_str = self._create_rules_str('model_with_relations.yaml')

        self.assertFalse(
            'murano_property+("50fa68ff-cd9a-4845-b573-2c80879d158d", '
            '"server", "8ce94f23-f16a-40a1-9d9d-a877266c315d")' in rules_str)

        self.assertTrue(
            'murano_relationship+("50fa68ff-cd9a-4845-b573-2c80879d158d", '
            '"8ce94f23-f16a-40a1-9d9d-a877266c315d", "server")' in rules_str)

    def test_convert_model_nested(self):
        rules_str = self._create_rules_str('model_complex.yaml')

        self.assertTrue(
            'murano_property+("ade378ce-00d4-4a33-99eb-7b4b6ea3ab97",'
            ' "networks.customProp1.prop", "val")' in rules_str)

    def test_convert_model_list_value(self):
        rules_str = self._create_rules_str('model_complex.yaml')

        self.assertTrue(
            'murano_property+("ade378ce-00d4-4a33-99eb-7b4b6ea3ab97",'
            ' "ipAddresses", "10.0.1.13")' in rules_str)

        self.assertTrue(
            'murano_property+("ade378ce-00d4-4a33-99eb-7b4b6ea3ab97",'
            ' "ipAddresses", "16.60.90.90")' in rules_str)

        self.assertTrue(
            'murano_property+("ade378ce-00d4-4a33-99eb-7b4b6ea3ab97",'
            ' "networks.customNetworks", "10.0.1.0")' in rules_str)

        self.assertTrue(
            'murano_property+("ade378ce-00d4-4a33-99eb-7b4b6ea3ab97",'
            ' "networks.customNetworks", "10.0.2.0")' in rules_str)

    def test_convert_model_none_value(self):
        rules_str = self._create_rules_str('model_complex.yaml')

        self.assertTrue(
            'murano_property+("be3c5155-6670-4cf6-9a28-a4574ff70b71",'
            ' "floatingIpAddress", "")' in rules_str)

    def test_parent_types(self):

        #     grand-parent
        #       /     \
        #  parent1   parent2
        #       \     /
        # io.murano.apps.linux.Git

        def my_side_effect(*args):
            if args[0] == 'io.murano.apps.linux.Git':
                return cls
            elif args[0] == 'parent1':
                return parent1
            elif args[0] == 'parent2':
                return parent2

        class_loader = mock.Mock()
        cls = mock.Mock()
        grand = mock.Mock()
        grand.name = 'grand-parent'
        parent1 = mock.Mock()
        parent1.name = 'parent1'
        parent1.parents = [grand]
        parent2 = mock.Mock()
        parent2.name = 'parent2'
        parent2.parents = [grand]
        cls.parents = [parent1, parent2]
        class_loader.get_class = mock.Mock(side_effect=my_side_effect)

        model = self._load_file('model.yaml')

        congress_rules = congress.CongressRules()
        rules = congress_rules.convert(model, class_loader)
        rules_str = ", \n".join(map(str, rules))
        print rules_str

        self.assertTrue(
            'murano_parent-type+("0c810278-7282-4e4a-9d69-7b4c36b6ce6f",'
            ' "parent1")' in rules_str)

        self.assertTrue(
            'murano_parent-type+("0c810278-7282-4e4a-9d69-7b4c36b6ce6f",'
            ' "parent2")' in rules_str)

        self.assertTrue(
            'murano_parent-type+("0c810278-7282-4e4a-9d69-7b4c36b6ce6f",'
            ' "grand-parent")' in rules_str)