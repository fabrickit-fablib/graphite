# coding: utf-8

from fabkit import *  # noqa
from fablib.base import SimpleBase


class Graphite(SimpleBase):
    def __init__(self, enable_services=['.*']):
        self.data_key = 'graphite'
        self.data = {
        }

        self.packages = {
            'CentOS Linux 7.*': [
                'epel-release',
                'httpd',
                'graphite-web',
                {'name': 'go-carbon', 'path': 'https://github.com/lomik/go-carbon/releases/download/v0.7.3/go-carbon-0.7.3-1.el6.x86_64.rpm'},  # noqa
            ]
        }

        self.services = ['go-carbon', 'httpd']

    def setup(self):
        data = self.init()

        if self.is_tag('package'):
            self.install_packages()
            filer.mkdir('/data/graphite/whisper')

        filer.template('/data/graphite/schemas')
        self.start_services().enable_services()
