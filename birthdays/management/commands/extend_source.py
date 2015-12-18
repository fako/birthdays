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
                        props=person_source.props
                    )
                person_source.master = master
                person_source.save()

    @staticmethod
    def extend_master(source_model):
        master_set = Person.objects.all()
        for person_source in source_model.objects.all():
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
        for person_source in source_model.objects.filter(props__haskey="city"):
            if hasattr(person_source, 'master'):
                person_source.city = person_source.props["city"]
            else:
                print(", ".join([
                    source.props["city"]
                    for source in person_source.sources
                    if source.props.get("city")
                ]))
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
            .filter(birth_date__lt=datetime.strptime("31-10-2015", "%d-%m-%Y")) \
            .delete()

    @staticmethod
    def add_city_soccer_source(source_model):
        pass

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

