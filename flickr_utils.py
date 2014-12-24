#!/usr/bin/python

"""
Flickr utility functions
"""
from __future__ import print_function
import datetime
import os

try:
    from urllib2 import urlopen
except ImportError:
    from urllib.request import urlopen

import xml.etree.ElementTree as ET
assert ET  # silence warnings


def most_interesting_today_in(flickr, nsid, year, size="b", now=None):
    """Find the most interesting photo on this day in a given year"""
    if now is None:
        now = datetime.datetime.now()

    # Find a photo from this year
    taken_year = now.replace(year=year)

    min_taken_date = datetime.datetime.combine(
        taken_year, datetime.time.min)
    max_taken_date = datetime.datetime.combine(
        taken_year, datetime.time.max)

    # Flickr returns nothing if microseconds set: 23:59:59.99999
    max_taken_date = max_taken_date.replace(microsecond=0)

    # Convert into MySQL datetime
    min_taken_date = min_taken_date.isoformat(' ')
    max_taken_date = max_taken_date.isoformat(' ')

    url_size = "url_" + size
    photos = flickr.photos_search(
        user_id=nsid,
        sort="interestingness-desc",  # most interesting
        privacy_filter="1",  # public
        per_page="1",  # only want a single photo per year
        media="photos",  # no videos
        min_taken_date=min_taken_date,
        max_taken_date=max_taken_date,
        extras=url_size)

    if len(photos[0]) > 0:
        # ET.dump(photos[0][0])
        # photo_id = int(photos[0][0].attrib['id'])
        # ET.dump(photos[0])

        return photos[0][0]
    else:
        return None


def photo_title(photo):
    return photo.attrib['title']


def photo_url(flickr, photo, size):
    # ET.dump(photo)

    url_size = "url_" + size
    print(photo.attrib[url_size])
    return(photo.attrib[url_size])


def download(url, title, noclobber=False, number=None, dir=None):
    if title:
        file_name = title + ".jpg"
        # Make Windows-safe
        file_name = "".join(
            c for c in file_name if c.isalnum() or c in [
                ' ', '.', '-']).rstrip()
    else:
        file_name = url.split('/')[-1]

    if number:
        file_name = number + "-" + file_name

    if len(file_name) > 200:
        file_name = file_name[:200]

    if dir:
        file_name = os.path.join(dir, file_name)

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
