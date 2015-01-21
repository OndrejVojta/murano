===========================================
Murano Policy Enforcement - Developer Guide
===========================================

This document describes internals of murano policy enforcement.

Congress Integration
--------------------
- congress rest client
- simulation api

Model Decomposition
-------------------

Models of Murano applications are transformed to set of rules that are processed by congress. This represent data for policy validation.

There are several "tables" created in murano policy for different kind of rules:

- ``murano:object(environment_id, object_id, type_name)``
- ``murano:property(object_id, property_name, property_value)``
- ``murano:relationship(source, target, name)``
- ``murano:parent_type(object_id, parent_name)``

``murano:object(environment_id, object_id, type_name)``
""""""""""""""""""""""""""""""""""""""""""""""""""""""""
This rule is used for representation of all objects in murano model (environment, applications, instances, ...):

    .. code-block:: yaml

        name: wordpress-env
        '?': {type: io.murano.Environment, id: 83bff5ac}
        applications:
        - '?': {id: e7a13d3c, type: io.murano.databases.MySql}
    ..

Transformed to these rules:

- ``murano:object+("83bff5ac", "83bff5ac", "io.murano.Environment")``
- ``murano:object+("83bff5ac", "e7a13d3c", "io.murano.databases.MySql")``

.. note:: In case of rule for environment ``environment_id``, ``object_id`` are the same.


``murano:property(object_id, property_name, property_value)``
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
Each object can have properties. In this example we have application with one property:

    .. code-block:: yaml

        applications:
        - '?': {id: e7a13d3c, type: io.murano.databases.MySql}
        database: wordpress
    ..

Transformed to these rules:

- ``murano:property+("e7a13d3c", "database", "wordpress")``

Inner properties are also supported using dot notation:

    .. code-block:: yaml

        instance:
        '?': {id: 825dc61d, type: io.murano.resources.LinuxMuranoInstance}
        networks:
          useFlatNetwork: false
    ..

Transformed to these rules:

- ``murano:property+("825dc61d", "networks.useFlatNetwork", "False")``

If model contains list of values it is represented as set of multiple rules:

    .. code-block:: yaml

        instances:
        - '?': {id: be3c5155, type: io.murano.resources.LinuxMuranoInstance}
        networks:
          customNetworks: [10.0.1.0, 10.0.2.0]
    ..

Transformed to these rules:

- ``murano:property+("be3c5155", "networks.customNetworks", "10.0.1.0")``
- ``murano:property+("be3c5155", "networks.customNetworks", "10.0.2.0")``

There is one special property on environment for tenant_id:

- ``murano:property+("...", "tenant_id", "123")``

``murano:relationship(source, target, name)``
""""""""""""""""""""""""""""""""""""""""""""""
Murano app models can contain references to other applications. In this example WordPress application references MySQL in property "database":

    .. code-block:: yaml

        applications:
        - '?':
            id: 0aafd67e
            type: io.murano.databases.MySql
        - '?':
            id: 50fa68ff
            type: io.murano.apps.WordPress
          database: 0aafd67e
    ..

Transformed to these rules:

- ``murano:relationship+("50fa68ff", "0aafd67e", "database")``

.. note:: For property "database" we do not create rule ``murano:property+``.

Also if we define inner object inside other object, they will have relationship between them:

    .. code-block:: yaml

        applications:
        - '?':
            id: 0aafd67e
            type: io.murano.databases.MySql
          instance:
            '?': {id: ed8df2b0, type: io.murano.resources.LinuxMuranoInstance}
    ..

Transformed to these rules:

- ``murano:relationship+("0aafd67e", "ed8df2b0", "instance")``

murano:parent_type(object_id, parent_name)
"""""""""""""""""""""""""""""""""""""""""""
Each object in murano has class type and these classes can inherit from one or more parents:

e.g. ``LinuxMuranoInstance`` > ``LinuxInstance`` > ``Instance``

So this model:

    .. code-block:: yaml

        instances:
        - '?': {id: be3c5155, type: LinuxMuranoInstance}
    ..

Transformed to these rules:

- ``murano:object+("...", "be3c5155", "LinuxMuranoInstance")``
- ``murano:parent_type+("be3c5155", "LinuxMuranoInstance")``
- ``murano:parent_type+("be3c5155", "LinuxInstance")``
- ``murano:parent_type+("be3c5155", "Instance")``

.. note:: Type of object is also repeated among parent types (``LinuxMuranoInstance`` in example) for easier handling of user-created rules.

.. note:: If type inherits from more than one parent and those parents inherit from one common type, ``parent_type`` rule is included only once for common type.
