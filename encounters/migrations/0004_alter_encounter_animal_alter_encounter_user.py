from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def delete_invalid_encounters(apps, schema_editor):
    Encounter = apps.get_model("encounters", "Encounter")
    Encounter.objects.filter(user=None).delete()
    Encounter.objects.filter(animal=None).delete()

class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('encounters', '0003_animal_deleted_by_cascade_and_more'),
    ]

    operations = [
        migrations.RunPython(delete_invalid_encounters, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='encounter',
            name='animal',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='encounters.animal'),
        ),
        migrations.AlterField(
            model_name='encounter',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL, verbose_name='Handler'),
        ),
    ]
