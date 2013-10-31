#!/usr/bin/python

""" 
Flickr set downloader
Based on http://pastebin.com/JEJiCNRd
"""
import argparse
import os
import sys
import urllib2
import xml.etree.ElementTree as ET

import flickrapi

api_key = os.environ['FLICKR_API_KEY']
api_secret = os.environ['FLICKR_SECRET']

def download(url, title, number):
    if title:
        file_name = title + ".jpg"
        file_name = "".join(c for c in file_name if c.isalnum() or c in [' ', '.']).rstrip() # make Windows-safe
    else:
        file_name = url.split('/')[-1]

    if args.number:
        file_name = number + "-" + file_name

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
    parser.add_argument("setid", help="The Set ID for the set to download.")
    parser.add_argument("-s" , "--size", default="b", choices=("s", "q", "t", "m", "n", "z", "c", "b", "o"), help="The size of photo you want to download. Size must fit the following: s - 75x75, q - 150x150, t - 100 on the longest side, m - 240 on the longest side, n - 320 on the longest side, z - 640 on the longest side, c - 800 on the longest side, \nb - 1024 on the longest side (default), o - original")
    parser.add_argument("-t" , "--title", action="store_true", help="Use the title as the filename (TODO ensure title is filesystem-safe)")
    parser.add_argument("-nc" , "--noclobber", action="store_true", help="Don't clobber pre-exisiting files")
    parser.add_argument("-n" , "--number", action="store_true", help="Prefix filenames with a serial number")
    args = parser.parse_args()

    try: import timing # Optional, http://stackoverflow.com/a/1557906/724176
    except: None

    if args.setid is None:
        sys.exit("You must specify a photo set to download. \nUse -h for examples.")

    flickr = flickrapi.FlickrAPI(api_key, api_secret)
    (token, frob) = flickr.get_token_part_one(perms='write')
    if not token: raw_input("Press ENTER after you authorized this program")
    flickr.get_token_part_two((token, frob))

    photo_set = flickr.photosets_getPhotos(photoset_id=args.setid)
    photo_set = photo_set[0]
    total = str(len(photo_set))
    print total, "photos in set"

    for i, photo in enumerate(photo_set):
        number = str(i + 1).zfill(len(total))
        photo_id = photo.attrib['id']
        photo_info = flickr.photos_getInfo(photo_id=photo_id)
        photo_info = photo_info[0]
        secret=photo_info.attrib['secret']
        oSecret=photo_info.attrib['originalsecret']
        if args.title:
            photo_title = photo.attrib['title']
        else:
            photo_title = None
            
        if args.size == "o":
            download("http://farm%s.static.flickr.com/%s/%s_%s_o.jpg" % (photo.attrib['farm'], photo.attrib['server'], photo.attrib['id'],oSecret), 
            photo_title, number)
        else:
            download("http://farm%s.static.flickr.com/%s/%s_%s_%s.jpg" % (photo.attrib['farm'], photo.attrib['server'], photo.attrib['id'], 
            secret, args.size), photo_title, number)

# End of file
