from django.db import models

# Create your models here.
class Detections (models.Model):
    id = models.AutoField(primary_key=True)
    ref_img = models.TextField()
    placa = models.TextField()
    date = models.DateField(auto_now=True)
