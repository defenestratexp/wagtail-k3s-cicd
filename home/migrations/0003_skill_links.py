import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_projectpage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='skill',
            name='percentage',
            field=models.IntegerField(blank=True, help_text='Unused: the proficiency bars were replaced by project and job links', null=True, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)]),
        ),
        migrations.AddField(
            model_name='skill',
            name='match_tags',
            field=models.CharField(blank=True, help_text="Comma-separated project technology tags that also count as this skill (the skill name itself always counts), e.g. 'Amazon ECR, AWS Secrets Manager' for AWS", max_length=300),
        ),
        migrations.AddField(
            model_name='skill',
            name='related_jobs',
            field=models.ManyToManyField(blank=True, help_text='Jobs shown for this skill when no project is tagged with it', related_name='skills', to='home.job'),
        ),
    ]
