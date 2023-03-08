# Generated by Django 3.2.1 on 2021-05-05 12:45

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Role',
            fields=[
                ('_id', models.IntegerField(db_column='id', primary_key=True, serialize=False, verbose_name='角色编号')),
                ('name', models.CharField(max_length=255, verbose_name='角色名称')),
            ],
            options={
                'db_table': 'DMS_roles',
            },
        ),
    ]