from celery import shared_task
from .pipeline import read_txt_pcr, standard_names, processing_data, run_r_script, mkdir_results, get_classification, \
    get_calibration, standard_data, media_to_static, check_amplification_fit, check_all_data_files, check_all_cpg
from .models import Sample
import os.path


@shared_task
def pipeline(sample_id):
    sample = Sample.objects.get(id=sample_id)
    path_results = mkdir_results(path_to_txt=sample.file.url)
    read_txt_pcr(path_to_read=sample.file.url, path_to_save=path_results)
    flag1 = check_all_data_files(path_folder=path_results)
    sample.txt_complete = flag1
    if flag1:
        get_calibration(path_to_txt=sample.file.url, path_to_results=path_results, sample=sample)
        flag2, message = check_all_cpg(path_folder=path_results)
        sample.all_cpg = flag2
        if flag2:
            standard_data(path_folder=path_results)
            standard_names(path_folder=path_results)
            processing_data(path_folder=path_results)
            flag3 = check_amplification_fit(path_folder=path_results)
            sample.dataframe_complete = flag3
            if flag3:
                run_r_script(path_folder=path_results)
                if os.path.isfile(path_results + 'dataframe_results_lda.csv'):
                    get_classification(path_folder=path_results, sample=sample)
                else:
                    pass
                media_to_static(path_folder=path_results)
                sample.status = 1111
                sample.save()
            else:
                print("Some of the wells do not have sufficient amplification!")
                sample.status = 3
                sample.save()
        else:
            print("Some CpGs are missing!")
            sample.missing_cpg = message
            sample.status = 2
            sample.save()
    else:
        print("Txt file is incomplete!")
        sample.status = 1
        sample.save()


