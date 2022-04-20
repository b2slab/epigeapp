import pandas as pd
import numpy as np
import weasyprint
import pickle
import re
import subprocess


from .models import Classification, Sample, Calibration
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from io import BytesIO
from django.conf import settings
from PIL import Image
from numpy import asarray
from decouple import config
from sklearn.linear_model import LogisticRegression


def get_pattern(dataframe):
    dummy = dataframe
    dummy['pattern'] = dummy.cg18849583.astype(str) + dummy.cg01268345.astype(str) + dummy.cg10333416.astype(str) + \
                       dummy.cg12925355.astype(str) + dummy.cg25542041.astype(str) + dummy.cg02227036.astype(str)

    return dummy['pattern'][0]


def hamming_distance(string1, string2):
    # Start with a distance of zero, and count up
    distance = 0
    # Loop over the indices of the string
    L = len(string1)
    for i in range(L):
        # Add 1 to the distance if these two characters are not equal
        if string1[i] != string2[i]:
            distance += 1
    # Return the final count of differences
    return distance


def score_dist(distance):
    return 1 - (distance / 6)


def get_probability_df(array):
    dummy = pd.DataFrame(data=array, columns=['Prob_Unmet', 'Prob_Met'])

    dummy['CpG'] = ["cg18849583", "cg01268345", "cg10333416",
                    "cg12925355", "cg25542041", "cg02227036"]

    dummy['Status'] = np.where(dummy['Prob_Met'] > 0.456, 'Methylated', 'Unmethylated')

    dummy = dummy[['CpG', 'Status', 'Prob_Met']]

    dummy.columns = dummy.columns.str.replace('Prob_Met', 'Probability')

    dummy['Probability'] = round(dummy['Probability'], 2)

    return dummy


def get_classification(path_folder, sample):
    results_data = pd.read_csv(path_folder / 'Results.csv', sep='\t')

    results_data = results_data[results_data['Task'] == "UNKNOWN"]

    delta = []
    names = []
    for name, group in results_data.groupby("SNP Assay Name"):
        dummy_mean = group[["Allele1 Delta Rn", "Allele2 Delta Rn"]].mean()
        delta.append(dummy_mean.values)
        names.append(name)

    delta = np.vstack(delta)

    df = pd.DataFrame(delta, columns=["Allele1 Delta Rn", "Allele2 Delta Rn"])
    df["delta1_avg_log"] = np.log(df["Allele1 Delta Rn"])
    df["delta2_avg_log"] = np.log(df["Allele2 Delta Rn"])
    df["cpg"] = names

    if sum(df['cpg'] == ['G1_1884', 'G3_0126', 'S1_1033', 'S3_1292', 'W1_2554', 'W3_0222']) != 6:
        df = df.sort_values('cpg')

    filename = 'R/logistic_model.sav'
    loaded_model = pickle.load(open(filename, 'rb'))
    my_array = loaded_model.predict_proba(df[['delta1_avg_log', 'delta2_avg_log']])

    df_methylation = get_probability_df(array=my_array)

    df_methylation.to_csv(path_folder / 'probability_dataframe.csv', index=False)

    df2 = pd.DataFrame(np.where(df_methylation['Status'] == 'Methylated', 1, 0).reshape(1, 6),
                       columns=["cg18849583", "cg01268345", "cg10333416",
                                "cg12925355", "cg25542041", "cg02227036"])

    df2['sample_name'] = results_data['Sample Name'].unique()

    df2.to_csv(path_folder / 'sample_dataframe.csv', index=False)

    pattern = get_pattern(df2)

    distances = [hamming_distance(pattern, '100101'),
                 hamming_distance(pattern, '011001'),
                 hamming_distance(pattern, '010110')]

    subgroup = ["non-WNT/non-SHH", "SHH", "WNT"]

    if sum(distances == np.amin(distances)) < 2:
        index = np.where(distances == np.amin(distances))[0][0]
        assigned = subgroup[index]
    else:
        assigned = "Not classified"

    Classification.objects.create(sample=sample,
                                  subgroup=assigned,
                                  score_wnt=score_dist(distances[2]),
                                  score_shh=score_dist(distances[1]),
                                  score_gg=score_dist(distances[0]),
                                  )

    df3 = pd.DataFrame(data=np.array([score_dist(distances[0]),score_dist(distances[1]),
                                      score_dist(distances[2])]).reshape(1, 3), columns=["dGG", "dSHH", "dWNT"])

    df3.to_csv(path_folder / 'distances_dataframe.csv', index=False)


def send_report(sample_id, base_url):
    sample = Sample.objects.get(id=sample_id)

    # create e-mail
    subject = "EpiGeApp Job ID: {jobID}".format(jobID=sample.id)
    message = f"""
    Hello, the following analysis is complete:

    Job code: {sample.id}
    Sample identifier: {sample.sample_identifier}
    Created at: {sample.created}

    Please, find attached the results for your recent analysis.

    EpiGe Team
    """

    email = EmailMessage(subject, message, 'hospitalbarcelona.PECA@sjd.es', [sample.email])

    if not sample.txt_complete:
        html = render_to_string('delta_rn/report_error1.html',
                                {'sample': sample})
    elif not sample.all_cpg:
        calibration = Calibration.objects.get(sample=sample_id)
        html = render_to_string('delta_rn/report_error2.html',
                                {'calibration': calibration,
                                 'sample': sample})
    else:
        calibration = Calibration.objects.get(sample=sample_id)
        classification = Classification.objects.get(sample=sample_id)

        html = render_to_string('delta_rn/report_complete.html',
                                {'classification': classification,
                                 'calibration': calibration,
                                 'sample': sample})
    # generate PDF file
    out = BytesIO()
    stylesheets = [weasyprint.CSS(settings.STATICFILES_DIRS[0] / 'css/pdf.css')]
    weasyprint.HTML(string=html, base_url=base_url).write_pdf(out, stylesheets=stylesheets)
    # attach PDF file
    email.attach(f'analysis_{sample.id}.pdf', out.getvalue(), 'application/pdf')
    # send e-mail
    email.send()
    print("Report Sent!")


def fixing_radar_plot(path_to_image):
    # load the image
    image = Image.open(path_to_image / "plots/radar_plot.tiff")
    # convert image to numpy array
    data = asarray(image)
    # trimming image
    im_trim = data[0:1200,:]
    # convert numpy array to image
    img = Image.fromarray(im_trim, 'RGBA')
    # save the image
    img.save(path_to_image / "plots/radar_plot.png")


def get_calibration(path_to_txt, path_to_results, sample):
    with open(path_to_txt, 'r') as f:
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

    df = pd.read_csv(path_folder / "Results.csv", sep="\t")
    df_ntc = df.query("Task == 'NTC'")
    allele1_ct = list(set(df_ntc["Allele1 Ct"].values))
    allele2_ct = list(set(df_ntc["Allele2 Ct"].values))
    if len(allele1_ct) == 1 and len(allele2_ct) == 1:
        flag = True

    return flag


def call_r_functions(path_folder):
    # Change accordingly to your Rscript.exe & R script path
    r_path = config("R_PATH")
    script_path1 = settings.BASE_DIR.parent / "R/1_plot_table_sample.R"
    script_path2 = settings.BASE_DIR.parent / "R/2_plot_radar_plot.R"

    # Used as input arguments to the R code
    args = str(path_folder) + "/"
    # Execute command
    cmd = [r_path, str(script_path1), args]
    result = subprocess.check_output(cmd, universal_newlines=True)
    print(result)

    cmd2 = [r_path, str(script_path2), args]
    result = subprocess.check_output(cmd2, universal_newlines=True)
    # Display result
    return print(result)
