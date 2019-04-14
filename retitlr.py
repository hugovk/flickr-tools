#!/usr/bin/env python3
# coding=utf-8
"""
Retitle photos
"""
import argparse
import flickrapi  # http://www.stuvel.eu/flickrapi
import os
import sys

# import xml.etree.ElementTree as ET  # ET.dump(some xml object)


def retitle(photo_id, info):
    title = info.getchildren()[0].find("title").text
    if title:
        print(title)
        if args.search in title:
            print("\tMatch!")
            new_title = title.replace(args.search, args.replace)
            print(new_title)
            if not args.test:
                flickr.photos.setMeta(photo_id=photo_id, title=new_title)
                print("\tRenamed!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Retitle photos.")
    parser.add_argument(
        "-x",
        "--test",
        action="store_true",
        help="Test mode: go through the motions but don't add any tags",
    )
    parser.add_argument("search", help="Text to search for")
    parser.add_argument("replace", help="Text to replace with")
    parser.add_argument("-b", "--begin", type=int, default=1, help="Photo to begin at")
    parser.add_argument(
        "-n",
        "--number",
        type=int,
        help="Number of photos to process. If left blank, keep going",
    )
    parser.add_argument(
        "-k",
        "--api-key",
        help="Flickr API key. "
        "If not given, looks in FLICKR_API_KEY environment variable",
    )
    parser.add_argument(
        "-s",
        "--api-secret",
        help="Flickr API secret. "
        "If not given, looks in FLICKR_SECRET environment variable",
    )
    args = parser.parse_args()

    try:
        import timing  # optional

        assert timing  # silence warnings
    except ImportError:
        pass

    if not args.api_key:
        args.api_key = os.environ["FLICKR_API_KEY"]
    if not args.api_secret:
        args.api_secret = os.environ["FLICKR_SECRET"]
    flickr = flickrapi.FlickrAPI(args.api_key, args.api_secret)

    try:
        flickr.authenticate_via_browser(perms="write")
    except flickrapi.exceptions.FlickrError:
        (token, frob) = flickr.get_token_part_one(perms="write")
        if not token:
            input("Press ENTER after you authorised this program")
        flickr.get_token_part_two((token, frob))

    # Get all my photos
    photos = []
    print("Getting photos")
    count, processed = 0, 0
    for photo in flickr.walk(tag_mode="all", user_id="me", text=args.search):
        photo_id = photo.get("id")
        count += 1
        if count < args.begin:
            continue
        processed += 1
        if args.number and processed > args.number:
            print(str(args.number) + " photos processed, exiting")
            sys.exit()

        print("\nProcessing photo", count, ":", photo_id)

        try:
            info = flickr.photos_getInfo(photo_id=photo_id)
        except KeyboardInterrupt:
            print("Keyboard interrupt")
            raise
        except Exception:
            print("  Error getting photo info:", sys.exc_info())
            print("  Skipping")
            continue

        # Skip those that aren't mine
        owner = info.getchildren()[0].find("owner").attrib["username"]
        if owner != "hugovk":
            print("  Not mine, skipping")
            continue

        retitle(photo_id, info)

# End of file
