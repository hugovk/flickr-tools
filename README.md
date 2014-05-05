Flickr tools
============

Command-line Python scripts to do stuff with Flickr.

Installation
------------

The easiest way is to put these somewhere found in your PATH. Install prerequisites with `pip install -r requirements.txt`


Authentication
--------------

You need a Flickr API key and secret. Apply at the [Flickr website](http://www.flickr.com/services/api/auth.howto.web.html).

Then set them as environment variables. For example, if you use Bash, add the following lines to your $HOME/.bash_profile:

    export FLICKR_API_KEY=0123456789abcdef0123456789abcdef
    export FLICKR_SECRET=0123456789abcdef


favr.py
-------

Create a set of your photos that have been marked as favourites by others.

```
usage: favr.py [-h] [-t TITLE] [-l LIMIT]

Create a set containing your photos that others marked favourite.

optional arguments:
  -h, --help            show this help message and exit
  -t TITLE, --title TITLE
                        Title for the set of your most favoured photos
                        (default: Your favourites)
  -l LIMIT, --limit LIMIT
                        How many photos to add to the set (default: 81)
```

flickr_random_downloadr.py
--------------------------
```
usage: flickr_random_downloadr.py [-h] [-u USERNAME] [-n NUMBER]
                                  [-s {s,q,t,m,n,z,c,b,o}] [-t] [-nc]

Download random photos from your account

optional arguments:
  -h, --help            show this help message and exit
  -u USERNAME, --username USERNAME
                        The username to download from. (default: hugovk)
  -n NUMBER, --number NUMBER
                        Number of photos to download (default: 10)
  -s {s,q,t,m,n,z,c,b,o}, --size {s,q,t,m,n,z,c,b,o}
                        The size of photo you want to download. Size must fit
                        the following: s - 75x75, q - 150x150, t - 100 on the
                        longest side, m - 240 on the longest side, n - 320 on
                        the longest side, z - 640 on the longest side, c - 800
                        on the longest side, b - 1024 on the longest side
                        (default), o - original (default: b)
  -t, --title           Use the title as the filename (TODO ensure title is
                        filesystem-safe) (default: False)
  -nc, --noclobber      Don't clobber pre-exisiting files (default: False)

```

flickr_set_downloadr.py
-----------------------
```
usage: flickr_set_downloadr.py [-h] [-s {s,q,t,m,n,z,c,b,o}] [-t] [-nc] [-n]
                               setid

Download a Flickr set

positional arguments:
  setid                 The Set ID for the set to download.

optional arguments:
  -h, --help            show this help message and exit
  -s {s,q,t,m,n,z,c,b,o}, --size {s,q,t,m,n,z,c,b,o}
                        The size of photo you want to download. Size must fit
                        the following: s - 75x75, q - 150x150, t - 100 on the
                        longest side, m - 240 on the longest side, n - 320 on
                        the longest side, z - 640 on the longest side, c - 800
                        on the longest side, b - 1024 on the longest side
                        (default), o - original (default: b)
  -t, --title           Use the title as the filename (TODO ensure title is
                        filesystem-safe) (default: False)
  -nc, --noclobber      Don't clobber pre-exisiting files (default: False)
  -n, --number          Prefix filenames with a serial number (default: False)
```

onthisday.py
------------

Example tweet:

> [#OnThisDay](https://twitter.com/search?q=%23OnThisDay&src=hash) 2013: http://flic.kr/p/dGrjUj  2011: http://flic.kr/p/98wFvG  2010: http://flic.kr/p/7t9aDT  2008: http://flic.kr/p/4jSx8c

https://twitter.com/hugovk/status/418366422344282112

```
usage: onthisday.py [-h] [-u USERNAME] [-y EARLIEST_YEAR] [-x] [-k API_KEY]
                    [-s API_SECRET]

Tweet your old Flickr photos on this day in history.

optional arguments:
  -h, --help            show this help message and exit
  -u USERNAME, --username USERNAME
                        Your Twitter username (default: hugovk)
  -y EARLIEST_YEAR, --earliest-year EARLIEST_YEAR
                        Earliest year to check for photos. If 'None', checks
                        the year of your oldest uploaded photo. (default:
                        2004)
  -x, --test            Test mode: go through the motions but don't add any
                        photos (default: False)
  -k API_KEY, --api-key API_KEY
                        Flickr API key. If not given, looks in FLICKR_API_KEY
                        environment variable (default: None)
  -s API_SECRET, --api-secret API_SECRET
                        Flickr API secret. If not given, looks in
                        FLICKR_SECRET environment variable (default: None)
```

taggr.py
--------

Add machine tags on Flickr from EXIF data.

Initial version based on [Paul Mison's EXIF machine tagger](http://blech.typepad.com/blog/2008/11/flickr-exif-machine-tags.html) [Perl script](http://husk.org/code/flickr_exif_machinetag.pl), but without the database.

```
usage: taggr.py [-h] [-x] [-a] [-b BEGIN] [-n NUMBER] [-d] [-j] [-k API_KEY]
                [-s API_SECRET]

Machine tag photos from EXIF.

optional arguments:
  -h, --help            show this help message and exit
  -x, --test            Test mode: go through the motions but don't add any
                        tags
  -a, --all             Process all, regardless of previous processing
  -b BEGIN, --begin BEGIN
                        Photo to begin at
  -n NUMBER, --number NUMBER
                        Number of photos to process. If left blank, keep going
  -d, --description     Include description as tags
  -j, --jatkuu          When reaching a previously processed photo, continue
                        to the next instead of exiting
  -k API_KEY, --api-key API_KEY
                        Flickr API key. If not given, looks in FLICKR_API_KEY
                        environment variable
  -s API_SECRET, --api-secret API_SECRET
                        Flickr API secret. If not given, looks in
                        FLICKR_SECRET environment variable
```

viewr.py
--------

Add photos to Flickr groups based on number of views.


```
usage: viewr.py [-h] [-n NUMBER] [-b BEGIN] [-t TAGS] [-x] [-i]

Add things to groups depending on view count.

optional arguments:
  -h, --help            show this help message and exit
  -n NUMBER, --number NUMBER
                        Number of photos to process. If left blank, keep going
                        (default: None)
  -b BEGIN, --begin BEGIN
                        Photo to begin at (default: 1)
  -t TAGS, --tags TAGS  Process images with these tags (default: None)
  -x, --test            Test mode: go through the motions but don't add any
                        photos (default: False)
  -i, --info            Show information about my groups and exit (default:
                        False)
```

yr.py
--------

Make a collage of a year's most interesting photos. Requires PIL (or rather Pillow) and flickrapi. Also uses normalise.py and contact_sheet.py from https://github.com/hugovk/pixel-tools.

[Some examples on Flickr.](https://www.flickr.com/search/?text=flickr%3Atool%3Dyr&sort=date-posted-desc)


```
usage: yr.py [-h] [-u USERNAME] [-s {s,q,t,m,n,z,c,b,o}] [-y YEAR]

Make a collage of a year's most interesting photos

optional arguments:
  -h, --help            show this help message and exit
  -u USERNAME, --username USERNAME
                        Your Flickr username (default: hugovk)
  -s {s,q,t,m,n,z,c,b,o}, --size {s,q,t,m,n,z,c,b,o}
                        The size of photo you want to download: s - 75x75, q -
                        150x150, t - 100 on the longest side, m - 240 on the
                        longest side, n - 320 on the longest side, z - 640 on
                        the longest side, c - 800 on the longest side, b -
                        1024 on the longest side (default), o - original
                        (default: b)
  -y YEAR, --year YEAR  Year to download (default: 2013)
  ```
