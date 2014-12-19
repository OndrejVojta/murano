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
Converts Murano model to Congress rules
"""


class CongressRules(object):

    def convert(self, model):
        rules = []

        if model is None or not model['Objects']:
            return rules

        env_id = model['Objects']['?']['id']

        for app in model['Objects']['applications']:
            obj = self._create_object_rule(app, env_id)
            rules.append(obj)
            rules.extend(self._create_propety_rules(obj.obj_id, app))

            instance = app['instance']
            obj2 = self._create_object_rule(instance, env_id)
            rules.extend(self._create_propety_rules(obj2.obj_id, instance))
            rules.append(obj2)

        return rules

    @staticmethod
    def _create_object_rule(app, env_id):
        return MuranoObject(app['?']['id'], env_id, app['?']['type'])

    @staticmethod
    def _create_propety_rules(obj_id, obj):
        rules = []

        for key, value in obj.iteritems():
            if key != '?' and key != 'instance':
                rule = MuranoProperty(obj_id, key, value)
                rules.append(rule)

        return rules


class MuranoObject(object):
    def __init__(self, obj_id, env_id, type_name):
        self.obj_id = obj_id
        self.env_id = env_id
        self.type_name = type_name

    def __str__(self):
        return 'murano_object+("{0}", "{1}", "{2}")'\
            .format(self.obj_id, self.env_id, self.type_name)


class MuranoProperty(object):
    def __init__(self, obj_id, prop_name, prop_value):
        self.obj_id = obj_id
        self.prop_name = prop_name
        self.prop_value = prop_value

    def __str__(self):
        return 'murano_property+("{0}", "{1}", "{2}")' \
            .format(self.obj_id, self.prop_name, self.prop_value)