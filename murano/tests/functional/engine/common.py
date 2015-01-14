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
import murano.tests.functional.engine.config as cfg
import os

from keystoneclient.v2_0 import client as ksclient
from muranoclient import client as mclient

CONF = cfg.cfg.CONF

cfg.load_config()


@contextlib.contextmanager
def ignored(*exceptions):
    try:
        yield
    except exceptions:
        pass


class Memoize:

    def __init__(self, f):
        self.f = f
        self.mem = {}

    def __call__(self, *args, **kwargs):
        if (args, str(kwargs)) in self.mem:
            return self.mem[args, str(kwargs)]
        else:
            tmp = self.f(*args, **kwargs)
            self.mem[args, str(kwargs)] = tmp
            return tmp


# TODO(FilipBlaha) refactor base.py to use this module
class DeployTestMixin(object):

    @staticmethod
    @Memoize
    def keystone_client():
        return ksclient.Client(username=CONF.murano.user,
                               password=CONF.murano.password,
                               tenant_name=CONF.murano.tenant,
                               auth_url=CONF.murano.auth_url)

    @staticmethod
    @Memoize
    def congress_client():
        auth = keystoneclient.auth.identity.v2.Password(
            auth_url=CONF.murano.auth_url,
            username=CONF.murano.user,
            password=CONF.murano.password,
            tenant_name=CONF.murano.tenant)
        session = keystoneclient.session.Session(auth=auth)
        return cclient.Client(session=session,
                              service_type='policy')

    @staticmethod
    @Memoize
    def murano_client():
        keystone_client = DeployTestMixin.keystone_client()
        return mclient.Client('1',
                              endpoint=CONF.murano.murano_url,
                              token=keystone_client.auth_token)

    @staticmethod
    @Memoize
    def packages_path():
        return os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            os.path.pardir,
            'murano-app-incubator'
        ))

    @staticmethod
    def upload_package(package_name, body, app):
        files = {'%s' % package_name: open(app, 'rb')}
        return DeployTestMixin.murano_client().packages.create(body, files)

    @staticmethod
    def upload_telnet():
        return DeployTestMixin.upload_package(
            'Telnet', {"categories": ["Web"], "tags": ["tag"]},
            os.path.join(DeployTestMixin.packages_path(),
                         'io.murano.apps.linux.Telnet.zip'))