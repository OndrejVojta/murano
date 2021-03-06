..
      Copyright 2014 Mirantis, Inc.

      Licensed under the Apache License, Version 2.0 (the "License"); you may
      not use this file except in compliance with the License. You may obtain
      a copy of the License at

          http://www.apache.org/licenses/LICENSE-2.0

      Unless required by applicable law or agreed to in writing, software
      distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
      WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
      License for the specific language governing permissions and limitations
      under the License.

Application Catalog API
=======================

Manage application definitions in the Application Catalog.
You can browse, edit and upload new application packages (.zip.package archive with all data that required for a service deployment).

Packages
========

Methods for application package management

**Package Properties**

- ``id``: guid of a package (``fully_qualified_name`` can also be used for some API functions)
- ``fully_qualified_name``: fully qualified domain name -  domain name that specifies exact application location
- ``name``: user-friendly name
- ``type``: package type, "library" or "application"
- ``description``: text information about application
- ``author``: name of application author
- ``tags``: list of short names, connected with the package, which allows to search applications easily
- ``categories``: list of application categories
- ``class_definition``: list of class names used by a package
- ``is_public``: determines whether the package is shared for other tenants
- ``enabled``: determines whether the package is browsed in the Application Catalog
- ``owner_id``: id of a tenant which user  not an owned the package

List packages
-------------

`/v1/catalog/packages?{marker}{limit}{order_by}{type}{category}{fqn}{owned}{class_name} [GET]`

This is the compound request to list and search through application catalog.
If there are no search parameters all packages that is_public, enabled and belong to the user's tenant will be listed.
Default order is by 'created' field.
For an admin role all packages are available.

**Parameters**

+----------------------+-------------+------------------------------------------------------------------------------------------------------------------------------+
| Attribute            | Type        | Description                                                                                                                  |
+======================+=============+==============================================================================================================================+
| ``marker``           | string      | A package identifier marker may be specified. When present only packages which occur after the identifier ID will be listed  |
+----------------------+-------------+------------------------------------------------------------------------------------------------------------------------------+
| ``limit``            | string      | When present the maximum number of results returned will not exceed the specified value.                                     |
|                      |             | The typical pattern of limit and marker is to make an initial limited request and then to use the ID of the last package from|
|                      |             | the response as the marker parameter in a subsequent limited request.                                                        |
+----------------------+-------------+------------------------------------------------------------------------------------------------------------------------------+
| ``order_by``         | string      | Allows to sort packages by: `fqn`, `name`, `created`. Created is default value.                                              |
+----------------------+-------------+------------------------------------------------------------------------------------------------------------------------------+
| ``type``             | string      | Allows to point a type of package: `application`, `library`                                                                  |
+----------------------+-------------+------------------------------------------------------------------------------------------------------------------------------+
| ``category``         | string      | Allows to point a categories for a search                                                                                    |
+----------------------+-------------+------------------------------------------------------------------------------------------------------------------------------+
| ``fqn``              | string      | Allows to point a fully qualified package name for a search                                                                  |
+----------------------+-------------+------------------------------------------------------------------------------------------------------------------------------+
| ``owned``            | bool        | Search only from packages owned by user tenant                                                                               |
+----------------------+-------------+------------------------------------------------------------------------------------------------------------------------------+
| ``include_disabled`` | bool        | Include disabled packages in a the result                                                                                    |
+----------------------+-------------+------------------------------------------------------------------------------------------------------------------------------+
| ``search``           | string      | Gives opportunity to search specified data by all the package parameters                                                     |
+----------------------+-------------+------------------------------------------------------------------------------------------------------------------------------+
| ``class_name``       | string      |Search only for packages, that use specified class                                                                            |
+----------------------+-------------+------------------------------------------------------------------------------------------------------------------------------+

**Response 200 (application/json)**

::

         {"packages": [
                      {
                        "id": "fed57567c9fa42c192dcbe0566f8ea33",
                         "fully_qualified_name" : "com.example.murano.services.linux.telnet",
                         "is_public": false,
                         "name": "Telnet",
                         "type": "linux",
                         "description": "Installs Telnet service",
                         "author": "Openstack, Inc.",
                         "created": "2014-04-02T14:31:55",
                         "enabled": true,
                         "tags": ["linux", "telnet"],
                         "categories": ["Utility"],
                         "owner_id": "fed57567c9fa42c192dcbe0566f8ea40"
                      },
                      {
                        "id": "fed57567c9fa42c192dcbe0566f8ea31",
                        "fully_qualified_name": "com.example.murano.services.windows.WebServer",
                        "is_public": true,
                        "name": "Internet Information Services",
                        "type": "windows",
                        "description": "The  Internet Information Service sets up an IIS server and joins it into an existing domain",
                        "author": "Openstack, Inc.",
                        "created": "2014-04-02T14:31:55",
                        "enabled": true,
                        "tags": ["windows", "web"],
                        "categories": ["Web"],
                        "owner_id": "fed57567c9fa42c192dcbe0566f8ea40"
                      }]
          }



Upload a new package[POST]
--------------------------

`/v1/catalog/packages`

See the example of multipart/form-data request, It should contain two parts - text (json string) and file object

**Request (multipart/form-data)**

::

    Content-type: multipart/form-data, boundary=AaB03x
    Content-Length: $requestlen

    --AaB03x
    content-disposition: form-data; name="submit-name"

    --AaB03x
    Content-Disposition: form-data; name="JsonString"
    Content-Type: application/json

    {"categories":["web"] , "tags": ["windows"], "is_public": false, "enabled": false}
    `categories` - array, required
    `tags` - array, optional
    `name` - string, optional
    `description` - string, optional
    `is_public` - bool, optional
    `enabled` - bool, optional

    --AaB03x
    content-disposition: file; name="file"; filename="test.tar"
    Content-Type: targz
    Content-Transfer-Encoding: binary

    $binarydata
    --AaB03x--


**Response 200 (application/json)**

::

    {
        "updated": "2014-04-03T13:00:13",
        "description": "A domain service hosted in Windows environment by using Active Directory Role",
        "tags": ["windows"],
        "is_public": true,
        "id": "8f4f09bd6bcb47fb968afd29aacc0dc9",
        "categories": ["test1"],
        "name": "Active Directory",
        "author": "Mirantis, Inc",
        "created": "2014-04-03T13:00:13",
        "enabled": true,
        "class_definition": [
            "com.mirantis.murano.windows.activeDirectory.ActiveDirectory",
            "com.mirantis.murano.windows.activeDirectory.SecondaryController",
            "com.mirantis.murano.windows.activeDirectory.Controller",
            "com.mirantis.murano.windows.activeDirectory.PrimaryController"
        ],
        "fully_qualified_name": "com.mirantis.murano.windows.activeDirectory.ActiveDirectory",
        "type": "Application",
        "owner_id": "fed57567c9fa42c192dcbe0566f8ea40"
    }

Get package details
-------------------

`/v1/catalog/packages/{id} [GET]`

Display details for a package.

**Parameters**

``id`` (required)  Hexadecimal `id` (or fully qualified name) of the package

**Response 200 (application/json)**

::

    {
        "updated": "2014-04-03T13:00:13",
        "description": "A domain service hosted in Windows environment by using Active Directory Role",
        "tags": ["windows"],
        "is_public": true,
        "id": "8f4f09bd6bcb47fb968afd29aacc0dc9",
        "categories": ["test1"],
        "name": "Active Directory",
        "author": "Mirantis, Inc",
        "created": "2014-04-03T13:00:13",
        "enabled": true,
        "class_definition": [
            "com.mirantis.murano.windows.activeDirectory.ActiveDirectory",
            "com.mirantis.murano.windows.activeDirectory.SecondaryController",
            "com.mirantis.murano.windows.activeDirectory.Controller",
            "com.mirantis.murano.windows.activeDirectory.PrimaryController"
        ],
        "fully_qualified_name": "com.mirantis.murano.windows.activeDirectory.ActiveDirectory",
        "type": "Application",
        "owner_id": "fed57567c9fa42c192dcbe0566f8ea40"
    }

**Response 403**

*  In attempt to get non-public package by user whose tenant is not an owner of this package.

**Response 404**

*  In case specified package id doesn't exist.

Update a Package
================

`/v1/catalog/packages/{id} [PATCH]`

Allows to edit mutable fields (categories, tags, name, description, is_public, enabled).
See the full specification `here <http://tools.ietf.org/html/rfc6902>`_.

**Parameters**

``id`` (required)  Hexadecimal `id` (or fully qualified name) of the package

Allowed operations:

::

    [
        { "op": "add", "path": "/tags", "value": [ "foo", "bar" ] },
        { "op": "add", "path": "/categories", "value": [ "foo", "bar" ] },
        { "op": "remove", "path": "/tags", ["foo"] },
        { "op": "remove", "path": "/categories", ["foo"] },
        { "op": "replace", "path": "/tags", "value": [] },
        { "op": "replace", "path": "/categories", "value": ["bar"] },
        { "op": "replace", "path": "/is_public", "value": true },
        { "op": "replace", "path": "/enabled", "value": true },
        { "op": "replace", "path": "/description", "value":"New description" },
        { "op": "replace", "path": "/name", "value": "New name" }
    ]

**Request 200 (application/murano-packages-json-patch)**

::

    [
     { "op": "add", "path": "/tags", "value": [ "windows", "directory"] },
     { "op": "add", "path": "/categories", "value": [ "Directory" ] }
    ]

**Response 200 (application/json)**

::

    {
        "updated": "2014-04-03T13:00:13",
        "description": "A domain service hosted in Windows environment by using Active Directory Role",
        "tags": ["windows", "directory"],
        "is_public": true,
        "id": "8f4f09bd6bcb47fb968afd29aacc0dc9",
        "categories": ["test1"],
        "name": "Active Directory",
        "author": "Mirantis, Inc",
        "created": "2014-04-03T13:00:13",
        "enabled": true,
        "class_definition": [
            "com.mirantis.murano.windows.activeDirectory.ActiveDirectory",
            "com.mirantis.murano.windows.activeDirectory.SecondaryController",
            "com.mirantis.murano.windows.activeDirectory.Controller",
            "com.mirantis.murano.windows.activeDirectory.PrimaryController"
        ],
        "fully_qualified_name": "com.mirantis.murano.windows.activeDirectory.ActiveDirectory",
        "type": "Application",
        "owner_id": "fed57567c9fa42c192dcbe0566f8ea40"
    }

**Response 403**

*  An attempt to update immutable fields
*  An attempt to perform operation that is not allowed on the specified path
*  An attempt to update non-public package by user whose tenant is not an owner of this package

**Response 404**

* An attempt to update package that doesn't exist


Delete application definition from the catalog
----------------------------------------------

`/v1/catalog/packages/{id} [DELETE]`

**Parameters**

``id`` (required)  Hexadecimal `id` (or fully qualified name) of the package to delete

**Response 404**

* An attempt to delete package that doesn't exist


Get application package
-----------------------

`/v1/catalog/packages/{id}/download [GET]`

Get application definition package

**Parameters**

* id (required)  Hexadecimal `id` (or fully qualified name) of the package

**Response 200 (application/octetstream)**

The sequence of bytes representing package content

**Response 404**

Specified package id doesn't exist


Get UI definition
-----------------

`/v1/catalog/packages/{id}/ui [GET]`

Retrieve UI definition for a application which described in a package with provided id

**Parameters**

* id (required)  Hexadecimal `id` (or fully qualified name) of the package

**Response 200 (application/octet-stream)**

The sequence of bytes representing UI definition

**Response 404**

Specified package id doesn't exist

**Response 403**

Specified package is not public and not owned by user tenant, performing the request

**Response 404**

* Specified package id doesn't exist


Get logo
--------

Retrieve application logo which described in a package with provided id

`/v1/catalog/packages/{id}/logo [GET]`

**Parameters**

id (required)  Hexadecimal `id` (or fully qualified name) of the package

**Response 200 (application/octet-stream)**

The sequence of bytes representing application logo

**Response 403**

Specified package is not public and not owned by user tenant, performing the request

**Response 404**

Specified package is not public and not owned by user tenant, performing the request

Categories
==========

List categories
---------------

`/v1/catalog/packages/categories [GET]`

Retrieve list of all available application categories

**Response 200 (application/json)**

::

        {
            "categories": ["Web service", "Directory", "Database", "Storage"]
        }
