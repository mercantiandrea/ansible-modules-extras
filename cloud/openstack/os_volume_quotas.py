#!/usr/bin/python

# Copyright (c) 2015 Hewlett-Packard Development Company, L.P.
#
# This module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>.

try:
    import shade
    HAS_SHADE = True
except ImportError:
    HAS_SHADE = False

from distutils.version import StrictVersion


DOCUMENTATION = '''
---
module: os_volume_quotas
short_description: Update/Delete volume quotas in a OpenStack tenant.
extends_documentation_fragment: openstack
author: "Andrea Mercanti (@mercantiandrea)"
version_added: "2.2"
description:
   - Update or delete volume quotas in a OpenStack tenant.
options:
  project:
    description:
      - The name or id of the project to which the quota should be assigned
    required: true
  state:
    description:
      - Should the resource be present or absent
    choices: ['present', 'absent']
    required: false
    default: present
  quota:
    description:
      - Dictionary containing the quotas and values you want to update
    required: false

requirements: ["shade"]
'''

EXAMPLES = '''
# Update the quota of the tenant 'demo'
- os_volume_quotas:
    cloud: mycloud
    project: demo
    state: present
    quota:
      backup_gigabytes: 33333
      backups: 33
      gigabytes: 33333
      per_volume_gigabytes: 33333
      snapshots: 33
      volumes: 33

# Delete quotas for the tenant 'demo' and back to defaults
- os_volume_quotas:
    cloud: mycloud
    project: demo
    state: absent
'''

RETURN = '''
quotas:
    description: Dictionary listing all the volume quotas and their values for the project
    returned: On success
    type: dictionary

'''


def main():
    argument_spec = openstack_full_argument_spec(
        project = dict(required=False),
        quota = dict(default=None, type='dict'),
        state = dict(default='present', choices=['absent', 'present']),
    )

    module_kwargs = openstack_module_kwargs()
    module = AnsibleModule(argument_spec, **module_kwargs)

    if not HAS_SHADE:
        module.fail_json(msg='shade is required for this module')

    if (StrictVersion(shade.__version__) < StrictVersion('1.8.0')):
        module.fail_json(msg="To manage volume quotas, the installed version of"
                             "the shade library MUST be >=1.8.0")

    try:
        cloud = shade.operator_cloud(**module.params)

        old_quotas = cloud.get_volume_quotas(module.params['project'])

        if module.params['state'] == 'present':
            cloud.set_volume_quotas(module.params['project'],
                                     **module.params['quota'])

        elif module.params['state'] == 'absent':
            cloud.delete_volume_quotas(module.params['project'])

        new_quotas = cloud.get_volume_quotas(module.params['project'])

        module.exit_json(changed=old_quotas != new_quotas, quotas=new_quotas)

    except shade.OpenStackCloudException as e:
        module.fail_json(msg=str(e))


from ansible.module_utils.basic import *
from ansible.module_utils.openstack import *

if __name__ == '__main__':
    main()
