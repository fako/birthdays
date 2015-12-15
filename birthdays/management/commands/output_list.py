from __future__ import unicode_literals, absolute_import, print_function, division

from django.core.management.base import BaseCommand
from django.db.models import Count

from birthdays.models import Person, SoccerSource, SchoolBankSource
from birthdays.helpers import output_person


class Command(BaseCommand):
    """
    Command to list all the people we have more information on than average.
    """

    @staticmethod
    def players_with_city():
        query_set = SoccerSource.objects \
            .annotate(source_num=Count("master__sources")) \
            .filter(source_num__gte=2) \
            .order_by("-source_num")
        for player in query_set:
            if player.master.sources.filter(props__has_key="city").exists():
                output_person(player.master)

    @staticmethod
    def alumni_with_city():
        print(SchoolBankSource.objects.filter(master__isnull=False).count())
        query_set = SchoolBankSource.objects \
            .annotate(source_num=Count("master__sources")) \
            .filter(source_num__gte=2) \
            .order_by("-source_num")
        for alumni in query_set:
            if alumni.master.sources.filter(props__has_key="city").exists():
                output_person(alumni.master)

    @staticmethod
    def juice():
        query_set = Person.objects \
            .annotate(source_num=Count("sources")) \
            .all() \
            .order_by("-source_num")
        for person in query_set[:100]:
            output_person(person)

    def add_arguments(self, parser):
        parser.add_argument(
            'method',
            type=unicode,
            help="The method invoked. Either 'list_juice' or 'list_players_with_city'."
        )

    def handle(self, *args, **options):
        handler = getattr(self, options["method"])
        handler()
