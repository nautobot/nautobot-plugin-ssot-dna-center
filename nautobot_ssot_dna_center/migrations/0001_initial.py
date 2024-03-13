# Generated by Django 3.2.23 on 2024-01-04 15:46

import django.core.serializers.json
from django.db import migrations, models
import django.db.models.deletion
import nautobot.core.models.fields
import nautobot.extras.models.mixins
import uuid


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("extras", "0102_set_null_objectchange_contenttype"),
        ("tenancy", "0008_tagsfield"),
    ]

    operations = [
        migrations.CreateModel(
            name="DNACInstance",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True
                    ),
                ),
                ("created", models.DateTimeField(auto_now_add=True, null=True)),
                ("last_updated", models.DateTimeField(auto_now=True, null=True)),
                (
                    "_custom_field_data",
                    models.JSONField(blank=True, default=dict, encoder=django.core.serializers.json.DjangoJSONEncoder),
                ),
                ("name", models.CharField(max_length=100, unique=True)),
                ("description", models.CharField(blank=True, max_length=200)),
                ("host_url", models.CharField(blank=True, max_length=255)),
                ("port", models.IntegerField(default=443)),
                ("verify", models.BooleanField(default=True)),
                (
                    "auth_group",
                    models.ForeignKey(
                        blank=True,
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="extras.secretsgroup",
                    ),
                ),
                ("tags", nautobot.core.models.fields.TagsField(through="extras.TaggedItem", to="extras.Tag")),
                (
                    "tenant",
                    models.ForeignKey(
                        blank=True,
                        default=None,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to="tenancy.tenant",
                    ),
                ),
            ],
            options={
                "verbose_name": "DNA Center Instance",
                "verbose_name_plural": "DNA Center Instances",
                "ordering": ["name"],
            },
            bases=(
                models.Model,
                nautobot.extras.models.mixins.DynamicGroupMixin,
                nautobot.extras.models.mixins.NotesMixin,
            ),
        ),
    ]
