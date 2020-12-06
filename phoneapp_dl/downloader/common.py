 import os
from .. import config, util


class DownloaderBase():
    """Base class for downloaders"""
    scheme = ""

    def __init__(self, job):
        self.out = job.out
        self.session = job.extractor.session
        self.part = self.config("part", True)
        self.partdir = self.config("part-directory")
        self.log = job.get_logger("downloader." + self.scheme)

        if self.partdir:
            self.partdir = util.expand_path(self.partdir)
            os.makedirs(self.partdir, exist_ok=True)

    def config(self, key, default=None):
        """Interpolate downloader config value for 'key'"""
        return config.interpolate(("downloader", self.scheme), key, default)

    def download(self, url, pathfmt):
        """Write data from 'url' into the file specified by 'pathfmt'"""

