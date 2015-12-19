from __future__ import unicode_literals, absolute_import, print_function, division

from django.test import TestCase

from birthdays.management.commands.input_source import Command as InputCommand
from birthdays.models import PersonSourceMockOne


class TestInputCommand(TestCase):

    fixtures = ["test.json"]

    def test_from_fixture(self):
        InputCommand.from_fixture("birthdays/tests/mock-fixture.json", "PersonSourceMockOne", {"voornaam": "first_name"}, "%Y-%m-%d")
        self.assertEqual(PersonSourceMockOne.objects.count(), 9)  # 6 from Django fixtures, 3 from file.
        mp = PersonSourceMockOne.objects.last()
        self.assertTrue(mp.props["occupation"])
        self.assertTrue(mp.first_name)
        self.assertFalse(mp.last_name)
        self.assertFalse(mp.full_name)
        self.assertTrue(mp.birth_date)
        self.assertEqual(sorted(mp.props.keys()), sorted(['occupation']))
