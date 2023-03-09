from celery import shared_task
from .models import Sample
from .functions import get_classification, send_report, fixing_radar_plot, get_calibration, call_r_functions, \
    read_txt_pcr, mkdir_results, media_to_static, check_all_data_files, check_all_cpg
from django.core.mail import EmailMessage
import time
from time import process_time



@shared_task(name="analysis_workflow")
def analysis_and_report(sample_id, base_url):
    """
    Task to perform the analysis of a sample and report creation.
    """
    t1_start = process_time()
    sample = Sample.objects.get(id=sample_id)
    path_results = mkdir_results(path_to_txt=sample.file.path)
    read_txt_pcr(path_to_read=sample.file.path, path_to_save=path_results)
    flag1 = check_all_data_files(path_folder=path_results)
    if flag1:
        sample.txt_complete = flag1
        get_calibration(path_to_txt=sample.file.path, path_to_results=path_results, sample=sample)
        flag2, message = check_all_cpg(path_folder=path_results)
        if flag2:
            sample.all_cpg = flag2
            get_classification(path_folder=path_results, sample=sample)
            call_r_functions(path_folder=path_results)
            fixing_radar_plot(path_to_image=path_results)
            media_to_static(path_folder=path_results)
            sample.status = 1
            sample.save()
        else:
            print("Some CpGs are missing!")
            sample.missing_cpg = message
            sample.status = 3
            sample.save()
    else:
        print("Txt file is incomplete!")
        sample.status = 2
        sample.save()
    
    if sample.send_mail:
        print('Start 15 seconds timer')
        time.sleep(15)
        print('Sending email...')
        send_report(sample_id=sample_id, base_url=base_url)

    t1_stop = process_time()
    print("Elapsed time during the whole program in seconds:", t1_stop-t1_start)
    return print("DONE!")


@shared_task(name="send_notification")
def analysis_notification(sample_id):
    """
    Task to send an e-mail notification when an sample is successfully created.
    """
    sample = Sample.objects.get(id=sample_id)

    subject = "EpiGe-App Job ID: {jobID}".format(jobID=sample.id)
    message = f"""
    Hello, we just received an analysis with this e-mail address!

    You will receive another e-mail with your results in a few minutes.
    If you do not receive the e-mail, please write to us at this e-mail address with the job code of the analysis.

    The Job ID assigned to you is shown below:

    Job ID: {sample.id}
    Sample identifier: {sample.sample_identifier}
    Created at: {sample.created}

    Thank you for using EpiGe-App!

    EpiGe Team
    """
    email = EmailMessage(subject, message, 'hospitalbarcelona.PECA@sjd.es', [sample.email])
    email.send()
    print("Notification Sent!")
