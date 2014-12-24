#!/usr/bin/env python
"""
Tweet your old Flickr photos from this day in history.
"""
from __future__ import print_function
import argparse
import datetime
import os
import sys
import yaml
import webbrowser

# http://www.stuvel.eu/flickrapi
import flickrapi  # `pip install flickrapi`
import flickrapi.shorturl
# https://github.com/sixohsix/twitter
# from twitter import *  # `pip install twitter`
import twitter

import flickr_utils


def load_yaml(filename):
    f = open(filename)
    data = yaml.safe_load(f)
    f.close()
    if not data.viewkeys() >= {
            'oauth_token', 'oauth_token_secret',
            'consumer_key', 'consumer_secret'}:
        sys.exit("Twitter credentials missing from YAML: " + filename)
    return data


def tweet_it(string, credentials):
    if len(string) <= 0:
        return

    # Create and authorise an app with (read and) write access at:
    # https://dev.twitter.com/apps/new
    # Store credentials in YAML file. See data/onthisday_example.yaml
    t = twitter.Twitter(auth=twitter.OAuth(credentials['oauth_token'],
                        credentials['oauth_token_secret'],
                        credentials['consumer_key'],
                        credentials['consumer_secret']))

    print("TWEETING THIS:\n", string)

    if args.test:
        print("(Test mode, not actually tweeting)")
    else:
        result = t.statuses.update(status=string)
        url = "http://twitter.com/" + \
            result['user']['screen_name'] + "/status/" + result['id_str']
        print("Tweeted:\n" + url)
        if not args.no_web:
            webbrowser.open(url, new=2)  # 2 = open in a new tab, if possible


def six_months_ago(now):
    import calendar
    new_day = now.day
    new_year = now.year

    if now.month > 6:
        new_month = now.month - 6
    else:
        new_month = now.month + 6
        new_year = now.year - 1

    days_in_new_month = calendar.monthrange(new_year, new_month)[1]
    if new_day > days_in_new_month:
        new_day = days_in_new_month

    then = now.replace(year=new_year, month=new_month, day=new_day)
    return then


def six_months_from(now):
    import calendar
    new_day = now.day
    new_year = now.year

    if now.month > 6:
        new_month = now.month - 6
        new_year = now.year + 1
    else:
        new_month = now.month + 6

    days_in_new_month = calendar.monthrange(new_year, new_month)[1]
    if new_day > days_in_new_month:
        # new_day = days_in_new_month
        return None

    then = now.replace(year=new_year, month=new_month, day=new_day)
    return then


def find_photos(flickr, my_nsid, tweet, now, earliest_year):
    found = 0
    for year in range(now.year-1, earliest_year-1, -1):
        print("Checking", year)

        photo = flickr_utils.most_interesting_today_in(
            flickr, my_nsid, year, now=now)

        if photo is not None:
            print("Found a photo for", year)
            found += 1
#             ET.dump(photo)
            photo_id = int(photo.attrib['id'])
            url = flickrapi.shorturl.url(photo_id)
            tweetlet = " " + str(year) + ": "

            tweet += tweetlet + url

            # The next [tweetlet + url] will always be the same length.
            # Check if there's room for another now, so we can avoid
            # an extra API call if possible.

            # "A URL of any length will be altered to 22 characters,
            # even if the link itself is less than 22 characters long."
            # http://support.twitter.com/articles/78124-posting-links-in-a-tweet
            if len(tweet) + len(tweetlet) + 22 > 140:
                break
        else:
            print("No photo for", year)

        print(tweet)

    print("Found", found, "photos")
    return found, tweet


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Tweet your old Flickr photos on this day in history.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '-u', '--username', default="hugovk",
        help="Your Twitter username")
    parser.add_argument(
        '-y', '--yaml',
        default='/Users/hugo/Dropbox/bin/data/onthisday.yaml',
        help="YAML file location containing Twitter keys and secrets")
    parser.add_argument(
        '-e', '--earliest-year', default=2004, type=int,
        help="Earliest year to check for photos. "
        "If 'None', uses the year of your oldest uploaded photo.")
    parser.add_argument(
        '-6', '--six-months', action='store_true',
        help="Show photos from six months ago instead of on this day")
    parser.add_argument(
        '-x', '--test', action='store_true',
        help="Test mode: go through the motions but don't add any photos")
    parser.add_argument(
        '-k', '--api-key',
        help="Flickr API key. "
        "If not given, looks in FLICKR_API_KEY environment variable")
    parser.add_argument(
        '-s', '--api-secret',
        help="Flickr API secret. "
        "If not given, looks in FLICKR_SECRET environment variable")
    parser.add_argument(
        '-nw', '--no-web', action='store_true',
        help="Don't open a web browser to show the tweeted tweet")
    args = parser.parse_args()

    try:
        import timing  # optional
        assert timing  # silence warnings
    except:
        pass

    twitter_credentials = load_yaml(args.yaml)

    if not args.api_key:
        args.api_key = os.environ['FLICKR_API_KEY']
    if not args.api_secret:
        args.api_secret = os.environ['FLICKR_SECRET']
    flickr = flickrapi.FlickrAPI(args.api_key, args.api_secret)
    flickr.authenticate_via_browser(perms='write')

    if args.test:
        print("(Test mode, not actually tweeting)")

    my_nsid = flickr.people_findByUsername(username=args.username)
    my_nsid = my_nsid.getchildren()[0].attrib['nsid']
    print("My NSID:", my_nsid)

    if args.earliest_year:
        earliest_year = args.earliest_year
    else:
        person_info = flickr.people_getInfo(user_id=my_nsid)
        firstdatetaken = person_info.getchildren()[0].find(
            'photos').find('firstdatetaken').text

        # User may have posted (for example, like me) an 19th century photo,
        # but it doesn't matter, this is just an upper limit which may not be
        # reached before the max tweet length is reached.
        earliest_year = int(firstdatetaken[:4])

    print("Earliest year:", earliest_year)

    now = datetime.datetime.now()
    found = 0

    if not args.six_months:
        tweet = "#OnThisDay"
        found, tweet = find_photos(flickr, my_nsid, tweet, now, earliest_year)

    if not found or args.six_months:
        tweet = "#6MonthsAgo"
        now = six_months_from(now)
        if now:
            found, tweet = find_photos(
                flickr, my_nsid, tweet, now, earliest_year)

    if not found:
        sys.exit("No photos found, try again tomorrow")

    print("Tweet this:\n", tweet)
    tweet_it(tweet, twitter_credentials)

# End of file
