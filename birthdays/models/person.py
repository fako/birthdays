from __future__ import unicode_literals
import six

import string

from pandas import DataFrame

from django.db import models
from django.contrib.postgres.fields import HStoreField
from django.core.urlresolvers import reverse
from django.conf import settings

from polymorphic import PolymorphicModel, PolymorphicManager

from ontology.models import (
    LastName,
    FirstName,
    Date,
    Year
)


class PersonManager(PolymorphicManager):

    def get_data_frame(self, *args, **kwargs):
        people = super(PersonManager, self).get_queryset(*args, **kwargs)
        data = [
            dict(
                person.props,
                first_name=person.first_name,
                initials=person.initials,
                prefix=person.prefix,
                last_name=person.last_name,
                full_name=person.full_name,
                birth_date=person.birth_date,
                pk=person.pk
            ) for person in people
        ]
        if data:
            columns = ["first_name", "last_name", "full_name", "birth_date", "pk"] + people[0].props.keys()
            return DataFrame(data, columns=columns)
        else:
            return None

    @classmethod
    def register_from_fields(cls, fields, source_model):
        person_source = source_model(
            first_name=fields.pop("first_name", None),
            initials=fields.pop("initials", None),
            prefix=fields.pop("prefix", None),
            last_name=fields.pop("last_name", None),
            full_name=fields.pop("full_name", None),
            birth_date=fields.pop("birth_date", None),
            props=fields
        )

        for attr in ["first_name", "initials", "prefix", "last_name", "full_name"]:
            value = getattr(person_source, attr, None)
            if value is not None and isinstance(value, six.string_types):
                setattr(person_source, attr, value.strip())

        person_source.clean()
        person_source.save()

        if person_source.last_name:
            last_name, created = LastName.objects.get_or_create(name=person_source.last_name)
            last_name.frequency = 1 if created or last_name.frequency is None else last_name.frequency + 1
            last_name.add_source(source_model)
            last_name.clean()
            last_name.save()
        if person_source.first_name:
            first_name, created = FirstName.objects.get_or_create(name=person_source.first_name)
            first_name.frequency = 1 if created or first_name.frequency is None else first_name.frequency + 1
            first_name.add_source(source_model)
            first_name.clean()
            first_name.save()
        if person_source.birth_date:
            date, created = Date.objects.get_or_create(date=person_source.birth_date)
            date.frequency = 1 if created or date.frequency is None else date.frequency + 1
            date.add_source(source_model)
            date.clean()
            date.save()
            year, created = Year.objects.get_or_create(year=person_source.birth_date.year)
            year.frequency = 1 if created or year.frequency is None else year.frequency + 1
            year.add_source(source_model)
            year.clean()
            year.save()

        return person_source


class PersonMixin(object):

    prefixes = [
        "af",
        "aan",
        "bij",
        "de", "den", "der", "d'",
        "het", "'t",
        "in",
        "onder",
        "op",
        "over",
        "'s",
        "'t",
        "te", "ten", "ter",
        "tot",
        "uit", "uijt",
        "van", "vanden",
        "ver",
        "voor",
        "a",
        "al",
        "am",
        "auf",
        "aus",
        "ben", "bin",
        "da",
        "dal", "dalla", "della",
        "das", "die", "den", "der", "des",
        "deca",
        "degli",
        "dei",
        "del",
        "di",
        "do",
        "don",
        "dos",
        "du",
        "el",
        "i",
        "im",
        "L",
        "la", "las",
        "le", "les",
        "lo", "los",
        "o'",
        "tho", "thoe", "thor", "to", "toe",
        "unter",
        "vom", "von",
        "vor",
        "zu", "zum", "zur",
    ]

    def fill_full_name(self, force=False):
        if (self.first_name and self.last_name and not self.full_name) or force:
            if not self.prefix:
                self.full_name = "{} {}".format(self.first_name, self.last_name)
            else:
                self.full_name = "{} {} {}".format(self.first_name, self.prefix, self.last_name)

    def split_full_name(self, force=False):

        if (not self.full_name or (self.first_name and self.last_name)) and not force:
            return
        translate_table = dict((ord(char), " ", ) for char in "-,()@&")
        names = [
            name for name in self.full_name.translate(translate_table).split(" ")
            if name
        ]
        if not len(names) > 1:
            return

        if len(names) == 2:
            self.first_name, self.last_name = names
            if self.is_real_last_name(self.last_name):
                self.save()
            return  # early return prevents indentation, which is easier to read IMO

        # prefix check
        pos_prefix = []
        for name in names:
            if name in self.prefixes:
                pos_prefix.append(names.index(name))  # append is not functional in Python and always returns None (aka null)

        # split with single first name and prefix
        if len(pos_prefix) and pos_prefix[0] == 1:
            self.first_name = " ".join(names[:1]).strip()
            self.last_name = " ".join(names[1:]).strip()
            self.prefix = " ".join(name for i, name in enumerate(names) if i in pos_prefix).strip()
            if self.is_real_last_name(self.last_name):
                self.save()

        # split with double first name or double last name or both
        else:

            reversed_names = list(reversed(names))
            found_last_names = []
            for i, name in enumerate(names):

                possible_last_name = " ".join(
                    reversed(reversed_names[:i+1])  # starting from the end we take increasingly more names as we loop
                )
                if self.is_real_last_name(possible_last_name):
                    found_last_names.append(possible_last_name)
                    reversed_names = reversed_names[i+1:]  # after storage of the name we cut out the names we included in our found name
                    continue  # explicitly continue with finding second last names, possibly problematic with first names like last names, break instead?

            if found_last_names:
                # for now we'll store double last names and first names together in one field, so we only need one split
                split_pos = self.full_name.find(found_last_names[-1])
                self.first_name = self.full_name[:split_pos].strip()
                self.last_name = self.full_name[split_pos:].strip()
                # we can only really store prefixes with single last names
                if len(found_last_names) == 1:
                    self.prefix = " ".join(name for i, name in enumerate(names) if i in pos_prefix).strip()
                self.save()

        return

    @staticmethod
    def is_real_last_name(last_name_check):
        from birthdays.models import PhoneBookSource  # inline import to prevent circular imports
        return PhoneBookSource.objects.filter(last_name__iexact=last_name_check).exists()  # case-insensitive db query for the name in PhoneBook records

    def __unicode__(self):
        return "{} {}".format(self.__class__.__name__, self.id)


class Person(PersonMixin, models.Model):

    first_name = models.CharField(max_length=128, db_index=True, null=True, blank=True)
    initials = models.CharField(max_length=20, db_index=True, null=True, blank=True)
    prefix = models.CharField(max_length=20, db_index=True, null=True, blank=True)
    last_name = models.CharField(max_length=128, db_index=True, null=True, blank=True)
    full_name = models.CharField(max_length=256, db_index=True, null=True, blank=True)
    city = models.CharField(max_length=256, db_index=True, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True, db_index=True)

    props = HStoreField()


class PersonSource(PersonMixin, PolymorphicModel):

    objects = PersonManager()

    first_name = models.CharField(max_length=128, db_index=True, null=True, blank=True)
    initials = models.CharField(max_length=20, db_index=True, null=True, blank=True)
    prefix = models.CharField(max_length=20, db_index=True, null=True, blank=True)
    last_name = models.CharField(max_length=128, db_index=True, null=True, blank=True)
    full_name = models.CharField(max_length=256, db_index=True, null=True, blank=True)
    city = models.CharField(max_length=256, db_index=True, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True, db_index=True)

    props = HStoreField()
    master = models.ForeignKey(Person, null=True, blank=True, related_name="sources")

    def save(self, *args, **kwargs):
        if self.first_name and self.last_name and not self.full_name:
            self.fill_full_name()
        if self.full_name and (not self.first_name or not self.last_name):
            self.split_full_name()
        super(PersonSource, self).save(*args, **kwargs)

    def get_uri(self):
        admin_view_name = "admin:birthdays_{}_change".format(self._meta.model_name)
        admin_url = reverse(admin_view_name, args=(self.id,))
        return "{}{}".format(settings.BIRTHDAYS_DOMAIN, admin_url)
