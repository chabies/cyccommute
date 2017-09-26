# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-09-26 08:20
from __future__ import unicode_literals

from django.conf import settings
import django.contrib.gis.db.models.fields
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='OsmWayClasses',
            fields=[
                ('class_id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.TextField(blank=True, null=True)),
                ('priority', models.FloatField(blank=True, null=True)),
                ('default_maxspeed', models.IntegerField(blank=True, null=True)),
            ],
            options={
                'db_table': 'osm_way_classes',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='OsmWayTypes',
            fields=[
                ('type_id', models.IntegerField(primary_key=True, serialize=False)),
                ('name', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'osm_way_types',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Ways',
            fields=[
                ('gid', models.BigAutoField(primary_key=True, serialize=False)),
                ('length', models.FloatField(blank=True, null=True)),
                ('length_m', models.FloatField(blank=True, null=True)),
                ('name', models.TextField(blank=True, null=True)),
                ('x1', models.FloatField(blank=True, null=True)),
                ('y1', models.FloatField(blank=True, null=True)),
                ('x2', models.FloatField(blank=True, null=True)),
                ('y2', models.FloatField(blank=True, null=True)),
                ('osm_id', models.BigIntegerField(blank=True, null=True)),
                ('source_osm', models.BigIntegerField(blank=True, null=True)),
                ('target_osm', models.BigIntegerField(blank=True, null=True)),
                ('priority', models.FloatField(blank=True, null=True)),
                ('the_geom', django.contrib.gis.db.models.fields.LineStringField(blank=True, null=True, srid=4326)),
            ],
            options={
                'db_table': 'ways',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='GPXFile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filename', models.FileField(upload_to=b'')),
                ('segments', models.TextField(null=True)),
                ('user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='GPXPoint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('point', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('timestamp', models.DateTimeField()),
                ('gpxfile', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='analytics.GPXFile')),
                ('user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='MatchingPoint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('point', django.contrib.gis.db.models.fields.PointField(srid=4326)),
                ('gpxfile', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='analytics.GPXFile')),
                ('user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Route',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('route_id', models.IntegerField()),
                ('route_counts', models.IntegerField()),
                ('route_color', models.TextField()),
                ('route_tt', models.IntegerField()),
                ('user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SegmentCounts',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('segment_id', models.IntegerField()),
                ('segment_counts', models.IntegerField()),
                ('user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SegmentGeoJSON',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('geojson', django.contrib.postgres.fields.jsonb.JSONField()),
                ('gpxfile', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='analytics.GPXFile')),
                ('user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ZIPGPX',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('filename', models.FileField(upload_to=b'')),
                ('user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
