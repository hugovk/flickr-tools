#!/usr/bin/python

"""
Flickr utility functions
"""
from __future__ import print_function
import os
try:
    from urllib2 import urlopen
except ImportError:
    from urllib.request import urlopen


def download(url, title, noclobber=False, number=None):
    if title:
        file_name = title + ".jpg"
        # Make Windows-safe
        file_name = "".join(
            c for c in file_name if c.isalnum() or c in [' ', '.']).rstrip()
    else:
        file_name = url.split('/')[-1]

    if number:
        file_name = number + "-" + file_name

    if noclobber and os.path.exists(file_name):
        print("File already exists, skipping:", file_name)
        return

    u = urlopen(url)
    f = open(file_name, 'wb')
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    print("Downloading: %s Bytes: %s" % (file_name, file_size))

    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break

        file_size_dl += len(buffer)
        f.write(buffer)
        status = r"%10d  [%3.2f%%]" % (
            file_size_dl, file_size_dl * 100. / file_size)
        status = status + chr(8)*(len(status)+1)
        print(status, end=" ")

    f.close()
    return

# End of file
