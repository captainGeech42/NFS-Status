#!/usr/bin/env python3

# This script rotates the persistent log for NFS status

from datetime import datetime
import os
import sys

def get_yesterday():
    return datetime.now().strftime("%Y-%m-%d")


def compress(filename):
    new_fp = "{}.{}".format(filename, get_yesterday())
    os.system("mv {} {}".format(filename, new_fp))
    os.system("gzip {}".format(new_fp))


def main(argv):
    log_fp = "/var/log/nfs_status/nfs_status.log"
    compress(log_fp)

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
