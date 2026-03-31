from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0025_alter_expression_audio'),
    ]

    operations = [
        migrations.AlterField(
            model_name='blogpost',
            name='slug',
            field=models.SlugField(blank=True, max_length=250, unique=True),
        ),
    ]
