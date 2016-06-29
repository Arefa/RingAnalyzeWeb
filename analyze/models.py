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


# big access ring
class BAR(models.Model):
    ring_name = models.CharField(max_length=100)
    ne_num = models.CharField(max_length=100)
    bar_ne = models.TextField(max_length=1000)

    def __str__(self):
        return "%s, %s, %s" % (self.ring_name, self.ne_num, self.bar_ne)


# big converge ne
class BCNE(models.Model):
    ring_name = models.CharField(max_length=100)
    cne_point = models.CharField(max_length=100)
    bcne_cne = models.CharField(max_length=100)

    def __str__(self):
        return "%s, %s, %s" % (self.ring_name, self.ne_num, self.bcne_cne)


# long single chain
class LSC(models.Model):
    ring_name = models.CharField(max_length=100)
    lsc_num = models.CharField(max_length=100)
    lsc_ne = models.TextField(max_length=1000)

    def __str__(self):
        return "%s, %s, %s" % (self.ring_name, self.lsc_num, self.lsc_ne)


# access ring rate
class ARR(models.Model):
    ring_name = models.CharField(max_length=100)
    arr = models.CharField(max_length=100)
    arr_ne = models.TextField(max_length=1000)

    def __str__(self):
        return "%s, %s, %s" % (self.ring_name, self.arr, self.arr_ne)


# double rate
class DR(models.Model):
    ring_name = models.CharField(max_length=100)
    dr = models.CharField(max_length=100)

    def __str__(self):
        return "%s, %s" % (self.ring_name, self.dr)


# access ring path
class ARP(models.Model):
    ring_name = models.CharField(max_length=100)
    arp = models.TextField(max_length=1000)

    def __str__(self):
        return "%s, %s" % (self.ring_name, self.arp)


#
class Result(models.Model):
    total_arr = models.CharField(max_length=100)
    total_dr = models.CharField(max_length=100)

    def __str__(self):
        return "%s, %s" % (self.total_arr, self.total_dr)


class ErrorMsg(models.Model):
    ring_name = models.CharField(max_length=100)
    msg = models.CharField(max_length=500)

    def __str__(self):
        return "%s, %s" % (self.ring_name, self.msg)
