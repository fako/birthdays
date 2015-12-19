from __future__ import unicode_literals, absolute_import, print_function, division

from django.test import TestCase
from django.db.models import Count

from birthdays.management.commands.extend_source import Command as ExtendCommand
from birthdays.models import Person, PersonSourceMockOne, PersonSourceMockTwo


class TestExtendCommand(TestCase):

    fixtures = ["test.json"]

    def test_add_to_master(self):
        ExtendCommand.add_to_master(PersonSourceMockOne)
        self.assertEqual(Person.objects.count(), 2)
        mp = Person.objects.last()
        self.assertEqual(mp.sources.count(), 1)
        self.skipTest("Test adding a city")

    def test_extend_master(self):
        ExtendCommand.add_to_master(PersonSourceMockOne)
        ExtendCommand.extend_master(PersonSourceMockTwo)
        self.assertEqual(Person.objects.annotate(num_sources=Count("sources")).filter(num_sources__gt=1).count(), 1)
        mp = Person.objects.annotate(num_sources=Count("sources")).get(num_sources__gt=1)
        self.assertEqual(sorted(mp.props.keys()), sorted(['address', 'occupation', 'sex', 'single']))
