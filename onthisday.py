#!/usr/bin/env python
"""
Tweet your old Flickr photos on this day in history.
"""
import argparse
import datetime
import flickrapi # http://www.stuvel.eu/flickrapi `pip install flickrapi`
import flickrapi.shorturl
import os
import sys
import xml.etree.ElementTree as ET
from twitter import * # https://github.com/sixohsix/twitter `pip install twitter`

# Twitter: create and authorise an app at https://dev.twitter.com/apps/new
CONSUMER_KEY = "TODO_ENTER_YOURS_HERE"
CONSUMER_SECRET = "TODO_ENTER_YOURS_HERE"
OAUTH_TOKEN = "TODO_ENTER_YOURS_HERE"
OAUTH_TOKEN_SECRET = "TODO_ENTER_YOURS_HERE"


def tweet_it(string):
    if len(string) <= 0:
        return

    t = Twitter(auth=OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET,
                           CONSUMER_KEY, CONSUMER_SECRET))

    print "TWEETING THIS:\n", string

    if not args.test:
        t.statuses.update(status=string)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Tweet your old Flickr photos on this day in history.", 
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-u', '--username', default="hugovk",
        help="Your Twitter username")
    parser.add_argument('-f', '--first_year', default=2004, type=int,
        help="Oldest year to check for photos. If 'None', checks the year of your oldest uploaded photo.")
    parser.add_argument('-x', '--test', action='store_true',
        help="Test mode: go through the motions but don't add any photos")
    args = parser.parse_args()

    try: import timing # optional
    except: pass

    api_key = unicode(os.environ['FLICKR_API_KEY'])
    api_secret = unicode(os.environ['FLICKR_SECRET'])
    flickr = flickrapi.FlickrAPI(api_key, api_secret)
    (token, frob) = flickr.get_token_part_one(perms='write')
    if not token: raw_input("Press ENTER after you authorised this program")
    flickr.get_token_part_two((token, frob))

    my_nsid = flickr.people_findByUsername(username = args.username)
    my_nsid = my_nsid.getchildren()[0].attrib['nsid']
    print "My NSID:", my_nsid

    if args.first_year:
        first_year = args.first_year
    else:
        person_info = flickr.people_getInfo(user_id = my_nsid)
        firstdatetaken = person_info.getchildren()[0].find('photos').find('firstdatetaken').text

        # User may have posted (for example, like me) an 19th century photo, 
        # but it doesn't matter, this is just an upper limit which may not be reached
        # before the max tweet length is reached.
        first_year = int(firstdatetaken[:4])

    print "First year:", first_year

    now = datetime.datetime.now()
    tweet = "#OnThisDay"
    found = 0
    for year in range(now.year-1, first_year-1, -1):
        print "Checking", year

        # Find a photo from this year
        taken_year = now.replace(year=year)
        
        min_taken_date = datetime.datetime.combine(taken_year, datetime.time.min)
        max_taken_date = datetime.datetime.combine(taken_year, datetime.time.max)
        
        # Convert into MySQL datetime
        min_taken_date = min_taken_date.isoformat(' ')
        max_taken_date = max_taken_date.isoformat(' ')

        photos = flickr.photos_search(
            user_id = my_nsid, 
            sort = "interestingness-desc", # most interesting
            privacy_filter = "1", # public
            per_page = "1", # only want a single photo per year
            min_taken_date = min_taken_date, 
            max_taken_date = max_taken_date)
#         ET.dump(photos)
        if len(photos[0]) > 0:
            print "Found a photo for", year
            found += 1
#             ET.dump(photos[0][0])
            photo_id = int(photos[0][0].attrib['id'])
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
            print "No photo for", year
        
        print tweet
    
    print "Found", found, "photos"
    if found == 0:
        sys.exit("No photos found today, try again tomorrow")

    print "Tweet this:\n", tweet
    tweet_it(tweet)

# End of file
