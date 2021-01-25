from celery import shared_task
from .pipeline import read_txt_pcr, standard_names, processing_data, run_r_script


@shared_task
def pipeline(path_txt):
    path_results = read_txt_pcr(path_txt=path_txt)
    standard_names(path_results)
    processing_data(path_results)
    result = run_r_script(path_results)
    return print(result)
