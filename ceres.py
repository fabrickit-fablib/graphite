# coding: utf-8

from lib.api import *  # noqa
from fablib import python


class Ceres():
    datamap = {}

    def __init__(self, datamap):
        self.datamap.update(datamap)

    def setup(self):
        self.install_ceres()
        return True

    def install_ceres(self):
        datamap = self.datamap

        python.setup()
        python.install_from_git('ceres',
                                'https://github.com/graphite-project/ceres.git')

        return True
