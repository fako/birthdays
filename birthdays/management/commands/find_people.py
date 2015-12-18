from __future__ import unicode_literals, absolute_import, print_function, division
import six

from django.core.management.base import BaseCommand
from django.core.paginator import Paginator

from birthdays.models import PersonSource
from birthdays.helpers import output_person

from ._actions import DecodeQueryAction, parse_dutch_date


class Command(BaseCommand):
    """
    Command to list all the people we have more information on than average.
    """

    @staticmethod
    def find(first_name=None, last_name=None, full_name=None, initials=None, prefix=None, birth_date=None,
             batch_size=0, page_number=1, fuzzy=False, **kwargs):
        # Making the extra kwargs work with the HStore field
        filters = {"props__{}".format(key): value for key, value in six.iteritems(kwargs) if value is not None}
        # Keeping IDE auto complete for the method by writing out the definition.
        # Putting values back in a dictionary (like kwargs) to iterate over the items.
        string_arguments = {
            "first_name__{}": first_name,
            "last_name__{}": last_name,
            "full_name__{}": full_name,
            "initials__{}": initials,
            "prefix__{}": prefix,
        }

        fixed_arguments = {
            key.format("iexact" if not fuzzy else "icontains"): value
            for key, value in six.iteritems(string_arguments)
        }
        fixed_arguments.update({
            "birth_date": birth_date

        })
        filters.update({key: value for key, value in six.iteritems(fixed_arguments) if value is not None})
        query_set = PersonSource.objects.filter(**filters)
        if batch_size:
            pages = Paginator(query_set, batch_size)
            page = pages.page(page_number)
            persons = page.object_list
        else:
            persons = query_set
        for person in persons:
            output_person(person)
        print("Applied filters:", filters)
        print("Total matches:", query_set.count())
        if batch_size:
            print("Batch size:", batch_size)
            print("Page:", page_number)

    def add_arguments(self, parser):
        parser.add_argument(
            '-f', '--first-name',
            type=unicode,
            nargs="?",
            help="First name you're looking for.",
            dest="first_name"
        )
        parser.add_argument(
            '-l', '--last-name',
            type=unicode,
            nargs="?",
            help="Last name you're looking for.",
            dest="last_name"
        )
        parser.add_argument(
            '-i', '--initials',
            type=unicode,
            nargs="?",
            help="Initials you're looking for.",
            dest="initials"
        )
        parser.add_argument(
            '-p', '--prefix',
            type=unicode,
            nargs="?",
            help="Prefix you're looking for.",
            dest="prefix"
        )
        parser.add_argument(
            '-n', '--name',
            type=unicode,
            nargs="?",
            help="Full name you're looking for.",
            dest="full_name"
        )
        parser.add_argument(
            '-d', '--birth-date',
            type=parse_dutch_date,
            nargs="?",
            help="Birth date you're looking for (dd-mm-yyyy).",
            dest="birth_date"
        )
        parser.add_argument(
            '-e', '--extra',
            type=unicode,
            action=DecodeQueryAction,
            nargs="?",
            default={},
            help="A urlencoded string that specifies extra search criteria. "
                 "Example: 'city=Utrecht&street_name=Oude Gracht'"
        )
        parser.add_argument(
            '-B', '--batch',
            type=int,
            nargs="?",
            default=0,
            help="The size of pages that the results should be divided in",
            dest="batch_size"
        )
        parser.add_argument(
            '-P', '--page',
            type=int,
            nargs="?",
            default=1,
            help="The page you want to view",
            dest="page_number"
        )
        parser.add_argument(
            '-F', '--fuzzy',
            action="store_true",
            nargs="?",
            default=False,
            help="",
            dest="fuzzy"
        )

    def handle(self, no_color=False, traceback=False, verbosity=1, *args, **options):
        options.update(options.pop("extra", {}))
        self.find(**options)
