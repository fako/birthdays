from __future__ import unicode_literals, absolute_import, print_function, division

from django.apps import apps as django_apps
from django.core.management.base import BaseCommand

from ontology.models import OntologyItem


class Command(BaseCommand):
    """
    Command to created canonic entities
    """

    @staticmethod
    def slugs(ontology_type):
        for item in ontology_type.objects.all():
            item.clean()
            item.save()

    @staticmethod
    def split_name(ontology_type):
        deletes = []
        for item in ontology_type.objects.filter(name__contains=" "):
            for name in item.name.split(" "):
                obj, created = ontology_type.objects.get_or_create(name=name)
                for source in item.sources:
                    if source not in obj.sources:
                        obj.sources.append(source)
                obj.clean()
                obj.save()
            deletes.append(item.id)
        ontology_type.objects.filter(id__in=deletes).delete()

    def add_arguments(self, parser):
        parser.add_argument(
            'update_type',
            type=unicode,
            help="The update method. Either 'slugs' or 'frequency'."
        )
        parser.add_argument(
            '-o', '--ontology',
            type=unicode,
            help="The ontology type to update"
        )

    def handle(self, *args, **options):
        ontology_type = django_apps.get_model(app_label="ontology", model_name=options["ontology"])
        assert issubclass(ontology_type, OntologyItem), "Specified ontology type {} is not a subclass of OntologyItem".format(options["ontology"])
        handler = getattr(self, options["update_type"])
        handler(ontology_type)