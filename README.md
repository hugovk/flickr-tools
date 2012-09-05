taggr.py
========

Command-line Python script to add machine tags on Flickr from EXIF data.

Initial version based on Paul Mison's EXIF machine tagger Perl script, but without the database:

    http://blech.typepad.com/blog/2008/11/flickr-exif-machine-tags.html
    http://husk.org/code/flickr_exif_machinetag.pl

Authentication
--------------

You need a Flickr API key and secret. Apply at the [Flickr website](http://www.flickr.com/services/api/auth.howto.web.html).

Then set them as environment variables. For example, if you use Bash, add the following lines to your $HOME/.bash_profile:

    export FLICKR_API_KEY=0123456789abcdef0123456789abcdef
    export FLICKR_SECRET=0123456789abcdef

Usage
-----

usage: taggr.py [-h] [-x]

optional arguments:
  -h, --help  show this help message and exit
  -x, --test  Test mode: go through the motions but don't add any tags
