from celery import shared_task
from core_app.utils import read_txt_pcr, mkdir_results, media_to_static, check_all_data_files, check_all_cpg, \
    get_calibration, run_r_script
from .models import Sample
from .utils import get_classification, send_report
from django.core.mail import EmailMessage


@shared_task(name="analysis_delta_rn_task")
def analysis_and_report(sample_id):
    """
    Task to perform the analysis of a sample and report creation.
    """
    sample = Sample.objects.get(id=sample_id)
    path_results = mkdir_results(path_to_txt=sample.file.path)
    read_txt_pcr(path_to_read=sample.file.path, path_to_save=path_results)
    flag1 = check_all_data_files(path_folder=path_results)
    if flag1:
        sample.txt_complete = flag1
        get_calibration(path_to_txt=sample.file.path, path_to_results=path_results, sample=sample, delta_rn=True)
        flag2, message = check_all_cpg(path_folder=path_results)
        if flag2:
            sample.all_cpg = flag2
            run_r_script(path_folder=path_results, delta_rn=True)
            get_classification(path_folder=path_results, sample=sample)
            media_to_static(path_folder=path_results)
            sample.status = 1
            sample.save()
            send_report(sample_id=sample_id)
        else:
            print("Some CpGs are missing!")
            sample.missing_cpg = message
            sample.save()
    else:
        print("Txt file is incomplete!")
        sample.save()

    return print("DONE!")


@shared_task(name="send_notification_delta_rn")
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



