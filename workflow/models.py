from django.db import models
import uuid
import os
from django.conf import settings
import pandas as pd
import numpy as np

media_root = settings.MEDIA_ROOT


def sample_directory_path(instance, filename):
    return 'samples/{0}/data/{1}'.format(instance.id, filename)


class Sample(models.Model):
    PENDING = 0
    CLASSIFIED = 1
    STATUS = (
        (PENDING, 'Pending'),
        (CLASSIFIED, 'Classified'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField()
    sample_identifier = models.CharField(max_length=25)
    diagnosis = models.CharField(max_length=25)
    created = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to=sample_directory_path)

    status = models.PositiveSmallIntegerField(choices=STATUS, default=PENDING)
    txt_complete = models.BooleanField(default=False)
    all_cpg = models.BooleanField(default=False)
    missing_cpg = models.CharField(max_length=25, default='', null=True, blank=True)

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
    subgroup = models.CharField(max_length=20, choices=SUBGROUP_CHOICES, default='Not classified')
    score_wnt = models.FloatField(default=0)
    score_shh = models.FloatField(default=0)
    score_gg = models.FloatField(default=0)

    def __str__(self):
        return str(self.sample.id)

    @property
    def sample_image(self):
        return '/static/samples/{0}/table_sample.png'.format(self.sample)

    @property
    def radar_plot(self):
        return '/static/samples/{0}/radar_plot.png'.format(self.sample)

    @property
    def logistic_table(self):
        path_cms = '{0}/samples/{1}/results/probability_dataframe.csv'.format(media_root, self.sample)
        data = pd.read_csv(path_cms)
        return data.to_html(index=False)


class Calibration(models.Model):
    sample = models.OneToOneField(Sample, on_delete=models.CASCADE, editable=False)
    ROX_valid = models.BooleanField()
    FAM_valid = models.BooleanField()
    VIC_valid = models.BooleanField()
    ROX_date = models.CharField(max_length=25)
    FAM_date = models.CharField(max_length=25)
    VIC_date = models.CharField(max_length=25)
    amplification_test = models.BooleanField()
    instrument_type = models.CharField(max_length=75)

    def __str__(self):
        return str(self.sample.id)

    @property
    def amplification_table(self):
        path_results = '{0}/samples/{1}/results/Results.csv'.format(media_root, self.sample)
        df = pd.read_csv(path_results, sep="\t")
        df_ntc = df.query("Task == 'NTC'")
        df_ntc = df_ntc[['Well Position', 'SNP Assay Name', 'Allele1 Ct', 'Allele2 Ct']]
        return df_ntc.to_html(index=False)

    @property
    def standard_deviation_dataframe(self):
        names = ['S1_1033', 'S3_1292', 'W1_2554', 'W3_0222', 'G1_1884', 'G3_0126']
        std1 = []
        std2 = []
        snp_name = []

        path_results = '{0}/samples/{1}/results/Results.csv'.format(media_root, self.sample)
        dummy = pd.read_csv(path_results, sep="\t")
        dummy = dummy.iloc[dummy.Task.values == "UNKNOWN", ]
        dummy = dummy.replace({'Allele1 Ct': 'Undetermined', 'Allele2 Ct': 'Undetermined'}, 40)

        allele1 = dummy["Allele1 Ct"].values
        allele1 = allele1.astype(float)

        allele2 = dummy["Allele2 Ct"].values
        allele2 = allele2.astype(float)
        for name in names:
            snp_name.append(name)
            v = dummy["SNP Assay Name"].values == name
            std1.append(round(np.std(allele1[v]), 4))
            std2.append(round(np.std(allele2[v]), 4))

        results = pd.DataFrame(list(zip(snp_name, std1, std2)),
                               columns=['SNP Assay Name', 'Allele1 Ct Std', 'Allele2 Ct Std'])

        return results


    @property
    def standard_deviation_table(self):
        results = self.standard_deviation_dataframe
        return results.to_html(index=False)

    @property
    def standard_deviation_test(self):
        results = self.standard_deviation_dataframe
        if any(results['Allele1 Ct Std'] > 0.5) | any(results['Allele2 Ct Std'] > 0.5):
            return True
        return False

