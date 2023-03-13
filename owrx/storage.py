from owrx.config.core import CoreConfig
from owrx.config import Config
from datetime import datetime

import os
import re

import logging

logger = logging.getLogger(__name__)

class Storage(object):
    def __init__(self):
        self.filePattern = r'[A-Z]+-[0-9]+-[0-9]+(-[0-9]+)?\.bmp'

    # Get file name pattern
    def getNamePattern(self):
        return self.filePattern

    # Create stored file name by inserting current UTC date
    # and time into the pattern spot designated with "{0}"
    def makeFileName(self, pattern: str = '{0}', frequency: int = 0):
        d = datetime.utcnow().strftime('%y%m%d-%H%M%S')
        f = ('-%d' % (frequency // 1000)) if frequency>0 else ''
        return pattern.format(d + f)

    # Get complete path to a stored file from its filename by
    # adding folder name
    def getFilePath(self, filename: str):
        return os.path.join(CoreConfig().get_temporary_directory(), filename)

    # Get list of stored files, sorted in reverse alphabetic order
    # (so that newer files appear first)
    def getStoredFiles(self):
        dir = CoreConfig().get_temporary_directory()
        files = [os.path.join(dir, f) for f in os.listdir(dir) if re.match(self.filePattern, f)]
        files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        return [os.path.basename(f) for f in files]

    # Delete all stored files except for <keep_files> newest ones
    def cleanStoredFiles(self):
        pm    = Config.get()
        keep  = pm["keep_files"]
        dir   = CoreConfig().get_temporary_directory()
        files = [os.path.join(dir, f) for f in os.listdir(dir) if re.match(self.filePattern, f)]
        files.sort(key=lambda x: os.path.getmtime(x), reverse=True)

        for f in files[keep:]:
            logger.debug("Deleting stored file '%s'." % os.path.basename(f))
            try:
                os.unlink(f)
            except Exception as exptn:
                logger.debug(str(exptn))

