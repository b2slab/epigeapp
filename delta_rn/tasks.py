from celery import shared_task
from core_app.utils import read_txt_pcr, standard_names, processing_data, mkdir_results, \
    standard_data, media_to_static, check_amplification_fit, check_all_data_files, check_all_cpg, \
    send_report
from .models import Sample, Classification, Calibration
import os.path
from decouple import config
from django.conf import settings
import subprocess
import pandas as pd
import re


base_root = str(settings.BASE_DIR)


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
    get_calibration(path_to_txt=sample.file.url, path_to_results=path_results, sample=sample)
    flag2, message = check_all_cpg(path_folder=path_results)
    sample.all_cpg = flag2
    run_r_script(path_folder=path_results)
    get_classification(path_folder=path_results, sample=sample)
    media_to_static(path_folder=path_results)
    sample.status = 1
    sample.save()

    # send_report(sample_id=sample_id)


def run_r_script(path_folder):
    # Change accordingly to your Rscript.exe & R script path
    r_path = config("R_PATH")
    script_path = base_root + config("SCRIPT_PATH_2")
    # Used as input arguments to the R code
    args = path_folder
    # Execute command
    cmd = [r_path, script_path, args]
    result = subprocess.check_output(cmd, universal_newlines=True)
    # Display result
    return print(result)


def get_classification(path_folder, sample):
    rf_data = pd.read_csv(path_folder + 'dataframe_rf.csv')

    Classification.objects.create(sample=sample,
                                  subgroup=rf_data.iloc[0]['subgroup'],
                                  probability_wnt=round(rf_data.iloc[0]['probability WNT'], 4),
                                  probability_shh=round(rf_data.iloc[0]['probability SHH'], 4),
                                  probability_gg=round(rf_data.iloc[0]['probability non-WNT/non-SHH'], 4),
                                  )

def get_calibration(path_to_txt, path_to_results, sample):
    with open(base_root + path_to_txt, 'r') as f:
        lines = f.readlines()

    ROX_valid = VIC_valid = FAM_valid = True

    # FAM DYE Calibration
    pattern = re.compile(r'\bCalibration Pure Dye FAM is expired\b')
    index = [i for i, line in enumerate(lines) if pattern.search(line) is not None]

    if lines[index[0]].split("=")[1].strip() == "No":
        FAM_valid = True

    pattern = re.compile(r'\bCalibration Pure Dye FAM performed\b')
    index = [i for i, line in enumerate(lines) if pattern.search(line) is not None]

    FAM_date = lines[index[0]].split("=")[1].strip()

    # ROX DYE Calibration
    pattern = re.compile(r'\bCalibration Pure Dye ROX is expired\b')
    index = [i for i, line in enumerate(lines) if pattern.search(line) is not None]

    if lines[index[0]].split("=")[1].strip() == "No":
        ROX_valid = True

    pattern = re.compile(r'\bCalibration Pure Dye ROX performed\b')
    index = [i for i, line in enumerate(lines) if pattern.search(line) is not None]

    ROX_date = lines[index[0]].split("=")[1].strip()

    # VIC DYE Calibration
    pattern = re.compile(r'\bCalibration Pure Dye VIC is expired\b')
    index = [i for i, line in enumerate(lines) if pattern.search(line) is not None]

    if lines[index[0]].split("=")[1].strip() == "No":
        VIC_valid = True

    pattern = re.compile(r'\bCalibration Pure Dye VIC performed\b')
    index = [i for i, line in enumerate(lines) if pattern.search(line) is not None]

    VIC_date = lines[index[0]].split("=")[1].strip()

    # Instrument Type:
    pattern = re.compile(r'\bInstrument Type\b')
    index = [i for i, line in enumerate(lines) if pattern.search(line) is not None]

    instrument_type = lines[index[0]].split("=")[1].strip()

    Calibration.objects.create(sample=sample,
                               ROX_valid=ROX_valid,
                               FAM_valid=FAM_valid,
                               VIC_valid=VIC_valid,
                               ROX_date=ROX_date,
                               FAM_date=FAM_date,
                               VIC_date=VIC_date,
                               amplification_test=amplification_test(path_to_results),
                               instrument_type=instrument_type)


def amplification_test(path_folder):
    flag = False
    filename = "Results.csv"

    df = pd.read_csv(path_folder + filename, sep="\t")
    df_ntc = df.query("Task == 'NTC'")
    allele1_ct = list(set(df_ntc["Allele1 Ct"].values))
    allele2_ct = list(set(df_ntc["Allele2 Ct"].values))
    if len(allele1_ct) == 1 and len(allele2_ct) == 1:
        flag = True

    return flag



