from django.db import models
import uuid


def sample_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/sample/<id>/data/<filename>
    return 'samples/{0}/data/{1}'.format(instance.id, filename)


class Sample(models.Model):
    STATUS_CHOICES = (
        ('outstanding', 'Outstanding'),
        ('classified', 'Classified'),
        ('error', 'Error'),
    )
    SUBGROUP_CHOICES = (
        ('wnt', 'WNT'),
        ('shh', 'SHH'),
        ('group 3', 'Group 3'),
        ('group 3', 'Group 4'),
        ('non-WNT/non-SHH', 'non-WNT/non-SHH'),
        ('not classified', 'Not classified'),
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
    medulloblastoma_subgroup = models.CharField(max_length=20,
                                                choices=SUBGROUP_CHOICES,
                                                default='not classified')

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return str(self.id)
