#!/usr/bin/env python3
import argparse
import flickrapi  # http://www.stuvel.eu/flickrapi
import os
import re
import sys
import time

# import xml.etree.ElementTree as ET  # ET.dump(some xml object)

# This script adds tags to Flickr.
#
# * EXIF tags as machine tags:
#   * namespace:predicate:value
#
# * EXIF tags as standard tags:
#   * EXIF camera tags -> "make model" make model
#   * EXIF date -> YYYY Month season
#
# * Standard tag expansions:
#   * e.g. bike -> bicycle cycle polkupyörä fillari
#   * e.g. Helsinki -> Helsingfors, Uusimaa, Nyland, Finland, Suomi
#
# * Metadata as standard tags:
#   * title "title" description "description"
#
# Initial version based on Paul Mison's EXIF machine tagger Perl script,
# but without the database:
# http://blech.typepad.com/blog/2008/11/flickr-exif-machine-tags.html
# http://husk.org/code/flickr_exif_machinetag.pl

# TODO?
#
# * EXIF tags as standard tags:
#   * geolookup -> city region country [continent?]
#
# * EXIF tags as machine tags:
#   * geolookup -> city region country [continent?]
#
# * Maybe in another script:
#   * flickr.groups.pools.add

wanted_labels = [
    "Aperture",
    "Exposure",
    "Exposure Bias",
    "Flash",
    "Focal Length",
    "ISO Speed",
    "Make",
    "Model",
    "Orientation",
]

# TODO change this to your own username, for example
ALWAYS_TAGS = ["hvk", "hugovk"]

# If the first one exists, add the others
EXPANDABLES = [
    ["Helsinki", ["Helsingfors", "Uusimaa", "Nyland", "Finland", "Suomi"]],
    [
        "HEL",
        [
            "Helsingfors",
            "Uusimaa",
            "Nyland",
            "Finland",
            "Suomi",
            "airport",
            "lentoasema",
            "Helsinki-Vantaa airport",
        ],
    ],
    ["wintercycling", ["bicycle", "cycle", "polkupyörä", "fillari", "cycling", "bike"]],
    ["bikehack", ["bicycle", "cycle", "polkupyörä", "fillari", "cycling", "hack"]],
    ["bike", ["bicycle", "cycle", "polkupyörä", "fillari", "cycling"]],
]


def get_photo_tags(photo_info):
    """Return a list of tags from a photo's info"""
    tags = []
    for tag in photo_info.getchildren()[0].find("tags"):
        tags.append(tag.text)
    return tags


def photo_has_partial_tag(tag_to_find, tags):
    """Return true if the desired text is found within any tag"""
    for tag in tags:
        if tag_to_find in tag:
            return True
    return False


def set_flickr_tags(photo_id, new_tags, old_tags):
    """Sets a string of tags to a given photo on Flickr"""

    # Remove any duplicates
    # TODO case-insensitive
    new_tags = uniquify(new_tags)

    # No need to add a tag if it's already on Flickr
    fresh_tags = []
    for tag in new_tags:
        if not string_in_list(tag, old_tags):
            fresh_tags.append(tag)

    if fresh_tags:
        tag_string = " ".join(fresh_tags)
        if not args.test:
            try:
                flickr.photos_addTags(photo_id=photo_id, tags=tag_string)
            except flickrapi.FlickrError:
                print("Flickr error:", sys.exc_info()[0])
                # Move on to the next photo
            except Exception:
                pass
        s = "s" if len(fresh_tags) > 1 else ""
        print(f"  Set {len(fresh_tags)} tag{s} for {photo_id}: {tag_string}")


def set_machine_tags(photo_id):
    """
    Get the EXIF from Flickr, generate some
    machine tags and add them to the photo
    """

    # Get EXIF from Flickr
    make, model, timestring = "", "", ""
    try:
        exif = flickr.photos_getExif(photo_id=photo_id)
    except Exception:
        return make, model, timestring
    exif_tags = exif.getchildren()[0].getchildren()
    machine_tags = []
    for exif_tag in exif_tags:
        predicate = exif_tag.attrib["label"]
        if predicate == "Date and Time (Original)":
            timestring = exif_tag[0].text
        if predicate in wanted_labels:
            namespace = "exif"
            predicate = predicate.replace(" ", "_")
            value = exif_tag[0].text
            # print(exif_tag.attrib['label'], exif_tag.attrib['tag'])

            if predicate == "Make" or predicate == "Model":
                namespace = "camera"
                if predicate == "Make":
                    value = value.title()
                    make = value
                elif predicate == "Model":
                    model = value

            machine_tag = f'"{namespace}:{predicate}={value}"'
            print("Got tag:", machine_tag)
            machine_tags.append(machine_tag)

    epoch_seconds = str(int(time.time()))
    if machine_tags:
        print(f"  Got {len(machine_tags)} exif tags for {photo_id}")
        machine_tags.append("meta:exif=" + epoch_seconds)
    else:
        print(f"  Got no exif tags for {photo_id}")
        machine_tags.append("meta:exif=none")

    set_flickr_tags(photo_id, machine_tags, flickr_tags)

    return make, model, timestring


def get_make_model_strings(make, model):
    """Given a make and a model, return a list of [make, model, make model]"""
    camera_tags = []
    if make:
        camera_tags.append(make)
    if model:
        camera_tags.append(f'"{model}"')
    if make and model:
        camera_tags.append(f'"{make} {model}"')
    return camera_tags


def uniquify(seq):
    # Doesn't preserve order
    return {}.fromkeys(seq).keys()


def string_in_list(my_string, things):
    """Check if string is in list, ignore case, hyphens, spaces and quotes"""
    return re.sub(r"[- ]", "", my_string).lower() in (thing.lower() for thing in things)


def expand_tags(tag_to_find, expanded_tags, source_tags, result_tags):
    """
    Expand tag to a list of expanded tags.
    For example, expand 'Helsinki' to 'Helsingfors', 'Finland', 'Suomi'
    """
    if string_in_list(tag_to_find, source_tags):
        for tag in expanded_tags:
            if not string_in_list(tag, source_tags):
                result_tags.append(tag)


def set_standard_tags(photo_id, make, model, timestring, flickr_tags):
    """Generate some normal tags and add them to the photo"""

    # Set some extra standard tags
    normal_tags = ALWAYS_TAGS + get_make_model_strings(make, model)

    # Special cases
    if make.lower() in ["nokia", "samsung"]:
        normal_tags.append("cameraphone")

    if model == "N8-00" or model == "808 PureView":
        normal_tags.append('"Carl Zeiss"')

    if model == "N8-00":
        model = "N8"
        new_tags = get_make_model_strings(make, model)
        normal_tags = normal_tags + new_tags

    if model == "SM-G950F":
        new_tags = get_make_model_strings(make, model)
        normal_tags = normal_tags + new_tags
        model = "S8"
        new_tags = get_make_model_strings(make, model)
        normal_tags = normal_tags + new_tags
        model = "Galaxy S8"
        new_tags = get_make_model_strings(make, model)
        normal_tags = normal_tags + new_tags

    if model == "SM-S901B":
        new_tags = get_make_model_strings(make, model)
        normal_tags = normal_tags + new_tags
        model = "S22"
        new_tags = get_make_model_strings(make, model)
        normal_tags = normal_tags + new_tags
        model = "Galaxy S22"
        new_tags = get_make_model_strings(make, model)
        normal_tags = normal_tags + new_tags

    # Tag expansions
    for expandable in EXPANDABLES:
        expand_tags(expandable[0], expandable[1], flickr_tags, normal_tags)

    set_flickr_tags(photo_id, normal_tags, flickr_tags)

    # Time-based tags
    if timestring:
        timestamp = time.strptime(timestring, "%Y:%m:%d %H:%M:%S")
        time_tags = [str(timestamp.tm_year), time.strftime("%B", timestamp)]

        # WARNING!
        # Works only in the northern hemisphere and assumes clockwork seasons!
        if 0 <= timestamp.tm_mon <= 2:
            time_tags.extend(["winter", "talvi"])
        elif 3 <= timestamp.tm_mon <= 5:
            time_tags.extend(["spring", "kevät"])
        elif 6 <= timestamp.tm_mon <= 8:
            time_tags.extend(["summer", "kesä"])
        elif 9 <= timestamp.tm_mon <= 11:
            time_tags.extend(["autumn", "syksy"])
        elif 12 <= timestamp.tm_mon:
            time_tags.extend(["winter", "talvi"])
        set_flickr_tags(photo_id, time_tags, flickr_tags)


def set_title_desc_tags(photo_id, info, flickr_tags):
    title = info.getchildren()[0].find("title").text
    new_tags = []
    if title:
        if "," in title:  # Remove commas
            title = title.replace(",", "")
            new_tags.append(title)
        new_tags.append(title)
        if " " in title:
            new_tags.append(f'"{title}"')
    if new_tags:
        set_flickr_tags(photo_id, new_tags, flickr_tags)

    if args.description:
        new_tags = []
        description = info.getchildren()[0].find("description").text
        if description:
            new_tags.append(description)
            if "," in description:
                new_tags.append(description.replace(",", ""))  # Remove commas
            if " " in description:
                new_tags.append(f'"{description}"')
        if new_tags:
            set_flickr_tags(photo_id, new_tags, flickr_tags)


def find_location(text, location):
    value = location.find(text)
    if value is not None:
        return value.text
    else:
        return None


def set_geo_tags(photo_id, flickr_tags):
    try:
        location = flickr.photos_geo_getLocation(photo_id=photo_id)
    except flickrapi.FlickrError:
        print("Flickr error:", sys.exc_info()[0])
        return
    except Exception:
        print("Error:", sys.exc_info()[0])
        return

    if location is None:
        return
    location = location.getchildren()[0].getchildren()[0]

    neighbourhood = find_location("neighbourhood", location)
    locality = find_location("locality", location)
    county = find_location("county", location)
    region = find_location("region", location)
    country = find_location("country", location)

    new_tags = []
    for tag in [neighbourhood, locality, county, region, country]:
        if tag:
            new_tags.append('"' + tag + '"')

    namespace = "geo"
    if neighbourhood:
        new_tags.append(f'"{namespace}:neighbourhood={neighbourhood}"')
    if locality:
        new_tags.append(f'"{namespace}:locality={locality}"')
    if county:
        new_tags.append(f'"{namespace}:county={county}"')
    if region:
        new_tags.append(f'"{namespace}:region={region}"')
    if country:
        new_tags.append(f'"{namespace}:country={country}"')

    if new_tags:
        set_flickr_tags(photo_id, new_tags, flickr_tags)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Machine tag photos from EXIF.")
    parser.color = True
    parser.add_argument(
        "-x",
        "--test",
        action="store_true",
        help="Test mode: go through the motions but don't add any tags",
    )
    parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        help="Process all, regardless of previous processing",
    )
    parser.add_argument("-b", "--begin", type=int, default=1, help="Photo to begin at")
    parser.add_argument(
        "-n",
        "--number",
        type=int,
        help="Number of photos to process. If left blank, keep going",
    )
    parser.add_argument(
        "-d", "--description", action="store_true", help="Include description as tags"
    )
    parser.add_argument(
        "-j",
        "--jatkuu",
        action="store_true",
        help="When reaching a previously processed photo, "
        "continue to the next instead of exiting",
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
            raw_input("Press ENTER after you authorised this program")
        flickr.get_token_part_two((token, frob))

    # Get all my photos
    photos = []
    print("Getting photos")
    count, processed = 0, 0
    for photo in flickr.walk(tag_mode="all", user_id="me"):
        # tags = "hvk"):
        photo_id = photo.get("id")
        count += 1
        if count < args.begin:
            continue
        processed += 1
        if args.number and processed > args.number:
            print(f"{args.number} photos processed, exiting")
            sys.exit()

        print(f"\nProcessing photo {count}: {photo_id}")

        try:
            info = flickr.photos_getInfo(photo_id=photo_id)
        except KeyboardInterrupt:
            print("Keyboard interrupt")
            raise
        except Exception:
            print(f"  Error getting photo info: {sys.exc_info()}")
            print("  Skipping")
            continue

        # Skip those that aren't mine
        owner = info.getchildren()[0].find("owner").attrib["username"]
        if owner != "hugovk":
            print("  Not mine, skipping")
            continue

        flickr_tags = get_photo_tags(info)
        if not args.all:
            # Skip those previously processed
            if photo_has_partial_tag("meta:exif=", flickr_tags):
                if not args.jatkuu:
                    print("  Previously processed, exiting")
                    sys.exit()
                print("  Previously processed, skipping")
                continue

        set_title_desc_tags(photo_id, info, flickr_tags)
        set_geo_tags(photo_id, flickr_tags)
        make, model, timestring = set_machine_tags(photo_id)
        set_standard_tags(photo_id, make, model, timestring, flickr_tags)

# End of file
