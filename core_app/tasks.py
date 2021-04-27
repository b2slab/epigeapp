from celery import shared_task
from .pipeline import read_txt_pcr, standard_names, processing_data, run_r_script, mkdir_results, get_classification, \
    get_calibration, standard_data, media_to_static, check_dataframe
from .models import Sample
import os.path


@shared_task
def pipeline(sample_id):
    sample = Sample.objects.get(id=sample_id)
    path_results = mkdir_results(path_to_txt=sample.file.url)
    read_txt_pcr(path_to_read=sample.file.url, path_to_save=path_results)
    get_calibration(path_to_txt=sample.file.url, path_to_results=path_results, sample=sample)
    standard_data(path_folder=path_results)
    standard_names(path_folder=path_results)
    processing_data(path_folder=path_results)
    flag = check_dataframe(path_folder=path_results)
    if not flag:
        run_r_script(path_folder=path_results)
        if os.path.isfile(path_results + 'dataframe_results_lda.csv'):
            get_classification(path_folder=path_results, sample=sample)
        else:
            pass
        media_to_static(path_folder=path_results)
        sample.status = 'classified'
        sample.save()
    else:
        print("Dataframe is incomplete!")


