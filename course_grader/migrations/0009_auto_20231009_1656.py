# Generated by Django 3.2.22 on 2023-10-09 23:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course_grader', '0008_auto_20211103_1911'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gradeimport',
            name='source',
            field=models.CharField(choices=[('canvas', 'Canvas Gradebook'), ('catalyst', 'Catalyst Gradebook'), ('csv', 'CSV File')], max_length=20),
        ),
        migrations.AddIndex(
            model_name='grade',
            index=models.Index(fields=['section_id', 'modified_by'], name='course_grad_section_fdf9ae_idx'),
        ),
        migrations.AddIndex(
            model_name='gradeimport',
            index=models.Index(fields=['term_id'], name='course_grad_term_id_dd39ee_idx'),
        ),
        migrations.AddIndex(
            model_name='submittedgraderoster',
            index=models.Index(fields=['secondary_section_id'], name='course_grad_seconda_c11485_idx'),
        ),
        migrations.AddIndex(
            model_name='submittedgraderoster',
            index=models.Index(fields=['section_id'], name='course_grad_section_3de2a4_idx'),
        ),
        migrations.AddIndex(
            model_name='submittedgraderoster',
            index=models.Index(fields=['term_id'], name='course_grad_term_id_b59da5_idx'),
        ),
        migrations.AddIndex(
            model_name='submittedgraderoster',
            index=models.Index(fields=['accepted_date'], name='course_grad_accepte_536d57_idx'),
        ),
    ]