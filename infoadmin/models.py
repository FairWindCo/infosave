import os

from django.db import models

from infosave import settings


# Create your models here.


def barcode_images_path():
    return os.path.join(settings.MEDIA_ROOT, 'barcodes')


def defects_images_path():
    return os.path.join(settings.MEDIA_ROOT, 'barcodes')


class Batch(models.Model):
    code_number = models.CharField(max_length=50)
    rolls_count = models.IntegerField(default=0)
    rolls_processed = models.IntegerField(default=0)
    timestamp_start_process = models.DateTimeField(auto_now_add=True)
    timestamp_end_process = models.DateTimeField(auto_now_add=False, null=True, blank=True)
    bar_code_1 = models.ImageField()
    bar_code_2 = models.ImageField(null=True, blank=True)

    def __str__(self):
        return f'Партия {self.code_number} {self.rolls_count}/{self.rolls_processed}'


class Machines(models.Model):
    name = models.CharField(max_length=50)
    is_use_roll = models.BooleanField(default=False)

    def __str__(self):
        return f'Станок {self.name}'


class Rolls(models.Model):
    code_number = models.CharField(max_length=50, null=True, blank=True)
    cycles = models.IntegerField(default=0)
    timestamp_start_process = models.DateTimeField(auto_now_add=True)
    timestamp_end_process = models.DateTimeField(auto_now_add=False, null=True, blank=True)
    bar_code_1 = models.ImageField(null=True, blank=True)
    bar_code_2 = models.ImageField(null=True, blank=True)
    machine = models.ForeignKey(Machines, on_delete=models.CASCADE)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)

    def __str__(self):
        return f'Рулон {self.code_number} [{self.id}]'


class Defects(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    defect_image_1 = models.ImageField()
    defect_image_2 = models.ImageField()
    roll = models.ForeignKey(Rolls, on_delete=models.CASCADE)
    defect = models.TextField()

    def __str__(self):
        return f'{self.timestamp} {self.defect_image_1} {self.defect_image_2} {self.defect}'
