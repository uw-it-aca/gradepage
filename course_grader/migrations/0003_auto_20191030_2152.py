# Generated by Django 2.0.13 on 2019-10-30 21:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course_grader', '0002_auto_20191021_2223'),
    ]

    operations = [
        migrations.AddField(
            model_name='importconversion',
            name='course_id',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='importconversion',
            name='course_name',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='importconversion',
            name='grading_standard_id',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='importconversion',
            name='grading_standard_name',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
