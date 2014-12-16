# coding: utf-8

from lib.api import *  # noqa
from fablib import python


class GraphiteWeb():
    datamap = {
        'user': 'nobody',
        'group': 'nobody',
        'secret_key': 'default',
        'time_zone': 'Asia/Tokyo',
        'storage_finders': [
            'graphite.finders.ceres.CeresFinder',
            # 'graphite.finders.standard.StandardFinder',
        ]
    }

    def __init__(self, datamap):
        self.datamap.update(datamap)

    def setup(self):
        is_updated = self.install_graphite_web()
        service.enable('httpd')
        service.start('httpd')
        if is_updated:
            service.restart('httpd')

        self.db_sync()
        return True

    def db_sync(self):
        sudo('sh -c "cd /opt/graphite/webapp/ && ./manage.py syncdb --noinput"')

    def install_graphite_web(self):
        datamap = self.datamap

        package.install('pycairo')
        package.install('cairo-devel')
        package.install('bitmap-fonts-compat')
        package.install('httpd')
        package.install('mod_wsgi')
        package.install('MySQL-python')

        python.setup()
        sudo('pip install django==1.6.8')
        python.install_from_git('graphite-web',
                                'https://github.com/graphite-project/graphite-web.git')

        log_dir = '/opt/graphite/storage/log/webapp/'
        owner = '{0[user]}:{0[group]}'.format(datamap)
        filer.mkdir(log_dir, owner=owner)
        log_files = ['access.log', 'error.log', 'exception.log', 'info.log']
        for log_file in log_files:
            log_file = os.path.join(log_dir, log_file)
            filer.touch(log_file, owner=owner)

        manage_py = os.path.join(conf.REMOTE_TMP_DIR, 'git/graphite-web.git/webapp/manage.py')
        sudo('cp {0} /opt/graphite/webapp/'.format(manage_py))

        is_updated = filer.template('/opt/graphite/webapp/graphite/local_settings.py',
                                    data=self.datamap)

        is_updated = filer.template('/opt/graphite/webapp/graphite/settings.py',
                                    data=self.datamap) or is_updated

        is_updated = filer.template('/opt/graphite/conf/graphite.wsgi') or is_updated

        is_updated = filer.template('/etc/httpd/conf.d/graphite-vhost.conf', data={
            'user': datamap['user'],
            'group': datamap['group'],
        }) or is_updated

        return is_updated
