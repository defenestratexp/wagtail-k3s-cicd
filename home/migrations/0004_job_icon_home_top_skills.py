from django.db import migrations, models
import wagtail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0003_skill_links'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='icon',
            field=models.CharField(blank=True, help_text="Font Awesome class for the home-page job row, e.g. 'fa-solid fa-car-side'", max_length=50),
        ),
        migrations.AddField(
            model_name='homepage',
            name='top_skills',
            field=wagtail.fields.RichTextField(blank=True, help_text='Short bulleted list of the top skills, shown under the intro'),
        ),
    ]
