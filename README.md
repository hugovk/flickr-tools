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
