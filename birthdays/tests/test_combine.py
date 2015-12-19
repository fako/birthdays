from __future__ import unicode_literals, absolute_import, print_function, division

from django.test import TestCase

from birthdays.management.commands.combine_sources import Command as CombineCommand
from birthdays.models import GeneratedPerson


class TestCombineCommand(TestCase):

    fixtures = ["test.json"]

    def test_combine(self):
        CombineCommand.combine("PersonSourceMockOne", "PersonSourceMockTwo", ["sex", "address"])
        self.assertEqual(GeneratedPerson.objects.count(), 2)
        gp = GeneratedPerson.objects.first()
        self.assertTrue(gp.first_name)
        self.assertTrue(gp.last_name)
        self.assertTrue(gp.full_name)
        self.assertTrue(gp.birth_date)
        self.assertEqual(sorted(gp.props.keys()), sorted(['address', 'occupation', 'sex', 'single']))