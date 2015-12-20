from __future__ import unicode_literals, absolute_import, print_function, division

from django.test import TestCase
from django.conf import settings

from birthdays.models import NBASource, Person, SoccerSource


class TestSources(TestCase):

    fixtures = ["phonebook.json"]

    def test_nba_split_name(self):
        instance = NBASource()
        instance.full_name = "Spek, H. van der"
        instance.split_full_name()
        self.assertEqual(instance.initials, "H.")
        self.assertEqual(instance.prefix, "van der")
        self.assertEqual(instance.last_name, "van der Spek")
        instance = NBASource()
        instance.full_name = "Berkers, F.C."
        instance.split_full_name()
        self.assertEqual(instance.initials, "F.C.")
        self.assertEqual(instance.prefix, None)
        self.assertEqual(instance.last_name, "Berkers")
        instance = NBASource()
        instance.full_name = "Berkers"
        instance.split_full_name()
        self.assertEqual(instance.initials, None)
        self.assertEqual(instance.prefix, None)
        self.assertEqual(instance.last_name, None)

    def test_generic_split_name(self):
        instance = Person()
        instance.full_name = "Henk van der Spek"
        instance.split_full_name()
        self.assertEqual(instance.first_name, "Henk")
        self.assertEqual(instance.prefix, "van der")
        self.assertEqual(instance.last_name, "van der Spek")
        instance = Person()
        instance.full_name = "Fako Casper Berkers"
        instance.split_full_name()
        self.assertEqual(instance.first_name, "Fako Casper")
        self.assertEqual(instance.prefix, None)
        self.assertEqual(instance.last_name, "Berkers")
        instance = Person()
        instance.full_name = "Lotte Beatrice van der Snoek"
        instance.split_full_name()
        self.assertEqual(instance.first_name, "Lotte Beatrice")
        self.assertEqual(instance.prefix, "van der")
        self.assertEqual(instance.last_name, "van der Snoek")
        instance = Person()
        instance.full_name = "Ellen BijsterBOSCH"
        instance.split_full_name()
        self.assertEqual(instance.first_name, "Ellen")
        self.assertEqual(instance.prefix, None)
        self.assertEqual(instance.last_name, "BijsterBOSCH")
        instance = Person()
        instance.full_name = "Malou de Roy van Zuydewijn"
        instance.split_full_name()
        self.assertEqual(instance.first_name, "Malou")
        self.assertEqual(instance.prefix, None)
        self.assertEqual(instance.last_name, "de Roy van Zuydewijn")
        instance = Person()
        instance.full_name = "Bart-Jan Dokter"
        instance.split_full_name()
        self.assertEqual(instance.first_name, "Bart-Jan")
        self.assertEqual(instance.prefix, None)
        self.assertEqual(instance.last_name, "Dokter")
        instance = Person()
        instance.full_name = "Fako Berkers-Raaphorst"
        instance.split_full_name()
        self.assertEqual(instance.first_name, "Fako")
        self.assertEqual(instance.prefix, None)
        self.assertEqual(instance.last_name, "Berkers, Raaphorst")
        instance = Person()
        instance.full_name = "Gert Sup?r"
        instance.split_full_name()
        self.assertEqual(instance.first_name, None)
        self.assertEqual(instance.prefix, None)
        self.assertEqual(instance.last_name, None)
        instance = Person()
        instance.full_name = "zzzzz zzzzzzzz"
        instance.split_full_name()
        self.assertEqual(instance.first_name, None)
        self.assertEqual(instance.prefix, None)
        self.assertEqual(instance.last_name, None)
        instance = Person()
        instance.full_name = "Zwarte Piet"
        instance.split_full_name()
        self.assertEqual(instance.first_name, None)
        self.assertEqual(instance.prefix, None)
        self.assertEqual(instance.last_name, None)
        instance = Person()
        instance.full_name = "Frans Frans"
        instance.split_full_name()
        self.assertEqual(instance.first_name, "Frans")
        self.assertEqual(instance.prefix, None)
        self.assertEqual(instance.last_name, "Frans")
        instance = Person()
        instance.full_name = "Synthia Rosalie Frans van der Snoek (van der Spek)"
        instance.split_full_name()
        self.assertEqual(instance.first_name, "Synthia Rosalie")
        self.assertEqual(instance.prefix, None)
        self.assertEqual(instance.last_name, "van der Snoek, van der Spek")

    def test_soccer_split_name(self):
        instance = SoccerSource()
        instance.full_name = "H. van der Spek"
        instance.split_full_name()
        self.assertEqual(instance.first_name, None)
        self.assertEqual(instance.initials, "H.")
        self.assertEqual(instance.prefix, "van der")
        self.assertEqual(instance.last_name, "van der Spek")

    def test_get_uri(self):
        instance = NBASource()
        instance.full_name = "Henk van der Spek"
        instance.props = {}
        instance.save()
        uri = instance.get_uri()
        self.assertEqual(uri, "{}/admin/birthdays/nbasource/16/".format(settings.BIRTHDAYS_DOMAIN))
