#!/usr/bin/python
"""
Download random photos from your account
Based on flickr_set_downloadr.py
Based on http://pastebin.com/JEJiCNRd
"""
import argparse
import os
import random
import sys
# import xml.etree.ElementTree as ET

import flickrapi
import flickr_utils

api_key = os.environ['FLICKR_API_KEY']
api_secret = os.environ['FLICKR_SECRET']


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Download random photos from your account',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "-u", "--username", default="example",
        help="The username to download from.")
    parser.add_argument(
        "-n", "--number", type=int, default=10,
        help="Number of photos to download")

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
    args = parser.parse_args()

    # Optional, http://stackoverflow.com/a/1557906/724176
    try:
        import timing
    except:
        None

    flickr = flickrapi.FlickrAPI(api_key, api_secret)
    flickr.authenticate_via_browser(perms='read')

    # Get ugly ID from nice ID
    user_nsid = flickr.people_findByUsername(username=args.username)
    user_nsid = user_nsid.getchildren()[0].attrib['nsid']
    print "Username:", args.username
    print "User NSID:", user_nsid

    # Find how many photos they have
    person_info = flickr.people_getInfo(user_id=user_nsid)
    number_of_photos = person_info.getchildren()[0].find(
        'photos').find('count').text
    print "User has", number_of_photos, "photos"
    if int(number_of_photos) == 0:
        sys.exit()

    random_photos = []
    for i in range(args.number):
        # Endpoints included:
        print i, number_of_photos
        random_integer = random.randint(1, int(number_of_photos))
        print "Random tractor:", random_integer

        # If you ask for a page higher than 10,000,
        # the API just returns page 10,000
        if random_integer <= 10000:
#             Use pages of 1
            photo_page = flickr.people_getPublicPhotos(
                user_id=user_nsid, per_page=1, page=random_integer)
            photo = photo_page.getchildren()[0].find('photo')
        else:
            # Use pages of 500, the maximum
            page, offset = divmod(random_integer, 500)
            photo_page = flickr.people_getPublicPhotos(
                user_id=user_nsid, per_page=500, page=page)
            photo = photo_page.getchildren()[0][offset]

        random_photos.append(photo)

    # TODO? Some photos may not be found for some reason (private, etc),
    # so instead could have a while until the required number have
    # been actually downloaded.
    for photo in random_photos:
        url = flickr_utils.photo_url(photo, args.size)

        if args.title:
            photo_title = photo.attrib['title']
        else:
            photo_title = None

        flickr_utils.download(url, photo_title, args.noclobber)

# End of file
