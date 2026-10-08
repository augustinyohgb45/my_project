from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0004_remove_incident_destinataires_and_more'),
    ]

    operations = [
        # Les changements existants sont considérés comme déjà notifiés,
        # pour ne pas renvoyer d'anciens e-mails.
        migrations.AddField(
            model_name='changement',
            name='email_envoye',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='changement',
            name='email_envoye',
            field=models.BooleanField(default=False),
        ),
    ]
