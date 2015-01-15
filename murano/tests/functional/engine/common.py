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
import muranoclient.common.exceptions as exceptions
import os
import time

from heatclient import client as heatclient
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


def memoize(f):
    cache = {}

    def decorated_function(*args):
        if args in cache:
            return cache[args]
        else:
            cache[args] = f(*args)
            return cache[args]
    return decorated_function


class DeployTestMixin(object):

    @staticmethod
    @memoize
    def keystone_client():
        return ksclient.Client(username=CONF.murano.user,
                               password=CONF.murano.password,
                               tenant_name=CONF.murano.tenant,
                               auth_url=CONF.murano.auth_url)

    @classmethod
    @memoize
    def heat_client(cls):
        heat_url = cls.keystone_client().service_catalog.url_for(
            service_type='orchestration', endpoint_type='publicURL')
        return heatclient.Client('1',
                                 endpoint=heat_url,
                                 token=cls.keystone_client().auth_token)

    @staticmethod
    @memoize
    def congress_client():
        auth = keystoneclient.auth.identity.v2.Password(
            auth_url=CONF.murano.auth_url,
            username=CONF.murano.user,
            password=CONF.murano.password,
            tenant_name=CONF.murano.tenant)
        session = keystoneclient.session.Session(auth=auth)
        return cclient.Client(session=session,
                              service_type='policy')

    @classmethod
    @memoize
    def murano_client(cls):
        url = CONF.murano.murano_url
        murano_url = url if 'v1' not in url else "/".join(
            url.split('/')[:url.split('/').index('v1')])
        keystone_client = cls.keystone_client()
        return mclient.Client('1',
                              endpoint=murano_url,
                              token=keystone_client.auth_token)

    @staticmethod
    @memoize
    def packages_path():
        return os.path.abspath(os.path.join(
            os.path.dirname(__file__),
            os.path.pardir,
            'murano-app-incubator'
        ))

    @classmethod
    def upload_package(cls, package_name, body, app):
        files = {'%s' % package_name: open(app, 'rb')}
        package = cls.murano_client().packages.create(body, files)
        if not hasattr(cls, '_packages'):
            cls._packages = []
        cls._packages.append(package)
        return package

    @classmethod
    def purge_uploaded_packages(cls):
        if hasattr(cls, '_packages'):
            for pckg in cls._packages:
                cls.murano_client().packages.delete(pckg.id)

    @classmethod
    def upload_telnet(cls):
        return cls.upload_package(
            'Telnet', {"categories": ["Web"], "tags": ["tag"]},
            os.path.join(cls.packages_path(),
                         'io.murano.apps.linux.Telnet.zip'))

    @classmethod
    def upload_postgres(cls):
        return cls.upload_package(
            'PostgreSQL',
            {"categories": ["Databases"], "tags": ["tag"]},
            os.path.join(cls.packages_path(),
                         'io.murano.databases.PostgreSql.zip'))

    @classmethod
    def upload_sql_db(cls):
        return cls.upload_package(
            'SqlDatabase',
            {"categories": ["Databases"], "tags": ["tag"]},
            os.path.join(cls.packages_path(),
                         'io.murano.databases.SqlDatabase.zip'))

    @classmethod
    def upload_apache(cls):
        return cls.upload_package(
            'Apache',
            {"categories": ["Application Servers"], "tags": ["tag"]},
            os.path.join(cls.packages_path(),
                         'io.murano.apps.apache.ApacheHttpServer.zip'))

    @classmethod
    def upload_tomcat(cls):
        return cls.upload_package(
            'Tomcat',
            {"categories": ["Application Servers"], "tags": ["tag"]},
            os.path.join(cls.packages_path(),
                         'io.murano.apps.apache.Tomcat.zip'))

    def environment_delete(self, environment_id, timeout=180):
        self.murano_client().environments.delete(environment_id)

        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                self.murano_client().environments.get(environment_id)
            except exceptions.HTTPNotFound:
                return
        raise Exception(
            'Environment {0} was not deleted in {1} seconds'.format(
                environment_id, timeout))