# Generated by Django 3.2.1 on 2021-05-29 15:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0005_user_avatar_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='face_verification',
            field=models.BooleanField(default=0, verbose_name='是否人脸认证了'),
        ),
    ]
