# Generated by Django 3.2.1 on 2021-05-10 06:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('File', '0005_alter_filingcase_remark'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectteam',
            name='remark',
            field=models.CharField(max_length=255, null=True, verbose_name='备注'),
        ),
    ]
