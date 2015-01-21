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
        '?': {type: io.murano.Environment, id: 83bff5acf8354816b08cf9b4917c898d}
        applications:
        - '?': {id: e7a13d3c-b3c9-42fa-975d-a47b142fd233, type: io.murano.databases.MySql}
    ..

Transformed to these rules:

- ``murano:object+("83bff5acf8354816b08cf9b4917c898d", "83bff5acf8354816b08cf9b4917c898d", "io.murano.Environment")``
- ``murano:object+("83bff5acf8354816b08cf9b4917c898d", "e7a13d3c-b3c9-42fa-975d-a47b142fd233", "io.murano.databases.MySql")``

.. note:: In case of rule for environment ``environment_id``, ``object_id`` are the same.


``murano:property(object_id, property_name, property_value)``
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
Each object can have properties. In this example we have application with one property:

    .. code-block:: yaml

        applications:
        - '?': {id: e7a13d3c-b3c9-42fa-975d-a47b142fd233, type: io.murano.databases.MySql}
        database: wordpress
    ..

Transformed to these rules:

- ``murano:property+("e7a13d3c-b3c9-42fa-975d-a47b142fd233", "database", "wordpress")``

Inner properties are also supported using dot notation:

    .. code-block:: yaml

        instance:
        '?': {id: 825dc61d-217a-4fd8-80fc-43807f8d6fa2, type: io.murano.resources.LinuxMuranoInstance}
        networks:
          useFlatNetwork: false
    ..

Transformed to these rules:

- ``murano:property+("825dc61d-217a-4fd8-80fc-43807f8d6fa2", "networks.useFlatNetwork", "False")``

If model contains list of values it is represented as set of multiple rules:

    .. code-block:: yaml

        instances:
        - '?': {id: be3c5155-6670-4cf6-9a28-a4574ff70b71, type: io.murano.resources.LinuxMuranoInstance}
        networks:
          customNetworks: [10.0.1.0, 10.0.2.0]
    ..

Transformed to these rules:

- ``murano:property+("be3c5155-6670-4cf6-9a28-a4574ff70b71", "networks.customNetworks", "10.0.1.0")``
- ``murano:property+("be3c5155-6670-4cf6-9a28-a4574ff70b71", "networks.customNetworks", "10.0.2.0")``

There is one special property on environment for tenant_id:

- ``murano:property+("...", "tenant_id", "123")``

``murano:relationship(source, target, name)``
""""""""""""""""""""""""""""""""""""""""""""""
Murano app models can contain references to other applications. In this example WordPress application references MySQL in property "database":

    .. code-block:: yaml

        applications:
        - '?':
            _26411a1861294160833743e45d0eaad9: {name: MySQL}
            id: 0aafd67e-72e9-4ae0-bb62-fe724f77df2a
            type: io.murano.databases.MySql
        - '?':
            _26411a1861294160833743e45d0eaad9: {name: WordPress}
            id: 50fa68ff-cd9a-4845-b573-2c80879d158d
            type: io.murano.apps.WordPress
          database: 0aafd67e-72e9-4ae0-bb62-fe724f77df2a
    ..

Transformed to these rules:

- ``murano:relationship+("50fa68ff-cd9a-4845-b573-2c80879d158d", "0aafd67e-72e9-4ae0-bb62-fe724f77df2a", "database")``

.. note:: For property "database" we do not create rule ``murano:property+``.

Also if we define inner object inside other object, they will have relationship between them:

    .. code-block:: yaml

        applications:
        - '?':
            _26411a1861294160833743e45d0eaad9: {name: MySQL}
            id: 0aafd67e-72e9-4ae0-bb62-fe724f77df2a
            type: io.murano.databases.MySql
          instance:
            '?': {id: ed8df2b0-ddd2-4009-b3c9-2e7a368f3cb8, type: io.murano.resources.LinuxMuranoInstance}
    ..

Transformed to these rules:

- ``murano:relationship+("0aafd67e-72e9-4ae0-bb62-fe724f77df2a", "ed8df2b0-ddd2-4009-b3c9-2e7a368f3cb8", "instance")``

murano:parent_type(object_id, parent_name)
"""""""""""""""""""""""""""""""""""""""""""
Each object in murano has class type and these classes can inherit from one or more parents:

- e.g. ``io.murano.resources.LinuxMuranoInstance`` inherits from ``io.murano.resources.LinuxInstance`` which inherits form ``io.murano.resources.Instance``

So this model:

    .. code-block:: yaml

        instances:
        - '?': {id: be3c5155-6670-4cf6-9a28-a4574ff70b71, type: io.murano.resources.LinuxMuranoInstance}
    ..

Transformed to these rules:

- ``murano:object+("...", "be3c5155-6670-4cf6-9a28-a4574ff70b71", "io.murano.resources.LinuxMuranoInstance")``
- ``murano:parent_type+("be3c5155-6670-4cf6-9a28-a4574ff70b71", "io.murano.resources.LinuxMuranoInstance")``
- ``murano:parent_type+("be3c5155-6670-4cf6-9a28-a4574ff70b71", "io.murano.resources.LinuxInstance")``
- ``murano:parent_type+("be3c5155-6670-4cf6-9a28-a4574ff70b71", "io.murano.resources.Instance")``

.. note:: ``io.murano.resources.LinuxMuranoInstance`` is parent too for easier handling of user-created rules.
