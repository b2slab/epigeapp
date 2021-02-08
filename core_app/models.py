from django.db import models
import uuid
import os


def sample_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/sample/<id>/data/<filename>
    return 'samples/{0}/data/{1}'.format(instance.id, filename)


class Sample(models.Model):
    STATUS_CHOICES = (
        ('outstanding', 'Outstanding'),
        ('classified', 'Classified'),
        ('error', 'Error'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField()
    sample_identifier = models.CharField(max_length=25)
    diagnosis = models.CharField(max_length=25)
    created = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to=sample_directory_path)
    status = models.CharField(max_length=20,
                              choices=STATUS_CHOICES,
                              default='outstanding')

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return str(self.id)

    @property
    def filename(self):
        return os.path.basename(self.file.name)

    @property
    def filesize(self):
        x = self.file.size
        y = 512000
        if x < y:
            value = round(x / 1000, 2)
            ext = ' kb'
        elif x < y * 1000:
            value = round(x / 1000000, 2)
            ext = ' Mb'
        else:
            value = round(x / 1000000000, 2)
            ext = ' Gb'
        return str(value) + ext


class Classification(models.Model):
    SUBGROUP_CHOICES = (
        ('WNT', 'WNT'),
        ('SHH', 'SHH'),
        ('non-WNT/non-SHH', 'non-WNT/non-SHH'),
        ('Not classified', 'Not classified'),
    )

    sample = models.OneToOneField(Sample, on_delete=models.CASCADE, editable=False)
    subgroup = models.CharField(max_length=20,
                                choices=SUBGROUP_CHOICES,
                                default='Not classified')
    WNT_probability = models.FloatField(null=True)
    SHH_probability = models.FloatField(null=True)
    G3_G4_probability = models.FloatField(null=True)
    CMS_table = models.TextField(null=True)

    def __str__(self):
        return str(self.sample.id)


class Calibration(models.Model):
    sample = models.OneToOneField(Sample, on_delete=models.CASCADE, editable=False)
    ROX_valid = models.BooleanField()
    FAM_valid = models.BooleanField()
    VIC_valid = models.BooleanField()
    ROX_date = models.CharField(max_length=25)
    FAM_date = models.CharField(max_length=25)
    VIC_date = models.CharField(max_length=25)
    amplification_test = models.BooleanField()
    amplification_table = models.TextField(null=True)
    instrument_type = models.CharField(max_length=75)

    def __str__(self):
        return str(self.sample.id)
