#!/usr/bin/env python
"""
Add photos to Flickr groups based on number of views.
"""
import argparse
import flickrapi # http://www.stuvel.eu/flickrapi
import os
import sys
import xml.etree.ElementTree as ET

def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is one of "yes" or "no".
    """
    valid = {"yes":True,   "y":True,  "ye":True,
             "no":False,     "n":False}
    if default == None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "\
                             "(or 'y' or 'n').\n")

VIEW_GROUPS = [
    # group_id          min_views
    ["665334@N25",      25000],
    ["28114976@N00",    10000],
    ["52498228@N00",    5000],
    ["69218008@N00",    4000],
    ["10386539@N00",    3000],
    ["44588749@N00",    2000],
    ["25661400@N00",    1750],
    ["18374590@N00",    1500],
    ["66448677@N00",    1250],
    ["85342170@N00",    1000],
    ["79303709@N00",    900],
    ["87608476@N00",    800],
    ["65104419@N00",    700],
    ["50687206@N00",    600],
    ["32266655@N00",    500],
    ["97866666@N00",    400],
    ["76852794@N00",    300],
    ["35419517@N00",    200],
    ["37045109@N00",    100],
    ["26651003@N00",    75],
    ["63923506@N00",    50],
    ["14813384@N00",    25],
]

# cmd.exe cannot do Unicode so encode first
def print_it(text):
    print text.encode('utf-8')


def process_photo(photo_id):
    added = 0
    photo_added = False
    for i, group in enumerate(VIEW_GROUPS):
        nsid = group[0]
        min_views = group[1]
        membership = group[2]
        if not photo_added and views > min_views:
            print_it("\n" + str(number) + ") Photo " +photo_id + " has " + str(views) + " views and is eligable for " + nsid + " (min: " + str(min_views) + ")")

            if not membership:
                group_info = flickr.groups_getInfo(group_id = nsid)
                name = group_info.getchildren()[0].find('name').text
                rules = group_info.getchildren()[0].find('rules').text
                if rules:
                    print "----------------------------"
                    print "Rules for group " + name + ":"
                    print rules
                    print "----------------------------"
                    agree = query_yes_no("Agree to rules and join group?")
                    flickr.groups_join(group_id  = nsid, accept_rules = agree)
                else:
                    flickr.groups_join(group_id  = nsid)
                VIEW_GROUPS[i][2] = True

            if not args.test:
                try:
                    flickr.groups_pools_add(photo_id = photo_id, group_id = nsid)
                    print "    Photo added"
                    added += 1
                    photo_added = True

                except flickrapi.FlickrError:
                    error = str(sys.exc_info()[1])
                    print "    Flickr", error
                    if error == "Error: 3: Photo already in pool":
                        print "      Skip photo"
                        skip_photo = True
                        photo_added = True # don't add to any other pools
                        break # Don't bother checking this photo any more
                    if error == "Error: 4: Photo in maximum number of pools":
                        print "      Skip photo"
                        break # Don't bother checking this photo any more
                    elif error == "Error: 5: Photo limit reached":
                        # Don't bother checking this group again
                        print "      Skip group until next time"
                        del VIEW_GROUPS[i]
                    
                except:
                    error = str(sys.exc_info()[1])
                    print "    Error", error

        elif photo_added and views > min_views:
            print "Remove from group", nsid, ":", min_views
            try:
                flickr.groups_pools_remove(photo_id = photo_id, group_id  = nsid)
            except:
                pass
    return added

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Add things to groups depending on view count.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-n', '--number', type=int, 
        help="Number of photos to process. If left blank, keep going")
    parser.add_argument('-b', '--begin', type=int, default=1,
        help="Photo to begin at")
    parser.add_argument('-t', '--tags',
        help="Process images with these tags")
    sort_options = ['date-posted-asc', 'date-posted-desc', 'date-taken-asc', 'date-taken-desc', 'interestingness-desc', 'interestingness-asc', 'relevance']
    parser.add_argument('-s', '--sort', 
        default='interestingness-desc', # approximation to sort-by-views
         choices=sort_options,
        help="The order in which to process photos.")
    parser.add_argument('-r', '--random', action='store_true',
        help="Choose a sort method at random")
    parser.add_argument('-x', '--test', action='store_true',
        help="Test mode: go through the motions but don't add any photos")
    parser.add_argument('-i', '--info', action='store_true',
        help="Show information about my groups and exit")
    args = parser.parse_args()

    try: import timing # optional
    except: pass

    if args.random:
        from random import choice
        args.sort = choice(sort_options)
        print "Random sort order:", args.sort

    api_key = unicode(os.environ['FLICKR_API_KEY'])
    api_secret = unicode(os.environ['FLICKR_SECRET'])
    flickr = flickrapi.FlickrAPI(api_key, api_secret)
    (token, frob) = flickr.get_token_part_one(perms='write')
    if not token: raw_input("Press ENTER after you authorised this program")
    flickr.get_token_part_two((token, frob))

    my_nsid = flickr.people_findByUsername(username = "hugovk")
    my_nsid = my_nsid.getchildren()[0].attrib['nsid']
    print "My NSID:", my_nsid
    group_resp = flickr.people_getGroups(user_id = my_nsid)
    groups_resp = group_resp.getchildren()[0].getchildren()
    groups = {}

    my_groups = []
    for group in groups_resp:
        my_groups.append(group.attrib['nsid'])

    if args.info:
        print "My groups:"
        print "NSID\tThrottled?\tRemaining\tName"
        for group in groups_resp:
            group_nsid = group.attrib['nsid']
            # group_name = group.attrib['name']

            # Get group info
            groups[group_nsid] = get_group_info(group_nsid)

        sys.exit(1)
    
    # Initialise membership
    for i, group in enumerate(VIEW_GROUPS):
        VIEW_GROUPS[i].extend([group[0] in my_groups])
        
    number, processed, added = 0, 0, 0
    try:
        for photo in flickr.walk(tag_mode = 'all',
            privacy_filter = '1', # public
            user_id = 'me',
            sort = args.sort,
            tags = args.tags):

            # print(len(VIEW_GROUPS)), VIEW_GROUPS
            if len(VIEW_GROUPS) == 0:
                sys.exit("All groups filled with " + str(added) + " additions to groups")

            number += 1
            if number < args.begin:
                continue
            processed += 1
            if args.number and processed > args.number:
                sys.exit(str(args.number) + " photos processed, exiting")
            photo_added, photo_slept = False, False
            photo_id = photo.get('id')
            try:
                photo_info = flickr.photos_getInfo(photo_id = photo_id)
            except:
                # Let's just skip this photo then
                continue
            
            # Skip those that aren't mine
            owner = photo_info.getchildren()[0].find('owner').attrib['username']
            if owner != "hugovk":
                print "\n"+str(number)+") Photo "+photo_id+" not mine, skipping"
                continue

            views = int(photo_info.find('photo').attrib['views'])
#            print "===\nID:", photo_id, "Views:", str(views)
            added += process_photo(photo_id)

    except KeyboardInterrupt:
        print "Keyboard interrupt"

    print added, "additions to groups"

# End of file
