# Generated by Django 3.2.5 on 2021-12-03 11:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clubs', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='member',
            unique_together={('current_user', 'club_membership')},
        ),
    ]