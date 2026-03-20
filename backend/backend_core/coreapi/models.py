from django.db import models


class OptionSnapshot(models.Model):
    symbol = models.CharField(max_length=20)
    strike = models.FloatField()

    ltp = models.FloatField(null=True, blank=True)
    call_oi = models.FloatField(null=True, blank=True)
    put_oi = models.FloatField(null=True, blank=True)

    iv = models.FloatField(null=True, blank=True)

    delta = models.FloatField(null=True, blank=True)
    theta = models.FloatField(null=True, blank=True)
    gamma = models.FloatField(null=True, blank=True)
    vega = models.FloatField(null=True, blank=True)

    expiry = models.CharField(max_length=30, null=True, blank=True)

    captured_at = models.DateTimeField(auto_now_add=True)