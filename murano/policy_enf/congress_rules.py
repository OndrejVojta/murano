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
Converts murano model to list of congress rules:
    murano_object+(env_id, obj_id, type_name)
    murano_property+(obj_id, prop_name, prop_value)
"""


class CongressRules(object):

    def convert(self, model, class_loader=None):
        rules = []

        if model is None:
            return rules

        env_id = model['?']['id']

        app_ids = []
        for app in model['applications']:
            app = self._to_dict(app)

            obj = self._create_object_rule(app, env_id)
            app_ids.append(obj.obj_id)
            rules.append(obj)
            rules.extend(self._create_propety_rules(obj.obj_id, app))

            types = self._get_parent_types(app['?']['type'], class_loader)
            rules.extend(self._create_parent_type_rules(app['?']['id'],
                                                        types))

            instances = []
            if 'instance' in app:
                instances.append(app['instance'])

            if 'instances' in app:
                instances.extend(app['instances'])

            for instance in instances:
                instance = self._to_dict(instance)

                obj2 = self._create_object_rule(instance, env_id)
                rules.extend(self._create_propety_rules(obj2.obj_id,
                                                        instance))
                rules.append(obj2)

        # convert MuranoProperty containing reference to another object
        # to MuranoRelationship
        rules = [self._create_relationship(rule, app_ids) for rule in rules]

        return rules

    @staticmethod
    def _to_dict(obj):
        # if we have MuranoObject class we need to convert to dictionary
        if 'to_dictionary' in dir(obj):
            return obj.to_dictionary()
        else:
            return obj

    @staticmethod
    def _create_object_rule(app, env_id):
        return MuranoObject(app['?']['id'], env_id, app['?']['type'])

    @staticmethod
    def _create_propety_rules(obj_id, obj):
        rules = []
        excluded_keys = ['?', 'instance', 'instances']

        for key, value in obj.iteritems():
            if not key in excluded_keys:

                if value is None:
                    value = ""

                #TODO(ondrej.vojta) expand composite properties
                if not isinstance(value, list) and not isinstance(value, dict):
                    rule = MuranoProperty(obj_id, key, value)
                    rules.append(rule)

        return rules

    @staticmethod
    def _is_relationship(rule, app_ids):
        if not isinstance(rule, MuranoProperty):
            return False

        return rule.prop_value in app_ids

    def _create_relationship(self, rule, app_ids):
        if self._is_relationship(rule, app_ids):
            return MuranoRelationship(rule.obj_id, rule.prop_value,
                                      rule.prop_name)
        else:
            return rule

    def _get_parent_types(self, type_name, class_loader):
        types = set()
        if class_loader is not None:
            cls = class_loader.get_class(type_name)
            if cls is not None:
                for parent in cls.parents:
                    types.add(parent.name)
                    types = types.union(
                        self._get_parent_types(parent.name, class_loader))
        return types

    @staticmethod
    def _create_parent_type_rules(app_id, types):
        rules = []
        for type_name in types:
            rules.append(MuranoParentType(app_id, type_name))
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


class MuranoRelationship(object):
    def __init__(self, source_id, target_id, rel_name):
        self.source_id = source_id
        self.target_id = target_id
        self.rel_name = rel_name

    def __str__(self):
        return 'murano_relationship+("{0}", "{1}", "{2}")' \
            .format(self.source_id, self.target_id, self.rel_name)


class MuranoParentType(object):
    def __init__(self, obj_id, type_name):
        self.obj_id = obj_id
        self.type_name = type_name

    def __str__(self):
        return 'murano_parent-type+("{0}", "{1}")' \
            .format(self.obj_id, self.type_name)