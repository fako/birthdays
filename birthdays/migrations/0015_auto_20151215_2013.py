# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('birthdays', '0014_hobbyjournalsource'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='city',
            field=models.CharField(db_index=True, max_length=256, null=True, blank=True),
        ),
        migrations.AddField(
            model_name='personsource',
            name='city',
            field=models.CharField(db_index=True, max_length=256, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='birth_date',
            field=models.DateField(db_index=True, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='personsource',
            name='birth_date',
            field=models.DateField(db_index=True, null=True, blank=True),
        ),
    ]
