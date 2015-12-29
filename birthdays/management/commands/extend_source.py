from __future__ import unicode_literals, absolute_import, print_function, division
import six

import json
from datetime import datetime

from django.apps import apps as django_apps
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.models import Q

from birthdays.models import Person, PersonSource
from ._actions import DecodeQueryAction


class Command(BaseCommand):
    """
    Commands to extend sources.
    """

    @staticmethod
    def add_to_master(source_model):
        master_set = Person.objects.all()

        for person_source in source_model.objects.all():
            if person_source.full_name and person_source.birth_date:
                try:
                    master = master_set.get(full_name=person_source.full_name, birth_date=person_source.birth_date)
                except Person.DoesNotExist:
                    master = master_set.create(
                        first_name=person_source.first_name,
                        initials=person_source.initials,
                        prefix=person_source.prefix,
                        last_name=person_source.last_name,
                        full_name=person_source.full_name,
                        birth_date=person_source.birth_date,
                        city=person_source.city,
                        props=person_source.props
                    )
                person_source.master = master
                if person_source.city:
                    master.city = "" if master.city is None else master.city
                    master.city += ", {}".format(person_source.city.lower().capitalize())
                person_source.save()

    @staticmethod
    def extend_master(source_model):
        master_set = Person.objects.all()
        for person_source in source_model.objects.filter(master__isnull=True):
            try:
                master = master_set.get(full_name=person_source.full_name)
            except Person.DoesNotExist:
                continue
            master.props.update(person_source.props)
            master.save()
            person_source.master = master
            person_source.save()

    @staticmethod
    def add_cities(source_model):
        from birthdays.models import SchoolBankSource
        for person_source in source_model.objects \
                .not_instance_of(SchoolBankSource) \
                .filter(city__isnull=True, props__has_key="city"):
            if person_source.city or person_source.props["city"] is None:
                continue
            person_source.city = person_source.props["city"]
            person_source.save()

    @staticmethod
    def add_city_person(source_model):
        from birthdays.models import Person
        for person in Person.objects.all():
            person.city = ", ".join([
                source.props["city"]
                for source in person.sources.all()
                if source.props.get("city")
            ])
            person.save()

    @staticmethod
    def remove_minors(source_model):
        from datetime import datetime
        source_model.objects \
            .filter(birth_date__lt=datetime.strptime("28-02-1997", "%d-%m-%Y")) \
            .non_polymorphic() \
            .delete()
        from birthdays.models import Person
        Person.objects \
            .filter(birth_date__lt=datetime.strptime("28-02-1997", "%d-%m-%Y")) \
            .delete()

    @staticmethod
    def split_names(source_model):
        from birthdays.models import (
            PhoneBookSource,
            SchoolBankSource,
            NBASource,
            TriathlonSource,
            MusicSocietySource,
            KNACSource,
            HockeySource,
            HobbyJournalSource,
            FiftyPlusSource
        )
        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            print(letter)
            query_set = source_model.objects.not_instance_of(
                PhoneBookSource,
                SchoolBankSource,
                NBASource,
                TriathlonSource,
                MusicSocietySource,
                KNACSource,
                HockeySource,
                HobbyJournalSource
            ).filter(full_name__startswith=letter)
            for source in query_set:
                if source.full_name:
                    source.split_full_name(force=True)
                    source.save()

    @staticmethod
    def fifty_plus_names(source_model):
        from birthdays.models import FiftyPlusSource
        for source in FiftyPlusSource.objects.all():
            full_name = source.props["name"]
            if full_name and not full_name == "Anoniem":
                source.full_name = full_name
                source.split_full_name(force=True)
                source.save()

    @staticmethod
    def add_city_soccer_source(source_model):
        from pandas import read_csv
        data_frame = read_csv("output/clubs.csv")
        sites_and_city = dict(zip(list(data_frame.site), list(data_frame.city)))
        for person in source_model.objects.filter(city__isnull=True)[:10]
            site_end_pos = person.props["profile"].find("//", 8)
            if not site_end_pos > 0:
               continue
            site = person.props["profile"][site_end_pos+1]
            print(site)


    def add_arguments(self, parser):
        parser.add_argument(
            'extend_type',
            type=unicode,
            help="The extend method. Either 'add_to_master' or 'extend_master'."
        )
        parser.add_argument(
            '-s', '--source',
            type=unicode,
            help="The source to add or extend from."
        )

    def handle(self, *args, **options):
        source_model = django_apps.get_model(app_label="birthdays", model_name=options["source"])
        assert issubclass(source_model, PersonSource), "Specified source {} is not a subclass of PersonSource".format(options["source"])
        handler = getattr(self, options["extend_type"])
        handler(source_model)

