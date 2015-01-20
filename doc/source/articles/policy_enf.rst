=================================
Murano Policy Enforcement Example
=================================

1. Enable policy enforcement in murano
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    - edit */etc/murano/murano.conf*:

    .. code-block:: ini

        [engine]
        # Enable model policy enforcer using Congress (boolean value)
        enable_model_policy_enforcer = true
    ..

    - restart murano

2. Create murano and murano_system policy
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    - Check if policies **murano** and **murano_system** were created by datasource driver:
        ``congress policy list``
    - If there is no **murano** and **murano_system** then create them by these commands:

    .. code-block:: console

        congress policy create murano
        congress policy create murano_system
    ..

3. Create flavor_ram rule
^^^^^^^^^^^^^^^^^^^^^^^^^
    We create the rule that resolves parameters of flavor by flavor name and returns *ram* parameter. It uses rule *flavors* from *nova* policy.

    Use this command to create the rule:

    .. code-block:: console

        congress policy rule create murano_system "flavor_ram(flavor_name, ram) :- nova:flavors(id, flavor_name, cpus, ram)"
    ..

4. Create predeploy_error rule
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    Then we create this rule which references **flavor_ram** rule we created before. It disables flavors with ram higher than 2048 MB and constructs message returned to the user in *msg* variable. Policy validation checks for rule **predeploy_error** and other referenced rules are evaluated by congress engine.

    .. code-block:: console

        predeploy_error(eid, obj_id, msg) :-
           murano:object(obj_id, eid, type),
           murano:property(obj_id, "flavor", flavor_name),
           flavor_ram(flavor_name, ram),
           gt(ram, 2048),
           murano:property(obj_id, "name", obj_name),
           concat(obj_name, ": instance flavor has RAM size over 2048MB", msg)
    ..

    Use this command to create the rule:

    .. code-block:: console

      congress policy rule create murano_system "predeploy_error(eid, obj_id, msg) :- murano:object(obj_id, eid, type), murano:property(obj_id, \"flavor\", flavor_name), flavor_ram(flavor_name, ram), gt(ram, 2048), murano:property(obj_id, \"name\", obj_name), concat(obj_name, \": instance flavor has RAM size over 2048MB\", msg)"
    ..

    In this example we used data from policy **murano** which is represented by ``murano:property`` where are stored rows with decomposition of model representing murano application. We also used built-in functions of congress - ``gt`` - greater than, and ``concat`` which joins two strings into variable.

5. Create environment with simple application
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    - Choose Git application from murano applications
    - Create with **"m1.medium"** instance flavor which uses 4096MB so validation will fail

    .. image:: new-instance.png


6. Deploy environment
^^^^^^^^^^^^^^^^^^^^^
    - environment is in Status: **Deploy FAILURE**
    - Check deployment log:

    .. image:: deployment-log.png