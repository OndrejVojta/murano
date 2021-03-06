#    Copyright (c) 2014 Hewlett-Packard Development Company, L.P.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
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

# Based on designate/policy.py

import murano.openstack.common.log as logging
from murano.openstack.common import policy
from oslo.config import cfg
from webob import exc as exceptions

LOG = logging.getLogger(__name__)

CONF = cfg.CONF

_ENFORCER = None


def reset():
    global _ENFORCER
    if _ENFORCER:
        _ENFORCER.clear()
    _ENFORCER = None


def set_rules(data, default_rule=None, overwrite=True):
    default_rule = default_rule or cfg.CONF.policy_default_rule
    if not _ENFORCER:
        LOG.debug("Enforcer not present, recreating at rules stage.")
        init()

    if default_rule:
        _ENFORCER.default_rule = default_rule

    msg = "Loading rules %s, default: %s, overwrite: %s"
    LOG.debug(msg, data, default_rule, overwrite)

    if isinstance(data, dict):
        rules = dict((k, policy.parse_rule(v)) for k, v in data.items())
        rules = policy.Rules(rules, default_rule)
    else:
        rules = policy.Rules.load_json(data, default_rule)

    _ENFORCER.set_rules(rules, overwrite=overwrite)


def init(default_rule=None, use_conf=True):
    global _ENFORCER
    if not _ENFORCER:
        LOG.debug("Enforcer is not present, recreating.")
        _ENFORCER = policy.Enforcer(use_conf=use_conf)
    _ENFORCER.load_rules()


def check(rule, ctxt, target={}, do_raise=True, exc=exceptions.HTTPForbidden):
    creds = ctxt.to_dict()

    try:
        result = _ENFORCER.enforce(rule, target, creds, do_raise, exc)
    except Exception:
        result = False
        raise
    else:
        return result
    finally:
        extra = {'policy': {'rule': rule, 'target': target}}

        if result:
            LOG.audit("Policy check succeeded for rule '%s' on target %s",
                      rule, repr(target), extra=extra)
        else:
            LOG.audit("Policy check failed for rule '%s' on target: %s",
                      rule, repr(target), extra=extra)
