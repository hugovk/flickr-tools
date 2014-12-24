#!/usr/bin/python

"""
Download your most interesting photos for each day in a given year.
For days with no photos, create a black pixel.
Do the same for all days up to 31st, so we have 31st Feb.
Finally, make a grid of the whole year.
"""
from __future__ import print_function
import argparse
import datetime
import os

# import xml.etree.ElementTree as ET

from PIL import Image
import flickrapi
import flickr_utils

api_key = os.environ['FLICKR_API_KEY']
api_secret = os.environ['FLICKR_SECRET']


def create_dir(dir):
    import os
    if not os.path.isdir(dir):
        os.mkdir(dir)


def contact_sheet():
    # TODO import modules and call properly
    year = str(args.year)
    tempdir = os.path.join(year, 'temp_normalised')
    os.system('mkdir ' + tempdir)
    os.system(
        'normalise.py -n 1024,575 -i "' + os.path.join(year, '*.jpg') +
        '" -o ' + tempdir)
    os.system(
        'contact_sheet.py -m 50 -p 10 -i "' + os.path.join(tempdir, '*.jpg') +
        '" -o ' + year + '.jpg')


def black_pixel(filename):
    if not os.path.exists(filename):
        img = Image.new("RGB", (1, 1), "black")  # create a new black pixel
        img.save(filename)


def find_photo_for_date(date, flickr, nsid):
    title = str(date)  # yyyymmdd
    filename = os.path.join(str(args.year), title + ".jpg")
    if os.path.exists(filename):
        print("\tFound file")
    else:
        today = datetime.datetime.now()
        today = datetime.date(today.year, today.month, today.day)
        if date > today:
            print("\tIn the future")
            black_pixel(filename)
            return

        photo = flickr_utils.most_interesting_today_in(
            flickr, nsid, date.year, args.size, date)
        if photo is not None:
            print("\tFound photo")
            url = flickr_utils.photo_url(flickr, photo, args.size)

            attempts = 0
            while(attempts <= 5):
                try:
                    flickr_utils.download(url, title, True, dir=str(args.year))
                    break
                except:
                    print("Try again")
                    attempts += 1

        else:
            print("\tNo photo")
            black_pixel(filename)


def loop_days_in_year(year, flickr, nsid):

    # Only include real dates

    # create date objects
    begin_year = datetime.date(year, 1, 1)
    end_year = datetime.date(year, 12, 31)
    one_day = datetime.timedelta(days=1)
    print("These are all the dates of %d:" % year)
    next_day = begin_year
    for day in range(0, 366):  # includes potential leap year
        if next_day > end_year:
            break

        print(next_day)
        find_photo_for_date(next_day, flickr, nsid)

        # increment date object by one day
        next_day += one_day


def loop_days_in_year2(year, flickr, nsid):

    # Include "fake" dates like Feb 30, as we want to pad those with black

    # create date objects
    for month in range(1, 12+1):
        for day in range(1, 31+1):
            try:
                next_day = datetime.date(year, month, day)
            except ValueError:  # out of range, eg. 31 Feb
                print("\tblack pixel")
                black_pixel(
                    os.path.join(
                        str(args.year),
                        str(year) +
                        "-" +
                        str(month).zfill(2) +
                        "-" +
                        str(day).zfill(2) +
                        ".jpg"))
                continue

            print(next_day)
            find_photo_for_date(next_day, flickr, nsid)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Make a collage of a year's most interesting photos",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '-u', '--username', default="hugovk",
        help="Your Flickr username")
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
        "-y", "--year", default=2013, type=int,
        help="Year to download")
    args = parser.parse_args()

    # Optional, http://stackoverflow.com/a/1557906/724176
    try:
        import timing
        assert timing  # silence warnings
    except:
        pass

    flickr = flickrapi.FlickrAPI(api_key, api_secret)
    flickr.authenticate_via_browser(perms='read')

    my_nsid = flickr.people_findByUsername(username=args.username)
    my_nsid = my_nsid.getchildren()[0].attrib['nsid']
    print("My NSID:", my_nsid)

    create_dir(str(args.year))
    loop_days_in_year2(args.year, flickr, my_nsid)

    contact_sheet()

# End of file
