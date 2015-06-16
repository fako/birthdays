from __future__ import unicode_literals, absolute_import, print_function, division
import six

import json

from django.apps import apps as django_apps
from django.core.management.base import BaseCommand

from birthdays.models import Person, PersonSource
from ._actions import DecodeMappingAction


class Command(BaseCommand):
    """
    Command to merge sources into GeneratedPersons
    """

    @staticmethod
    def add_to_master(source_name):
        source_model = django_apps.get_model(app_label="birthdays", model_name=source_name)
        master_set = Person.objects.all()

        assert issubclass(source_model, PersonSource), "Specified source {} is not a subclass of Person".format(source_name)

        for person_source in source_model.objects.all():
            if (person_source.full_name or person_source.first_name and person_source.last_name) \
                    and person_source.birth_date:
                person_source.fill_full_name()  # assure presence of full name
                if master_set.filter(full_name=person_source.full_name).exists():
                    continue
                else:
                    master = master_set.create(
                        first_name=person_source.first_name,
                        last_name=person_source.last_name,
                        full_name=person_source.full_name,
                        birth_date=person_source.birth_date,
                        props=person_source.props
                    )
                    person_source.master = master
                    person_source.save()

    @staticmethod
    def prep_dict_for_fields(dictionary, mapping):
        fields = {}
        for key, value in six.iteritems(dictionary):
            if key in mapping:
                key = mapping[key]
            fields[key] = value
        return fields

    @staticmethod
    def from_fixture(file_name, source_name, mapping):
        source_model = django_apps.get_model(app_label="birthdays", model_name=source_name)
        with open(file_name, "r") as fp:
            data = json.load(fp)
            assert isinstance(data, list), "Expected a list inside " + file_name
            assert isinstance(data[0]["fields"], dict), "Expected JSON Django serialized models as elements in " + file_name
            for instance in data:
                fields = Command.prep_dict_for_fields(instance["fields"], mapping)
                source_model.objects.create(
                    first_name=fields.pop("first_name", None),
                    last_name=fields.pop("last_name", None),
                    full_name=fields.pop("full_name", None),
                    birth_date=fields.pop("birth_date", None),
                    props=fields
                )

    @staticmethod
    def from_records(file_name, source_name, mapping):
        pass

    @staticmethod
    def from_csv(file_name, source_name, mapping):
        pass

    def add_arguments(self, parser):
        parser.add_argument('input_type', type=unicode)
        parser.add_argument('-f', '--file', type=unicode)
        parser.add_argument('-s', '--source', type=unicode)
        parser.add_argument('-m', '--mapping', type=unicode, action=DecodeMappingAction, nargs="?", default={})

    def handle(self, *args, **options):
        handler = getattr(self, options["input_type"])
        handler(options["file"], options["source"], options["mapping"])
