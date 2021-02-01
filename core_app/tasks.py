from celery import shared_task
from .pipeline import read_txt_pcr, standard_names, processing_data, run_r_script, mkdir_results, create_qc_table
from .models import Sample


@shared_task
def pipeline(sample_id):
    sample = Sample.objects.get(id=sample_id)
    path_results = mkdir_results(path_to_txt=sample.file.url)
    read_txt_pcr(path_to_read=sample.file.url, path_to_save=path_results)
    standard_names(path_folder=path_results)
    processing_data(path_folder=path_results)
    run_r_script(path_folder=path_results)
    create_qc_table(path_folder=path_results, sample=sample)
    sample.status = 'classified'
    sample.save()

