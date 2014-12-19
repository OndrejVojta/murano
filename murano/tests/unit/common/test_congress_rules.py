import mock
import unittest2 as unittest

import json

import murano.common.congress_rules as congress


class TestModelPolicyEnforcer(unittest.TestCase):

    def test_convert_simple_app(self):

        model = json.load(open('model.json'))

        congress_rules = congress.CongressRules()
        rules = congress_rules.convert(model)
        rules_str = ", \n".join(map(str, rules))
        print rules_str

        self.assertTrue('murano_object("0c810278-7282-4e4a-9d69-7b4c36b6ce6f",'
                        ' "c86104748a0c4907b4c5981e6d3bce9f", '
                        '"io.murano.apps.linux.Git")' in rules_str)

        self.assertTrue('murano_property("0c810278-7282-4e4a-9d69'
                        '-7b4c36b6ce6f", "name", "git1")' in rules_str)

        self.assertTrue('murano_object("b840b71e-1805-46c5-9e6f-5a3d2c8d773e",'
                        ' "c86104748a0c4907b4c5981e6d3bce9f", '
                        '"io.murano.resources.LinuxMuranoInstance")'
                        in rules_str)

        self.assertTrue('murano_property("b840b71e-1805-46c5-9e6f'
                        '-5a3d2c8d773e", "name", '
                        '"whjiyi3uzhxes6")' in rules_str)


        pass