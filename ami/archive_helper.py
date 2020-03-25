import sys
import os
from pyunpack import Archive


class ArchiveHelper:
    @staticmethod
    def extract(archive_path, target_path):
        if not os.path.exists(target_path):
            os.makedirs(target_path)
        try:
            Archive(archive_path).extractall(target_path)
        except OSError as err:
            print("OS error: {0}".format(err))
        except ValueError:
            print("Could not convert data to an integer.")
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise
