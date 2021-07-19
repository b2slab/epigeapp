from celery import shared_task
from .utils import read_txt_pcr, standard_names, processing_data, run_r_script, mkdir_results, get_classification, \
    get_calibration, standard_data, media_to_static, check_amplification_fit, check_all_data_files, check_all_cpg, \
    send_report
from .models import Sample
import os.path
from django.core.mail import EmailMessage


@shared_task(name="analysis_task")
def analysis_and_report(sample_id):
    """
    Task to perform the analysis of a sample and report creation.
    """
    sample = Sample.objects.get(id=sample_id)
    path_results = mkdir_results(path_to_txt=sample.file.path)
    read_txt_pcr(path_to_read=sample.file.path, path_to_save=path_results)
    flag1 = check_all_data_files(path_folder=path_results)
    sample.txt_complete = flag1
    if flag1:
        get_calibration(path_to_txt=sample.file.path, path_to_results=path_results, sample=sample)
        flag2, message = check_all_cpg(path_folder=path_results)
        sample.all_cpg = flag2
        if flag2:
            standard_data(path_folder=path_results)
            standard_names(path_folder=path_results)
            processing_data(path_folder=path_results)
            flag3 = check_amplification_fit(path_folder=path_results)
            sample.amplification_fit = flag3
            if flag3:
                run_r_script(path_folder=path_results)
                if os.path.isfile(path_results / 'dataframe_results_lda.csv'):
                    get_classification(path_folder=path_results, sample=sample)
                else:
                    pass
                media_to_static(path_folder=path_results)
                sample.status = 1111
                sample.save()
            else:
                media_to_static(path_folder=path_results)
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

    send_report(sample_id=sample_id)


@shared_task(name="send_notification")
def analysis_notification(sample_id):
    """
    Task to send an e-mail notification when an sample is successfully created.
    """
    sample = Sample.objects.get(id=sample_id)

    subject = 'EpiGeApp Analysis received'
    message = f"""
    Hello, we just received an analysis with this email!
    
    You will receive another email with your test result in a few minutes.
    If you do not receive the email, please write to us at this email address with the job code of the analysis.
    
    We show you the job code that has been assigned to you below.
    
    Job code: {sample.id}
    Sample identifier: {sample.sample_identifier}
    Created at: {sample.created}
    
    Thank you for using EpiGe App!
    
    EpiGe Team
    """
    email = EmailMessage(subject, message, 'iosullanoviles@gmail.com', [sample.email])
    email.send()
    print("Notification Sent!")

