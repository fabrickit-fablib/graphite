# coding: utf-8

from lib.api import *  # noqa
from fablib import python


class Carbon():
    datamap = {
        'user': 'nobody',
        'group': 'nobody',
        'initscript': {
            'wait_interval': 5,
            'wait_interval_time': 1,
        },
        'daemons': {
            # 'carbon_relay0': {
            #
            # }
        }
    }

    def __init__(self, datamap={}):
        self.datamap.update(datamap)
        print 'carbon'

    def setup(self):
        datamap = self.datamap
        is_updated = self.install_carbon()
        for name in datamap['daemons']:
            service_name = 'carbon-' + name
            service.enable(service_name)
            service.start(service_name, pty=False)
            if is_updated:
                service.restart(service_name, pty=False)

        return 0

    def install_carbon(self):
        datamap = self.datamap

        python.setup()
        python.install_from_git('carbon',
                                'https://github.com/graphite-project/carbon.git -b megacarbon')

        graphite_dir = '/opt/graphite'
        storage_dir = os.path.join(graphite_dir, 'storage')
        storage_files = os.path.join(storage_dir, '*')
        sudo('chown {0}:{1} {2}'.format(datamap['user'], datamap['group'], storage_dir))
        sudo('chown {0}:{1} {2}'.format(datamap['user'], datamap['group'], storage_files))

        daemons_dir = '/opt/graphite/conf/carbon-daemons/'
        daemon_confs = [
            'daemon.conf',
            'relay.conf',
            'aggregation.conf',
            'amqp.conf',
            'filter-rules.conf',
            'relay.conf',
            'storage-rules.conf',
            'aggregation-filters.conf',
            'daemon.conf',
            'listeners.conf',
            'relay-rules.conf',
            'writer.conf',
            'aggregation-rules.conf',
            'db.conf',
            'management.conf',
            'rewrite-rules.conf',
        ]

        is_updated = False
        for name, daemon in datamap['daemons'].items():
            daemon_dir = os.path.join(daemons_dir, name)
            filer.mkdir(daemon_dir)

            for daemon_conf in daemon_confs:
                is_updated = filer.template(os.path.join(daemon_dir, daemon_conf), data={
                    'user': datamap['user'],
                    'daemon': daemon,
                }, src_target=os.path.join('carbon-daemon', daemon_conf)) or is_updated

            is_updated = filer.template('/etc/init.d/carbon-{0}'.format(name), '755', data={
                'description': 'Carbon Daemon: {0}'.format(name),
                'name': name,
                'user': datamap['user'],
                'exec': os.path.join(graphite_dir, 'bin/carbon-daemon.py'),
                'initscript': datamap['initscript'],
            }, src_target='carbon-initscript') or is_updated

        return is_updated
