Flickr tools
============

Command-line Python scripts to do stuff with Flickr.

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
taggr.py
--------

Add machine tags on Flickr from EXIF data.

Initial version based on [Paul Mison's EXIF machine tagger](http://blech.typepad.com/blog/2008/11/flickr-exif-machine-tags.html) [Perl script](http://husk.org/code/flickr_exif_machinetag.pl), but without the database.

```
usage: taggr.py [-h] [-x]

optional arguments:
  -h, --help  show this help message and exit
  -x, --test  Test mode: go through the motions but don't add any tags
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
