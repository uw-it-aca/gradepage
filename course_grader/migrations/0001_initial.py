# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Grade',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('section_id', models.CharField(max_length=100)),
                ('student_reg_id', models.CharField(max_length=32)),
                ('duplicate_code', models.CharField(default=b'', max_length=15)),
                ('grade', models.CharField(max_length=100, null=True)),
                ('is_writing', models.BooleanField(default=False)),
                ('is_incomplete', models.BooleanField(default=False)),
                ('no_grade_now', models.BooleanField(default=False)),
                ('import_source', models.CharField(max_length=50, null=True)),
                ('import_grade', models.CharField(max_length=100, null=True)),
                ('comment', models.CharField(max_length=1000, null=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('modified_by', models.CharField(max_length=32)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='GradeImport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('section_id', models.CharField(max_length=100)),
                ('term_id', models.CharField(max_length=20)),
                ('source', models.CharField(max_length=20, choices=[(b'canvas', b'Canvas Gradebook'), (b'catalyst', b'Catalyst GradeBook')])),
                ('source_id', models.CharField(max_length=10, null=True)),
                ('status_code', models.CharField(max_length=3, null=True)),
                ('document', models.TextField()),
                ('imported_date', models.DateTimeField(auto_now=True)),
                ('imported_by', models.CharField(max_length=32)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ImportConversion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('scale', models.CharField(max_length=5, choices=[(b'ug', b'Undergraduate Scale (4.0-0.7)'), (b'gr', b'Graduate Scale (4.0-1.7)'), (b'pf', b'School of Medicine Pass/No Pass'), (b'cnc', b'Credit/No Credit Scale'), (b'hpf', b'Honors/High Pass/Pass/Fail Scale')])),
                ('grade_scale', models.TextField()),
                ('calculator_values', models.TextField(null=True)),
                ('lowest_valid_grade', models.CharField(max_length=5, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SubmittedGradeRoster',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('section_id', models.CharField(max_length=100)),
                ('secondary_section_id', models.CharField(max_length=100, null=True)),
                ('instructor_id', models.CharField(max_length=32)),
                ('term_id', models.CharField(max_length=20)),
                ('submitted_date', models.DateTimeField(auto_now_add=True)),
                ('submitted_by', models.CharField(max_length=32)),
                ('accepted_date', models.DateTimeField(null=True)),
                ('status_code', models.CharField(max_length=3, null=True)),
                ('document', models.TextField()),
                ('catalyst_gradebook_id', models.IntegerField(null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='gradeimport',
            name='import_conversion',
            field=models.ForeignKey(to='course_grader.ImportConversion', on_delete=models.CASCADE, null=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='grade',
            unique_together=set([('section_id', 'student_reg_id', 'duplicate_code', 'modified_by')]),
        ),
    ]
