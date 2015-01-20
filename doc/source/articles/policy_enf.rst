=================================
Murano Policy Enforcement Example
=================================

1. Enable policy enforcement in murano
    - murano.conf

2. Create **murano** and **murano_system** policy
    - if not done by datasource driver

3. Create **flavor_ram** rule
    .. code-block:: console

        $(openstack) congress policy rule create murano_system "flavor_ram(flavor_name, ram) :- nova:flavors(id, flavor_name, cpus, ram)"
    ..

4. Create **predeploy_error** rule

    .. code-block:: console

        $(openstack) congress policy rule create murano_system "predeploy_error(eid, obj_id, msg) :- murano:object(obj_id, eid, type), murano:property(obj_id, \"flavor\", flavor_name), flavor_ram(flavor_name, ram), gt(ram, 2048), murano:property(obj_id, \"name\", obj_name), concat(obj_name, \": instance flavor has RAM size over 2048MB\", msg)"
    ..

5. Create environment with simple application
    - Git picture

6. Deploy environment with "m1.medium" flavor
    - instance creation picture

    .. code-block:: console

        2015-01-20 04:24:15 - Model validation failed:
          ftceni54s1ywb1: instance flavor has RAM size over 2048MB
    ..