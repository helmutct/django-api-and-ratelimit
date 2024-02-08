from django.db import models

class Consumer(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    street = models.CharField(max_length=255)
    status = models.CharField(max_length=100)
    previous_jobs_count = models.PositiveIntegerField()
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    lat = models.FloatField()
    lng = models.FloatField()

    class Meta:
        db_table = 'consumer'
