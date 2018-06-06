# -*- coding: utf-8 -*-

import logging
from imio.migrator.migrator import Migrator

logger = logging.getLogger('imio.dashboard')


class Migrate_To_2(Migrator):

    def __init__(self, context):
        Migrator.__init__(self, context)

    def run(self):
        logger.info('Migrating to imio.dashboard 2...')
        self.cleanRegistries()
        self.runProfileSteps('imio.dashboard', steps=['jsregistry'])
        self.finish()


def migrate(context):
    '''
    '''
    Migrate_To_2(context).run()
