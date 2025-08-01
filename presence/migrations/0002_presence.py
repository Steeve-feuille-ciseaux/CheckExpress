# Generated by Django 5.2.4 on 2025-07-17 07:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('presence', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Presence',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now_add=True)),
                ('present', models.BooleanField(default=False)),
                ('licence', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='presence.licence')),
            ],
        ),
    ]
