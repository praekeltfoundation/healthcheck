from django.contrib.gis.db import models
from django.db.models import Manager as GeoManager
from django.contrib.gis.geos import Point
from django.utils import timezone


class Location(models.Model):
    name = models.CharField(max_length=100)
    location = models.PointField(geography=True, srid=4326)
    longitude = models.FloatField()
    latitude = models.FloatField()
    province = models.CharField(max_length=50)
    code = models.CharField(max_length=50, primary_key=True)
    short_name = models.CharField(max_length=100)
    address = models.CharField(max_length=255, null=True)
    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(default=timezone.now, editable=True)

    objects = GeoManager()

    def save(self, **kwargs):
        self.location = Point(self.longitude, self.latitude)
        super(Location, self).save(**kwargs)
