import argparse
import flickrapi # http://www.stuvel.eu/flickrapi
import os
import sys
import time
import xml.etree.ElementTree as ET

try: import timing # optional
except: pass

# This script adds my favourites to a set.
#

def print_it(text):
    print text.encode('utf-8')

def get_faves_set_id():
    response = flickr.photosets_getList()
    photosets = response.getchildren()[0]
    for photoset in photosets:
        title = photoset.getchildren()[0].text
        if title == args.title:
            print "  Favourites set already exists"
            id = photoset.attrib['id']
            # print "ID:         ", id
            # print "Title:      ", title
            description = photoset.getchildren()[1].text
            # if description: print "Description:", description
            return id
    print "  Favourites set not found, needs creating"
    return None
  
def generate_description():
    timestamp = time.strftime('%d %B %Y')
    description = "Set automatically generated on " + timestamp + " by https://github.com/hugovk/flickr-tools/blob/master/favr.py"
    return description
  
def create_faves_set(photo_id, faves_set_id):
    try:
        response = flickr.photosets_create(title = args.title, description = generate_description(), primary_photo_id = photo_id)
    except flickrapi.FlickrError:
        print "  Flickr", str(sys.exc_info()[1])

def add_to_faves_set(photo_id, faves_set_id):
    if faves_set_id == None:
        faves_set_id = get_faves_set_id()
        if faves_set_id == None:
            faves_set_id = create_faves_set(photo_id, faves_set_id)
        else: # update description
            try:
                flickr.photosets_editMeta(photoset_id = faves_set_id, title = args.title, description = generate_description())
            except flickrapi.FlickrError:
                error = str(sys.exc_info()[1])
                print "  Flickr", error
    
    try:
        flickr.photosets_addPhoto(photoset_id = faves_set_id, photo_id = photo_id)
    except flickrapi.FlickrError:
        error = str(sys.exc_info()[1])
        print "  Flickr", error

    return faves_set_id

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a set containing your photos that others marked favourite.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-t', '--title', default="Your favourites",
        help="Title for the set of your most favoured photos")
    parser.add_argument('-l', '--limit', default=81,
        help="How many photos to add to the set")
    args = parser.parse_args()
    
    api_key = unicode(os.environ['FLICKR_API_KEY'])
    api_secret = unicode(os.environ['FLICKR_SECRET'])
    flickr = flickrapi.FlickrAPI(api_key, api_secret)
    (token, frob) = flickr.get_token_part_one(perms='write')
    if not token: raw_input("Press ENTER after you authorised this program")
    flickr.get_token_part_two((token, frob))

    added = 0
    faves_set_id = None
    
    faves = flickr.stats_getPopularPhotos(sort = 'favorites', per_page = args.limit).getchildren()[0]
    print "Photo ID\tFaves\tTitle"
    for fave in faves:
        photo_id = fave.get('id')
        print_it(photo_id + "\t" + fave.find('stats').get('favorites') + "*\t" + fave.get('title'))
        faves_set_id = add_to_faves_set(photo_id, faves_set_id)
        added += 1

    print added, "additions to the set"
    print "Done."
    
# End of file
