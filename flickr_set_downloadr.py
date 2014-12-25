#!/usr/bin/python

"""
Flickr set downloader
Based on http://pastebin.com/JEJiCNRd
"""
from __future__ import print_function
import argparse
import os
import sys

# import xml.etree.ElementTree as ET

import flickrapi
import flickr_utils

api_key = os.environ['FLICKR_API_KEY']
api_secret = os.environ['FLICKR_SECRET']


def validate_setid(setid):
    if setid.isdigit():
        return setid

    if "flickr.com" in setid:
        print("URL:", setid)
        setid = setid.rstrip("/")
        sets_text = "/sets/"
        sets_pos = setid.find(sets_text)
        setid = setid[sets_pos+len(sets_text):]
        print("Set ID:", setid)
        return setid


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Download a Flickr set',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "setid", help="The Set ID or Flickr URL of the set to download.")
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

    # Optional, http://stackoverflow.com/a/1557906/724176
    try:
        import timing
        assert timing  # silence warnings
    except ImportError:
        pass

    if args.setid is None:
        sys.exit(
            "You must specify a photo set to download. \nUse -h for examples.")
    else:
        args.setid = validate_setid(args.setid)

    flickr = flickrapi.FlickrAPI(api_key, api_secret)
    flickr.authenticate_via_browser(perms='read')

    page = 0
    pages = 1  # may be higher, we'll update it later
    number = None

    while page < pages:
        page += 1
        photo_set = flickr.photosets_getPhotos(
            photoset_id=args.setid, page=page)
        photo_set = photo_set[0]
        print(photo_set.attrib['total'], "photos in set")
        pages = int(photo_set.attrib['pages'])
        print("Processing page", page, "of", pages)
        total = str(len(photo_set))

        for i, photo in enumerate(photo_set):
            if args.number:
                number = str(page-1) + str(i + 1).zfill(len(total))
            photo_id = photo.attrib['id']
            photo_info = flickr.photos_getInfo(photo_id=photo_id)
            photo_info = photo_info[0]
            secret = photo_info.attrib['secret']
            oSecret = photo_info.attrib['originalsecret']
            if args.title:
                photo_title = photo.attrib['title']
            else:
                photo_title = None

            if args.size == "o":
                flickr_utils.download(
                    "http://farm%s.static.flickr.com/%s/%s_%s_o.jpg" %
                    (photo.attrib['farm'], photo.attrib['server'],
                        photo.attrib['id'], oSecret),
                    photo_title, args.noclobber, number)
            else:
                flickr_utils.download(
                    "http://farm%s.static.flickr.com/%s/%s_%s_%s.jpg" %
                    (photo.attrib['farm'], photo.attrib['server'],
                        photo.attrib['id'], secret, args.size),
                    photo_title, args.noclobber, number)

# End of file
