from __future__ import unicode_literals

from django.db import models


class NetworkElement(models.Model):
    ne_name = models.CharField(max_length=100)
    ne_type = models.CharField(max_length=100)
    ring_name = models.CharField(max_length=100)
    ring_region = models.CharField(max_length=10)

    def __str__(self):
        return "%s, %s, %s, %s" % (self.ne_name, self.ne_type, self.ring_name, self.ring_region)
        # return self.ne_name


class FiberRelationship(models.Model):
    source = models.CharField(max_length=100)
    target = models.CharField(max_length=100)
    edge_weight = models.CharField(max_length=100)

    def __str__(self):
        return "%s, %s, %s" % (self.source, self.target, self.edge_weight)


class ConvergeNE(models.Model):
    cne_name = models.CharField(max_length=100)
    cne_type = models.CharField(max_length=100)
    ring_name = models.CharField(max_length=100)
    ring_region = models.CharField(max_length=10)

    def __str__(self):
        return "%s, %s, %s, %s" % (self.cne_name, self.cne_type, self.ring_name, self.ring_region)

