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
import urllib2
import xml.etree.ElementTree as ET

import flickrapi

api_key = os.environ['FLICKR_API_KEY']
api_secret = os.environ['FLICKR_SECRET']

def download(url, title):
    print url
    if title:
        file_name = title + ".jpg"
        file_name = "".join(c for c in file_name if c.isalnum() or c in [' ', '.']).rstrip() # make Windows-safe
    else:
        file_name = url.split('/')[-1]

    if args.noclobber and os.path.exists(file_name):
        print "File already exists, skipping:", file_name
        return
    
    u = urllib2.urlopen(url)
    f = open(file_name, 'wb')
    meta = u.info()
    file_size = int(meta.getheaders("Content-Length")[0])
    print "Downloading: %s Bytes: %s" % (file_name, file_size)

    file_size_dl = 0
    block_sz = 8192
    while True:
        buffer = u.read(block_sz)
        if not buffer:
            break

        file_size_dl += len(buffer)
        f.write(buffer)
        status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
        status = status + chr(8)*(len(status)+1)
        print status,

    f.close()
    return

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download a Flickr set', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-u", "--username", help="The username to download from.", 
        default="example")
    parser.add_argument("-n", "--number", help="Number of photos to download", 
        type=int, default=10)
    
    parser.add_argument("-s" , "--size", default="b", choices=("s", "q", "t", "m", "n", "z", "c", "b", "o"), help="The size of photo you want to download. Size must fit the following: s - 75x75, q - 150x150, t - 100 on the longest side, m - 240 on the longest side, n - 320 on the longest side, z - 640 on the longest side, c - 800 on the longest side, \nb - 1024 on the longest side (default), o - original")
    parser.add_argument("-t" , "--title", action="store_true", help="Use the title as the filename (TODO ensure title is filesystem-safe)")
    parser.add_argument("-nc" , "--noclobber", action="store_true", help="Don't clobber pre-exisiting files")
    args = parser.parse_args()

    try: import timing # Optional, http://stackoverflow.com/a/1557906/724176
    except: None

    flickr = flickrapi.FlickrAPI(api_key, api_secret)
    (token, frob) = flickr.get_token_part_one(perms='write')
    if not token: raw_input("Press ENTER after you authorized this program")
    flickr.get_token_part_two((token, frob))

    # Get ugly ID from nice ID
    user_nsid = flickr.people_findByUsername(username = args.username)
    user_nsid = user_nsid.getchildren()[0].attrib['nsid']
    print "Username:", args.username
    print "User NSID:", user_nsid

    # Find how many photos they have
    person_info = flickr.people_getInfo(user_id=user_nsid)
    number_of_photos = person_info.getchildren()[0].find('photos').find('count').text
    print "User has", number_of_photos, "photos"

    random_photos = []
    for i in range(args.number):
        random_integer = random.randint(1, int(number_of_photos))  # endpoints included
        print "Random tractor:", random_integer
    
        # If you ask for a page higher than 10,000, the API just returns page 10,000
        if random_integer <= 10000:
#             Use pages of 1
            photo_page = flickr.people_getPublicPhotos(user_id=user_nsid, per_page=1, page=random_integer)
            photo = photo_page.getchildren()[0].find('photo')
        else:
            # Use pages of 500, the maximum
            page, offset = divmod(random_integer, 500)
            photo_page = flickr.people_getPublicPhotos(user_id=user_nsid, per_page=500, page=page)
            photo = photo_page.getchildren()[0][offset]

        random_photos.append(photo)

    # TODO? Some photos may not be found for some reason (private, etc), so instead could have a while until the required number have been actually downloaded.
    for photo in random_photos:
        secret=photo.attrib['secret']
        photo_id = photo.attrib['id']
        if args.title:
            photo_title = photo.attrib['title']
        else:
            photo_title = None
        
        if args.size == "o":
            # Need an extra API call to get the originalsecret
            photo_info = flickr.photos_getInfo(photo_id=photo_id)
            photo_info = photo_info[0]
            oSecret=photo_info.attrib['originalsecret']
            download("http://farm%s.static.flickr.com/%s/%s_%s_o.jpg" % (photo.attrib['farm'], photo.attrib['server'], photo.attrib['id'], oSecret), photo_title)
        else:
            download("http://farm%s.static.flickr.com/%s/%s_%s_%s.jpg" % (photo.attrib['farm'], photo.attrib['server'], photo.attrib['id'], secret, args.size), photo_title)

# End of file
