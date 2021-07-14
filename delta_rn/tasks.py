from celery import shared_task
from core_app.utils import read_txt_pcr, mkdir_results, media_to_static, check_all_data_files, check_all_cpg, \
    get_calibration, run_r_script, send_report
from .models import Sample
from .utils import get_classification


@shared_task(name="analysis_delta_rn_task")
def analysis_and_report(sample_id):
    """
    Task to perform the analysis of a sample and report creation.
    """
    sample = Sample.objects.get(id=sample_id)
    path_results = mkdir_results(path_to_txt=sample.file.url)
    read_txt_pcr(path_to_read=sample.file.url, path_to_save=path_results)
    flag1 = check_all_data_files(path_folder=path_results)
    sample.txt_complete = flag1
    get_calibration(path_to_txt=sample.file.url, path_to_results=path_results, sample=sample, delta_rn=True)
    flag2, message = check_all_cpg(path_folder=path_results)
    sample.all_cpg = flag2
    run_r_script(path_folder=path_results, delta_rn=True)
    get_classification(path_folder=path_results, sample=sample)
    media_to_static(path_folder=path_results)
    sample.status = 1
    sample.save()

    # send_report(sample_id=sample_id)
    return print("DONE!")



