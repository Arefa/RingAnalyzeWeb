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


class DetailResult(models.Model):
    ring_name = models.CharField(max_length=100)
    ne_num = models.CharField(max_length=100)
    bar_ne = models.TextField(max_length=1000)
    cne_point = models.CharField(max_length=100)
    bcne_cne = models.CharField(max_length=100)
    lsc_num = models.CharField(max_length=100)
    lsc_ne = models.TextField(max_length=1000)
    arr = models.CharField(max_length=100)
    arr_ne = models.TextField(max_length=1000)
    dr = models.CharField(max_length=100)
    arp = models.TextField(max_length=1000)
    msg = models.CharField(max_length=500)

    def __str__(self):
        return "%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s" % (
            self.ring_name, self.ne_num, self.bar_ne, self.cne_point, self.bcne_cne, self.lsc_num, self.lsc_ne,
            self.arr, self.arr_ne, self.dr, self.arp, self.msg)


class RingTable(models.Model):
    region = models.CharField(max_length=100)
    ring_name = models.CharField(max_length=100)
    arp = models.CharField(max_length=1000)
    arp_nbr = models.CharField(max_length=100)
    is_big_ring = models.CharField(max_length=10)

    def __str__(self):
        return "%s, %s, %s, %s, %s" % (self.region, self.ring_name, self.arp, self.arp_nbr, self.is_big_ring)


class CneTable(models.Model):
    region = models.CharField(max_length=100)
    cne_name = models.CharField(max_length=100)
    cne_nenbr = models.CharField(max_length=100)
    is_big_cne = models.CharField(max_length=10)

    def __str__(self):
        return "%s, %s, %s, %s" % (self.region, self.cne_name, self.cne_nenbr, self.is_big_cne)


class NeTable(models.Model):
    region = models.CharField(max_length=100)
    ne_name = models.CharField(max_length=100)
    is_ring = models.CharField(max_length=10)
    is_double_arrive = models.CharField(max_length=10)

    def __str__(self):
        return "%s, %s, %s, %s" % (self.region, self.ne_name, self.is_ring, self.is_double_arrive)


class LongSingleTable(models.Model):
    region = models.CharField(max_length=100)
    longsinglepath = models.CharField(max_length=1000)
    nbr = models.CharField(max_length=100)

    def __str__(self):
        return "%s, %s, %s" % (self.region, self.longsinglepath, self.nbr)

# # big access ring
# class BAR(models.Model):
#     ring_name = models.CharField(max_length=100)
#     ne_num = models.CharField(max_length=100)
#     bar_ne = models.TextField(max_length=1000)
#
#     def __str__(self):
#         return "%s, %s, %s" % (self.ring_name, self.ne_num, self.bar_ne)
#
#
# # big converge ne
# class BCNE(models.Model):
#     ring_name = models.CharField(max_length=100)
#     cne_point = models.CharField(max_length=100)
#     bcne_cne = models.CharField(max_length=100)
#
#     def __str__(self):
#         return "%s, %s, %s" % (self.ring_name, self.ne_num, self.bcne_cne)
#
#
# # long single chain
# class LSC(models.Model):
#     ring_name = models.CharField(max_length=100)
#     lsc_num = models.CharField(max_length=100)
#     lsc_ne = models.TextField(max_length=1000)
#
#     def __str__(self):
#         return "%s, %s, %s" % (self.ring_name, self.lsc_num, self.lsc_ne)
#
#
# # access ring rate
# class ARR(models.Model):
#     ring_name = models.CharField(max_length=100)
#     arr = models.CharField(max_length=100)
#     arr_ne = models.TextField(max_length=1000)
#
#     def __str__(self):
#         return "%s, %s, %s" % (self.ring_name, self.arr, self.arr_ne)
#
#
# # double rate
# class DR(models.Model):
#     ring_name = models.CharField(max_length=100)
#     dr = models.CharField(max_length=100)
#
#     def __str__(self):
#         return "%s, %s" % (self.ring_name, self.dr)
#
#
# # access ring path
# class ARP(models.Model):
#     ring_name = models.CharField(max_length=100)
#     arp = models.TextField(max_length=1000)
#
#     def __str__(self):
#         return "%s, %s" % (self.ring_name, self.arp)
#
#
# #
class Result(models.Model):
    total_arr = models.CharField(max_length=100)
    total_dr = models.CharField(max_length=100)

    def __str__(self):
        return "%s, %s" % (self.total_arr, self.total_dr)

#
#
# class ErrorMsg(models.Model):
#     ring_name = models.CharField(max_length=100)
#     msg = models.CharField(max_length=500)
#
#     def __str__(self):
#         return "%s, %s" % (self.ring_name, self.msg)
