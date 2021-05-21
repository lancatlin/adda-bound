from django.test import TestCase

from bot.utils import get_token


class UtilsTest(TestCase):
    def test_get_token_success(self):
        '''Test getting token from a string'''
        s = '/join 276456'
        self.assertEqual(get_token(s), 276456)

    def test_get_token_blank(self):
        '''Test not getting number when there are no number provided'''
        s = '/join abcedf'
        self.assertRaises(ValueError, lambda: get_token(s))

    def test_get_token_multiple(self):
        s = '/join 12345 67890'
        self.assertRaises(ValueError, lambda: get_token(s))
