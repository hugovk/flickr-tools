#!/usr/bin/env python3
# coding=utf-8
"""
Add non-free photos to an album based.
"""
from __future__ import print_function, unicode_literals
import argparse
import flickrapi  # http://www.stuvel.eu/flickrapi
import os
import sys

import xml.etree.ElementTree as ET  # ET.dump()

# from pprint import pprint

# https://www.flickr.com/services/api/flickr.photos.licenses.getInfo.html
LICENSE_All_Rights_Reserved = 0
LICENSE_Attribution_NonCommercial_ShareAlike_License = 1
LICENSE_Attribution_NonCommercial_License = 2
LICENSE_Attribution_NonCommercial_NoDerivs_License = 3
LICENSE_Attribution_License = 4
LICENSE_Attribution_ShareAlike_License = 5
LICENSE_Attribution_NoDerivs_License = 6
LICENSE_No_known_copyright_restrictions = 7
LICENSE_United_States_Government_Work = 8
LICENSE_Public_Domain_Dedication_CC0 = 9
LICENSE_Public_Domain_Mark = 10


# cmd.exe cannot do Unicode so encode first
def print_it(text):
    if os.name == "nt":
        print(text.encode("utf-8"))
    else:
        print(text)


def create_and_add_to_set(flickr, photo_id):
    print("  Create and add to set")
    if not args.test:
        try:
            rsp = flickr.photosets_create(title="Non-free", primary_photo_id=photo_id)
            set_id = rsp.find("photoset").get("id")
            print("    Set created and photo added: ", set_id)

        except flickrapi.FlickrError:
            error = str(sys.exc_info()[1])
            print("    Flickr", error)
        #             if error == "Error: 4: Photo in maximum number of pools":
        #                 print("      Skip photo")
        #                 # Don't bother checking this photo any more
        #                 continue
        #             elif error == "Error: 5: Photo limit reached":
        #                 # Don't bother checking this group again
        #                 print("      Skip group until next time")
        #                 del MAPPINGS[i]

        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            error = str(sys.exc_info()[1])
            print("    Error", error)
    return set_id


def add_to_set(flickr, photo_id, set_id):
    # Add to set
    print("  Add to set")
    added = 0
    if not args.test:
        try:
            flickr.photosets_addPhoto(photo_id=photo_id, photoset_id=set_id)
            print("    Photo added")
            added += 1

        except flickrapi.FlickrError:
            error = str(sys.exc_info()[1])
            print("    Flickr", error)
        #             if error == "Error: 4: Photo in maximum number of pools":
        #                 print("      Skip photo")
        #                 # Don't bother checking this photo any more
        #                 continue
        #             elif error == "Error: 5: Photo limit reached":
        #                 # Don't bother checking this group again
        #                 print("      Skip group until next time")
        #                 del MAPPINGS[i]

        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            error = str(sys.exc_info()[1])
            print("    Error", error)
    return added


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="This script adds photos to sets/albums.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    # parser.add_argument(
    #     "-nf",
    #     "--non-free",
    #     action="store_true",
    #     help="Only show all-rights reserved",
    # )
    parser.add_argument(
        "-n",
        "--number",
        type=int,
        # default=20,
        help="Number of photos to process. If left blank, keep going",
    )
    parser.add_argument("-b", "--begin", type=int, default=1, help="Photo to begin at")
    parser.add_argument("-t", "--tags", help="Process images with these tags")
    sort_options = [
        "date-posted-asc",
        "date-posted-desc",
        "date-taken-asc",
        "date-taken-desc",
        "interestingness-desc",
        "interestingness-asc",
        "relevance",
    ]
    parser.add_argument(
        "-s",
        "--sort",
        default="date-posted-desc",  # most recent
        choices=sort_options,
        help="The order in which to process photos",
    )
    parser.add_argument(
        "-x",
        "--test",
        action="store_true",
        help="Test mode: go through the motions but don't add any tags",
    )
    parser.add_argument(
        "-i",
        "--info",
        action="store_true",
        help="Show information about my sets and exit",
    )
    args = parser.parse_args()

    try:
        import timing  # optional

        assert timing  # avoid warnings
    except ImportError:
        pass

    api_key = os.environ["FLICKR_API_KEY"]
    api_secret = os.environ["FLICKR_SECRET"]
    flickr = flickrapi.FlickrAPI(api_key, api_secret)

    try:
        flickr.authenticate_via_browser(perms="write")
    except flickrapi.exceptions.FlickrError:
        (token, frob) = flickr.get_token_part_one(perms="write")
        if not token:
            input("Press ENTER after you authorised this program")
        flickr.get_token_part_two((token, frob))

    my_nsid = flickr.people_findByUsername(username="hugovk")
    my_nsid = my_nsid.getchildren()[0].attrib["nsid"]
    print("My NSID:", my_nsid)
    set_resp = flickr.photosets_getList(user_id=my_nsid)
    sets_resp = set_resp.getchildren()[0].getchildren()
    sets = {}

    if args.info:
        print("My sets:")
        print("NSID\tName")
        for set in sets_resp:
            set_id = set.attrib["id"]
            set_name = set.find("title").text
            print("{}\t{}".format(set_id, set_name))

        sys.exit()

    non_free_set_id = None
    for set in sets_resp:
        set_id = set.attrib["id"]
        set_name = set.find("title").text
        # print("{}\t{}".format(set_id, set_name))
        if set_name == "Non-free":
            print("Non-free album ID: ", set_id)
            non_free_set_id = set_id
            break

    if not non_free_set_id:
        print("Non-free album doesn't exist, will create if needed")

    number, processed, added = 0, 0, 0
    try:
        for photo in flickr.walk(
            tag_mode="all",
            privacy_filter="1",  # public
            user_id="me",
            sort=args.sort,
            tags=args.tags,
            extras="license",
        ):
            number += 1
            if number < args.begin:
                continue
            processed += 1
            if args.number and processed > args.number:
                print(added, "additions to sets")
                sys.exit(str(args.number) + " photos processed, exiting")
            photo_id = photo.get("id")
            photo_title = photo.attrib["title"]
            photo_title_lower = photo_title.lower()
            license = int(photo.get("license"))
            if license >= 1:
                # Has a free license, skip
                continue

            try:
                photo_info = flickr.photos_getInfo(photo_id=photo_id)
            except (KeyboardInterrupt, SystemExit):
                raise
            except:
                # Let's just skip this photo then
                continue

            # Skip those that aren't mine
            owner = photo_info.getchildren()[0].find("owner").attrib["username"]
            if owner != "hugovk":
                print(
                    "\n"
                    + str(processed)
                    + ") Photo "
                    + photo_id
                    + " not mine, skipping"
                )
                continue

            print_it(photo_title)
            if not non_free_set_id:
                non_free_set_id = create_and_add_to_set(flickr, photo_id)
                added += 1
            else:
                added += add_to_set(flickr, photo_id, non_free_set_id)

    except KeyboardInterrupt:
        print("Keyboard interrupt")

    print(added, "additions to sets")

    # TODO reorder photos in set

# End of file
