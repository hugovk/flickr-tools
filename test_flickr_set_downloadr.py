#!/usr/bin/env python
"""
Unit tests for flickr_set_downloadr.py
"""
import unittest
import flickr_set_downloadr


class TestSequenceFunctions(unittest.TestCase):

    def test_validate_setid__only_numbers(self):
        """ Test numbers return as numbers """
        input = "72157639351309353"
        output = flickr_set_downloadr.validate_setid(input)
        self.assertTrue(output.isdigit())

    def test_validate_setid__numbers_dont_change(self):
        """ Test numbers don't change """
        input = "72157639351309353"
        output = flickr_set_downloadr.validate_setid(input)
        self.assertEqual(input, output)

    def test_validate_setid__flickr_url_returns_numbers(self):
        """ Test numbers don't change """
        input = \
            "https://secure.flickr.com/photos/hugovk/sets/72157639350946574"
        output = flickr_set_downloadr.validate_setid(input)
        self.assertTrue(output.isdigit())

    def test_validate_setid__flickr_url_returns_setit(self):
        """ Test numbers don't change """
        input = \
            "https://secure.flickr.com/photos/hugovk/sets/72157639350946574"
        output = flickr_set_downloadr.validate_setid(input)
        self.assertEqual("72157639350946574", output)

    def test_validate_setid__flickr_url_with_slash_returns_numbers(self):
        """ Test numbers don't change """
        input = \
            "https://secure.flickr.com/photos/hugovk/sets/72157639350946574/"
        output = flickr_set_downloadr.validate_setid(input)
        self.assertTrue(output.isdigit())

    def test_validate_setid__flickr_url_with_slash_returns_setid(self):
        """ Test numbers don't change """
        input = \
            "https://secure.flickr.com/photos/hugovk/sets/72157639350946574/"
        output = flickr_set_downloadr.validate_setid(input)
        self.assertEqual("72157639350946574", output)


if __name__ == '__main__':
    unittest.main()

# End of file
