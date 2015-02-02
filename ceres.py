# coding: utf-8

from fablib import python


class Ceres():
    data = {}

    def __init__(self, data={}):
        self.data.update(data)

    def setup(self):
        self.install_ceres()

    def install_ceres(self):
        python.setup()
        python.install_from_git('ceres',
                                'https://github.com/graphite-project/ceres.git')
