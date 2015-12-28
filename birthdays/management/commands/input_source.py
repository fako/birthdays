from __future__ import unicode_literals, absolute_import, print_function, division
import six

import json
from datetime import datetime
import pandas

from django.apps import apps as django_apps
from django.core.management.base import BaseCommand
from django.db import connections

from ._actions import DecodeQueryAction


class Command(BaseCommand):
    """
    Command to add new rows to person sources.
    """

    @staticmethod
    def prep_dict_for_fields(dictionary, mapping, date_format, exclude):
        fields = {}
        for key, value in six.iteritems(dictionary):
            if key in exclude:
                continue
            if key in mapping:
                key = mapping[key]
            if pandas.isnull(value):
                value = None
            if isinstance(value, (six.integer_types, float)):
                value = str(int(value))
            if key == "birth_date":
                if value:
                    value = datetime.strptime(value, date_format).date()
                else:
                    value = None
            if isinstance(value, six.string_types):
                if not isinstance(value, unicode):
                    fields[key] = unicode(value, errors="replace") if value else None
                else:
                    fields[key] = value if value else None
            else:
                fields[key] = value
        return fields

    @staticmethod
    def from_fixture(file_name, source_name, mapping, date_format, exclude):
        source_model = django_apps.get_model(app_label="birthdays", model_name=source_name)
        with open(file_name, "r") as fp:
            data = json.load(fp)
            assert isinstance(data, list), "Expected a list inside " + file_name
            assert isinstance(data[0]["fields"], dict), "Expected JSON Django serialized models as elements in " + file_name
            for instance in data:
                fields = Command.prep_dict_for_fields(instance["fields"], mapping, date_format, exclude)
                source_model.objects.register_from_fields(fields, source_model)

    @staticmethod
    def from_records(file_name, source_name, mapping, date_format, exclude):
        source_model = django_apps.get_model(app_label="birthdays", model_name=source_name)
        with open(file_name, "r") as fp:
            data = json.load(fp)
            assert isinstance(data, list), "Expected a list inside " + file_name
            assert isinstance(data[0], dict), "Expected JSON dict as elements in " + file_name
            for instance in data:
                fields = Command.prep_dict_for_fields(instance, mapping, date_format, exclude)
                source_model.objects.register_from_fields(fields, source_model)

    @staticmethod
    def from_csv(file_name, source_name, mapping, date_format, exclude):
        source_model = django_apps.get_model(app_label="birthdays", model_name=source_name)
        data_frame = pandas.read_csv(file_name, sep=';')
        columns = [c for c in data_frame.columns if 'Unnamed' not in c]
        data_frame = data_frame[columns]
        for record in data_frame.to_dict(orient="records"):
            fields = Command.prep_dict_for_fields(record, mapping, date_format, exclude)
            source_model.objects.register_from_fields(fields, source_model)

    @staticmethod
    def from_mysql_table(table_name, source_name, mapping, date_format, exclude):
        source_model = django_apps.get_model(app_label="birthdays", model_name=source_name)
        cursor = connections["mysql"].cursor()
        cursor.execute("SELECT COUNT(*) FROM {}".format(table_name))
        count = cursor.fetchone()[0]
        batch_size = 1000
        batch_count = int(count / batch_size) + 1  # bit naieve
        for index in range(0, batch_count):
            offset = index * batch_size
            cursor.execute("SELECT * FROM {} LIMIT {} OFFSET {}".format(table_name, batch_size, offset))
            desc = cursor.description
            records = [
                dict(zip([col[0] for col in desc], row))
                for row in cursor.fetchall()
            ]
            for record in records:
                fields = Command.prep_dict_for_fields(record, mapping, date_format, exclude)
                source_model.objects.register_from_fields(fields, source_model)

    def add_arguments(self, parser):
        parser.add_argument(
            'input_method',
            type=unicode,
            help="The input method. Either 'from_fixture' or 'from_mysql_table'."
        )
        parser.add_argument(
            '-f', '--file',
            type=unicode,
            help="The input data location. Either a fixture file or a MySQL table."
        )
        parser.add_argument(
            '-s', '--source',
            type=unicode,
            help="The name of the PersonSource to store the data under."
        )
        parser.add_argument(
            '-m', '--mapping',
            type=unicode,
            action=DecodeQueryAction,
            nargs="?",
            default={},
            help="A urlencoded string that specifies how to map the input data to the source data. "
                 "Example: 'naam=full_name&geboortedatum=birth_date'."
        )
        parser.add_argument(
            '-d', '--date-format',
            type=unicode,
            nargs="?",
            default="%d-%m-%Y",
            help="The format of the input data that should be stored in the birth_date source field."
        )
        parser.add_argument(
            '-e', '--exclude',
            type=lambda s: [item.strip() for item in s.split(',')],
            nargs="?",
            default=[],
            help="A comma separated list of fields that should be ignored."
        )

    def handle(self, *args, **options):
        handler = getattr(self, options["input_method"])
        handler(options["file"], options["source"], options["mapping"], options["date_format"], options["exclude"])
