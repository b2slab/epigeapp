from django.db import models


class Sample(models.Model):
    file = models.FileField(upload_to='files/raw_files/')
    submit_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-submit_date',)

    def __str__(self): return self.id
