# Generated by Django 2.1.3 on 2018-11-24 05:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0007_auto_20181124_1211'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='readnum',
            name='blog',
        ),
        migrations.DeleteModel(
            name='ReadNum',
        ),
    ]
