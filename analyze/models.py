from __future__ import unicode_literals

from django.db import models


class NetworkElement(models.Model):
    ne_name = models.CharField(max_length=100)
    ne_type = models.CharField(max_length=10)
    ring_name = models.CharField(max_length=100)
    ring_region = models.CharField(max_length=10)

    def __str__(self):
        return self.ne_name


class FiberRelationship(models.Model):
    source = models.CharField(max_length=100)
    target = models.CharField(max_length=100)
    edge_weight = models.IntegerField()

    def __str__(self):
        return self.source
