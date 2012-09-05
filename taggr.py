import argparse
import flickrapi # http://www.stuvel.eu/flickrapi
import os
import sys
import time

try: import timing # optional
except: pass

# Command-line Python script to add machine tags on Flickr from EXIF data.

# Initial version based on Paul Mison's EXIF machine tagger Perl script, but without the database:
# http://blech.typepad.com/blog/2008/11/flickr-exif-machine-tags.html
# http://husk.org/code/flickr_exif_machinetag.pl

wanted_labels = ["Aperture",
                "Exposure",
                "Exposure Bias",
                "Flash",
                "Focal Length",
                "ISO Speed",
                "Make",
                "Model",
                "Orientation"]

def get_photo_tags(photo_info):
    """Return a list of tags from a photo's info"""
    tags = []
    for tag in info.getchildren()[0].find('tags'):
        tags.append(tag.text)
    return tags

def photo_has_partial_tag(tag_to_find, tags):
    """Return true if the desired text is found within any tag"""
    for tag in tags:
        if tag_to_find in tag:
            return True
    return False

def set_machine_tags(photo_id):
    """Get the EXIF from Flickr, generate some machine tags and add them to the photo"""

    # Get EXIF from Flickr
    exif = flickr.photos_getExif(photo_id = photo_id)
    exif_tags = exif.getchildren()[0].getchildren()
    make, model = "",""
    machine_tags = []
    for exif_tag in exif_tags:
        predicate = exif_tag.attrib['label']
        if predicate in wanted_labels:
            namespace = "exif"
            predicate = predicate.replace(" ", "_")
            value = exif_tag[0].text

            if predicate == "Make" or predicate == "Model":
                namespace = "camera"

            machine_tag = '"' + namespace + ':' + predicate + '=' + value + '"'
            print "Got tag:", machine_tag
            machine_tags.append(machine_tag)

    epoch_seconds = str(int(time.time()))
    if machine_tags:
        print "  Got", len(machine_tags), "exif tags for", photo_id
        machine_tags.append("meta:exif=" + epoch_seconds)
    else:
        print "  Got no exif tags for", photo_id
        machine_tags.append("meta:exif=" + epoch_seconds)
    machine_tag_string = " ".join(machine_tags)

    # Finally, do tagging
    if not args.test:
        try:
            flickr.photos_addTags(
                    photo_id = photo_id,
                    tags = machine_tag_string)
        except flickrapi.FlickrError:
            print "Flickr error:", sys.exc_info()[0]
            # Move on to the next photo
            return

    print "  Set", len(machine_tags), "machine tags for", photo_id

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Machine tag photos from EXIF.")
    parser.add_argument('-x', '--test', action='store_true',
        help="Test mode: go through the motions but don't add any tags")
    args = parser.parse_args()

    api_key = os.environ['FLICKR_API_KEY']
    api_secret = os.environ['FLICKR_SECRET']
    flickr = flickrapi.FlickrAPI(api_key, api_secret)
    (token, frob) = flickr.get_token_part_one(perms='write')
    if not token: raw_input("Press ENTER after you authorised this program")
    flickr.get_token_part_two((token, frob))

    # Get all my photos
    photos = []
    print "Getting photos"
    count = 0
    for photo in flickr.walk(tag_mode = 'all',
            user_id = 'me'):
        photo_id = photo.get('id')
        info = flickr.photos_getInfo(photo_id = photo_id)
        count+=1
        print "\nProcessing photo", count, ":", photo_id #, photo.get('title')

        # Skip those previously processed
        flickr_tags = get_photo_tags(info)
        if photo_has_partial_tag("meta:exif=", flickr_tags):
            print "  Previously processed, skipping"
        else:
            set_machine_tags(photo_id)

# End of file
