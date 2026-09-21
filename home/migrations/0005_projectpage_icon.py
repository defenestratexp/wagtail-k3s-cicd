from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0004_job_icon_home_top_skills'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectpage',
            name='icon',
            field=models.CharField(blank=True, help_text="Font Awesome class for the home-page project row, e.g. 'fa-solid fa-radio'", max_length=50),
        ),
        migrations.AddField(
            model_name='projectpage',
            name='short_name',
            field=models.CharField(blank=True, help_text='Short label for the home-page project row (defaults to the page title)', max_length=40),
        ),
    ]
