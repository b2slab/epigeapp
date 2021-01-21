from django.db import models
import uuid


def sample_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'data/sample_{0}/{1}'.format(instance.id, filename)


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
    file = models.FileField(upload_to='data/%Y/%m/%d/')
    status = models.CharField(max_length=20,
                              choices=STATUS_CHOICES,
                              default='outstanding')

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return self.sample_identifier + ' from: ' + self.email
