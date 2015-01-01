#!/usr/bin/python

"""
Flickr search downloader
Based on http://pastebin.com/JEJiCNRd
"""
import argparse
import os
# import xml.etree.ElementTree as ET

import flickrapi
import flickr_utils

# Optional, http://stackoverflow.com/a/1557906/724176
try:
    import timing
    assert timing  # silence warnings
except ImportError:
    pass

api_key = os.environ['FLICKR_API_KEY']
api_secret = os.environ['FLICKR_SECRET']


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Download a Flickr set',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "--text",
        help="Search text")
    parser.add_argument(
        "--tags",
        help="Search tags")
    parser.add_argument(
        "-s", "--size", default="b",
        choices=("s", "q", "t", "m", "n", "z", "c", "b", "o"),
        help="The size of photo you want to download: "
        "s - 75x75, "
        "q - 150x150, "
        "t - 100 on the longest side, "
        "m - 240 on the longest side, "
        "n - 320 on the longest side, "
        "z - 640 on the longest side, "
        "c - 800 on the longest side, "
        "b - 1024 on the longest side (default), "
        "o - original")
    parser.add_argument(
        "-t", "--title", action="store_true",
        help="Use the title as the filename")
    parser.add_argument(
        "-nc", "--noclobber", action="store_true",
        help="Don't clobber pre-exisiting files")
    parser.add_argument(
        "-n", "--number", action="store_true",
        help="Prefix filenames with a serial number")
    args = parser.parse_args()

    flickr = flickrapi.FlickrAPI(api_key, api_secret)
    flickr.authenticate_via_browser(perms='read')

    i = 0
    number = None
    for photo in flickr.walk(
            tag_mode='all',
            # privacy_filter='1', # public
            # max_taken_date='2009-02-07',
            text=args.text,
            tags=args.tags):

        i += 1
        if args.number:
            number = str(i).zfill(6)

        photo_id = photo.attrib['id']
        photo_info = flickr.photos_getInfo(photo_id=photo_id)
        photo_info = photo_info[0]

        secret = photo_info.attrib['secret']
        size = args.size
        if size == 'o':
            if'originalsecret' in photo_info.attrib:
                secret = photo_info.attrib['originalsecret']
            else:
                size = 'b'  # Next best

        if args.title:
            photo_title = photo.attrib['title']
        else:
            photo_title = None

        flickr_utils.download(
            "http://farm%s.static.flickr.com/%s/%s_%s_%s.jpg" %
            (photo.attrib['farm'], photo.attrib['server'],
                photo.attrib['id'], secret, size),
            photo_title, args.noclobber, number)

# End of file
