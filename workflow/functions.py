# ==============================================================================
# PACKAGES
# ==============================================================================

import pandas as pd
import numpy as np
import weasyprint
import pickle
import re
import pathlib
import subprocess
import shutil
import os.path
import matplotlib

matplotlib.use('agg')
import matplotlib.pyplot as plt

from scipy.optimize import curve_fit
from PIL import Image
from numpy import asarray
from decouple import config
from io import BytesIO
from sklearn.linear_model import LogisticRegression

from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings

from .models import Classification, Sample, Calibration


# ==============================================================================
# FILE MANAGEMENT
# ==============================================================================

def read_txt_pcr(path_to_read, path_to_save):
    with open(path_to_read, 'r') as f:
        lines = f.readlines()

    pattern = re.compile(r"^\[.*?\]$", re.IGNORECASE)
    titles_index = [[line, i] for i, line in enumerate(lines) if pattern.search(line) is not None]
    titles, index = zip(*titles_index)
    filenames = ['_'.join(re.findall(r"[\w']+", title)) + '.csv' for title in titles]

    dict_files = {}
    long_index = len(index)
    for i, filename in enumerate(filenames):
        if i + 1 < long_index:
            dict_files[filename] = lines[index[i] + 1: index[i + 1]]
        else:
            dict_files[filename] = lines[index[i] + 1:]

    for filename in filenames:
        with open(path_to_save / filename, 'w') as f:
            f.writelines(dict_files[filename])


def mkdir_results(path_to_txt):
    path = pathlib.Path(path_to_txt)
    path_to_save = path.parent.parent / 'results'
    pathlib.Path(path_to_save).mkdir(parents=True, exist_ok=True)
    return path_to_save


def mkdir_static(sample_id):
    if settings.DEBUG:
        path = settings.STATICFILES_DIRS[0] / "samples" / sample_id
    else:
        path = settings.STATIC_ROOT / "samples" / sample_id
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)
    print("Static folder created!")
    return path


def media_to_static(path_folder):
    path_plots = path_folder / "plots"
    png_list = list(path_plots.rglob('*.png'))
    sample_id = str(path_folder).split("/")[-2]
    path_static_sample = mkdir_static(sample_id=sample_id)
    print("Moving files:")
    for image in png_list:
        newPath = shutil.copy(image, path_static_sample)
        print(newPath)


def fixing_radar_plot(path_to_image):
    # load the image
    image = Image.open(path_to_image / "plots/radar_plot.tiff")
    # convert image to numpy array
    data = asarray(image)
    # trimming image
    im_trim = data[0:1200, :]
    # convert numpy array to image
    img = Image.fromarray(im_trim, 'RGBA')
    # save the image
    img.save(path_to_image / "plots/radar_plot.png")


# ==============================================================================
# QUALITY CONTROL
# ==============================================================================

def amplification_test(path_folder):
    flag = False

    df = pd.read_csv(path_folder / "Results.csv", sep="\t")
    df_ntc = df.query("Task == 'NTC'")
    allele1_ct = list(set(df_ntc["Allele1 Ct"].values))
    allele2_ct = list(set(df_ntc["Allele2 Ct"].values))
    if len(allele1_ct) == 1 and len(allele2_ct) == 1:
        flag = True

    return flag


def check_all_data_files(path_folder):
    files = ["Amplification_Data.csv", "Multicomponent_Data.csv", "Raw_Data.csv",
             "Reagent_Information.csv", "Results.csv", "Sample_Setup.csv"]
    flag = True
    for file in files:
        if not os.path.isfile(path_folder / file):
            flag = False
            break
    return flag


def check_all_cpg(path_folder):
    df = pd.read_csv(path_folder / "Results.csv", sep="\t")

    # CAMBIO DE BUSQUEDA DE NOMBRES: names = ['S1_1033', 'S3_1292', 'W1_2554', 'W3_0222', 'G1_1884', 'G3_0126']
    names = ['cg18849583', 'cg01268345', 'cg10333416', 'cg12925355', 'cg25542041', 'cg02227036']

    flag = True
    message = None

    ref_re = [re.compile(name) for name in names]
    output = {i: [r.pattern for r in ref_re if r.match(i)] for i in df["SNP Assay Name"].unique()}

    for value in output.values():
        snp_match = value[0]
        if snp_match not in names:
            flag = False
            message = value
            break

    return flag, message


def check_amplification_fit(path_folder):
    df = pd.read_csv(path_folder / 'dataframe.csv')
    return not df.isnull().values.any()


def get_calibration(path_to_txt, path_to_results, sample):
    with open(path_to_txt, 'r') as f:
        lines = f.readlines()

    ROX_valid = VIC_valid = FAM_valid = False

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


# ==============================================================================
# CLASSIFICATION FUNCTIONS
# ==============================================================================

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
    return round(1 - (distance / 6), 2)


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
    
    # # CAMBIO DE BUSQUEDA DE NOMBRES:
    # if sum(df['cpg'] == ['G1_1884', 'G3_0126', 'S1_1033', 'S3_1292', 'W1_2554', 'W3_0222']) != 6:
    #    df = df.sort_values('cpg')
        
    if sum(df['cpg'] == ['cg18849583', 'cg01268345', 'cg10333416', 'cg12925355', 'cg25542041', 'cg02227036']) != 6:
        # CAMBIO DE BUSQUEDA DE NOMBRES:
        # df = df.sort_values('cpg')
        df['cpg'] = pd.Categorical(df['cpg'], ['cg18849583', 'cg01268345', 'cg10333416', 'cg12925355', 'cg25542041', 'cg02227036'])
        df = df.sort_values("cpg")
        
    filename = 'logistic_model.sav'
    loaded_model = pickle.load(open('workflow/classifiers/' + filename, 'rb'))
    my_array = loaded_model.predict_proba(df[['delta1_avg_log', 'delta2_avg_log']])

    df_met = get_probability_df(array=my_array)

    df_met.to_csv(path_folder / 'probability_dataframe.csv', index=False)

    df2 = pd.DataFrame(np.where(df_met['Status'] == 'Methylated', 1, 0).reshape(1, 6),
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

    df3 = pd.DataFrame(data=np.array([score_dist(distances[0]), score_dist(distances[1]),
                                      score_dist(distances[2])]).reshape(1, 3), columns=["dGG", "dSHH", "dWNT"])

    df3.to_csv(path_folder / 'distances_dataframe.csv', index=False)


# ==============================================================================
# REPORT FUNCTIONS
# ==============================================================================

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
        html = render_to_string('workflow/report_error1.html',
                                {'sample': sample})
    elif not sample.all_cpg:
        calibration = Calibration.objects.get(sample=sample_id)
        html = render_to_string('workflow/report_error2.html',
                                {'calibration': calibration,
                                 'sample': sample})
    else:
        calibration = Calibration.objects.get(sample=sample_id)
        classification = Classification.objects.get(sample=sample_id)

        html = render_to_string('workflow/report_complete.html',
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


# ==============================================================================
# R MANAGEMENT
# ==============================================================================

def call_r_functions(path_folder):
    # Change accordingly to your Rscript.exe & R script path
    r_path = config("R_PATH")

    script_path1 = settings.BASE_DIR.parent / "R_scripts/figure_NTC.R"
    script_path2 = settings.BASE_DIR.parent / "R_scripts/figure_probability_table.R"
    script_path3 = settings.BASE_DIR.parent / "R_scripts/figure_radar_plot.R"
    script_path4 = settings.BASE_DIR.parent / "R_scripts/figure_sample_table.R"
    script_path5 = settings.BASE_DIR.parent / "R_scripts/figure_standard_deviation.R"
    script_list = [script_path1, script_path2, script_path3, script_path4, script_path5]

    # Used as input arguments to the R code
    args = str(path_folder) + "/"

    # Execute command
    for script in script_list:
        cmd = [r_path, str(script), args]
        result = subprocess.check_output(cmd, universal_newlines=True)
        print(result)

    return print("R Plots created!")


# ==============================================================================
# OLD FUNCTIONS & UNUSED
# ==============================================================================

def replace_label(string):
    dict_label = {'S1_1033-Allele 2_Unmeth': 'S1_1033-Allele 2_U', 'S1_1033-Allele 1_Meth': 'S1_1033-Allele 1_M',
                  'S3_1292.1-Allele 2_U': 'S3_1292-Allele 2_U', 'S3_1292.1-Allele 1_M': 'S3_1292-Allele 1_M',
                  'G1_1884.1-Allele 2_U': 'G1_1884-Allele 2_U', 'G1_1884.1-Allele 1_M': 'G1_1884-Allele 1_M',
                  'G3_0126.1-Allele 2_U': 'G3_0126-Allele 2_U', 'G3_0126.1-Allele 1_M': 'G3_0126-Allele 1_M',
                  'S3_1292.1': 'S3_1292', 'G1_1884.1': 'G1_1884', 'G3_0126.1': 'G3_0126',
                  'Allele 2_Unmeth': 'Allele 2_U', 'Allele 1_Meth': 'Allele 1_M',
                  'B04-2075': 'B04-3075', 'B10-1192B': 'B10-1192', 'B04': 'B04-3075'
                  }
    if string in list(dict_label.keys()):
        return dict_label[string]
    else:
        return string


def standard_names(path_folder):
    setup = pd.read_csv(path_folder / "Sample_Setup.csv", sep="\t")
    setup['Sample Name'] = [name.split(sep="_")[0] if name is not np.nan else name for name in setup['Sample Name']]
    setup['Sample Name'] = [replace_label(label) for label in setup['Sample Name']]
    setup.to_csv(path_folder / "Sample_Setup.csv", sep='\t', index=False)
    return print('Data have been standardized.')


def standard_data(path_folder):
    amp_path = path_folder / 'Amplification_Data.csv'

    setup_path = path_folder / 'Sample_Setup.csv'

    data = pd.read_csv(amp_path, sep='\t')

    data['Target Name'] = [replace_label(label) for label in data['Target Name']]

    data.to_csv(amp_path, sep='\t', index=False)

    setup = pd.read_csv(setup_path, sep='\t')

    setup['SNP Assay Name'] = [replace_label(label) for label in setup['SNP Assay Name']]

    setup['Allele1 Name'] = [replace_label(label) for label in setup['Allele1 Name']]

    setup['Allele2 Name'] = [replace_label(label) for label in setup['Allele2 Name']]

    setup.to_csv(setup_path, sep='\t', index=False)

    return print('The Setup and Amplification data csv files have been standardized!')


def import_setup(csv_path):
    setup = pd.read_csv(csv_path, sep="\t")
    setup.rename(columns={'Well': 'well', 'Well Position': 'well_pos', 'Sample Name': 'sample_name',
                          'Sample Color': 'sample_color', 'SNP Assay Name': 'snp', 'SNP Assay Color': 'snp_color',
                          'Task': 'task', 'Allele1 Name': 'allele_1_name', 'Allele1 Color': 'allele_1_color',
                          'Allele1 Reporter': 'allele_1_reporter', 'Allele1 Quencher': 'allele_1_quencher',
                          'Allele2 Name': 'allele_2_name', 'Allele2 Color': 'allele_2_color',
                          'Allele2 Reporter': 'allele_2_reporter', 'Allele2 Quencher': 'allele_2_quencher',
                          'Comments': 'comments'}, inplace=True)
    setup.dropna(inplace=True, thresh=10)
    setup = setup[['well', 'well_pos', 'sample_name', 'snp', 'task', 'allele_1_name',
                   'allele_1_reporter', 'allele_2_name', 'allele_2_reporter']].copy()
    return setup


def import_data(csv_path):
    data = pd.read_csv(csv_path, sep="\t")
    data.dropna(inplace=True)
    data.rename(columns={'Well': 'well', 'Well Position': 'well_pos',
                         'Cycle': 'cycle', 'Target Name': 'target', 'Rn': 'rn',
                         'Delta Rn': 'delta_rn'}, inplace=True)
    data = data.reset_index(drop=True)
    data['snp'] = [x.split('-')[0] for x in data.target]
    data['allele'] = [x.split('-')[1] for x in data.target]
    return data


def sigmoid(x, a, b, c):
    return a * (np.exp(b * x + c) / (1 + np.exp(b * x + c)))


def rmse(predictions, targets):
    differences = predictions - targets
    differences_squared = differences ** 2
    mean_of_differences_squared = differences_squared.mean()
    rmse_val = np.sqrt(mean_of_differences_squared)
    return rmse_val


def fit(x, y):
    try:
        popt, pcov = curve_fit(sigmoid, xdata=x, ydata=y, maxfev=1000, bounds=([0., 0., -np.inf], np.inf))
        y_pred = sigmoid(x, *popt)
        rmse_val = rmse(y, y_pred)
        return y_pred, popt, rmse_val
    except(RuntimeError, ValueError, TypeError):
        return None, None, None


def processing_data(path_folder):
    setup = import_setup(path_folder / "Sample_Setup.csv")
    setup2 = setup.query("task == 'UNKNOWN'")
    data = import_data(path_folder / "Amplification_Data.csv")
    sample_name = setup2.sample_name.unique()[0]

    d = np.empty((12, 8))
    row_names = []

    for count, well in enumerate(setup2.well_pos):
        try:
            well_data = data[data.well_pos == well]
        except AttributeError:
            setup_raw = pd.read_csv(path_folder / "Sample_Setup.csv", sep="\t")
            ind = int(setup_raw[setup_raw['Well Position'] == well]['Well'].values)
            well_data = data[data.well == ind]

        cycles = well_data.query("allele == 'Allele 1_M'")['cycle'].values
        fam = well_data.query("allele == 'Allele 1_M'")['delta_rn'].values
        vic = well_data.query("allele == 'Allele 2_U'")['delta_rn'].values

        pcr = PCR(case_num=sample_name, well_pos=well, cycles=cycles, amp_fam=fam, amp_vic=vic)

        pcr.adj_fam, pcr.params_fam, pcr.rmse_fam = fit(x=pcr.cycles, y=pcr.amp_fam)
        if pcr.adj_fam is not None:
            row = [*pcr.params_fam, pcr.rmse_fam]
        else:
            row = [None, None, None, None]

        pcr.adj_vic, pcr.params_vic, pcr.rmse_vic = fit(x=pcr.cycles, y=pcr.amp_vic)
        if pcr.adj_vic is not None:
            row = row + [*pcr.params_vic, pcr.rmse_vic]
        else:
            row = row + [None, None, None, None]

        d[count] = row
        row_names.append(sample_name + "_" + well)

        pcr.plot_curve(path_save=path_folder / "plots")

    dataframe = pd.DataFrame(data=d, index=row_names, columns=['plateau_fam', 'slope_fam', 'intercept_fam', 'rmse_fam',
                                                               'plateau_vic', 'slope_vic', 'intercept_vic', 'rmse_vic'])

    dataframe['snp'] = setup2.snp.values

    dataframe.to_csv(path_folder / 'dataframe.csv')

    return print('Dataframe has been written.')


def run_r_script(path_folder, delta_rn=False):
    # Change accordingly to your Rscript.exe & R script path
    r_path = config("R_PATH")
    script_path = settings.BASE_DIR.parent / config("SCRIPT_PATH", cast=str)
    if delta_rn:
        script_path = settings.BASE_DIR.parent / config("SCRIPT_PATH_2", cast=str)

    # Used as input arguments to the R code
    args = str(path_folder) + "/"
    # Execute command
    cmd = [r_path, str(script_path), args]
    result = subprocess.check_output(cmd, universal_newlines=True)
    # Display result
    return print(result)


class PCR:

    def __init__(self, case_num, well_pos, cycles, amp_fam, amp_vic):
        self.case_num = case_num
        self.well_pos = well_pos
        self.cycles = cycles
        self.amp_fam = amp_fam
        self.amp_vic = amp_vic
        self.adj_fam = None
        self.adj_vic = None
        self.params_fam = None
        self.params_vic = None
        self.rmse_fam = None
        self.rmse_vic = None

    def plot_curve(self, path_save):
        pathlib.Path(path_save).mkdir(parents=True, exist_ok=True)
        name = '_'.join((self.case_num, self.well_pos))
        plt.figure(figsize=(10, 8))
        plt.plot(self.cycles, self.amp_fam, 'r-', label='FAM')
        plt.plot(self.cycles, self.amp_vic, 'b-', label='VIC')
        if self.adj_fam is not None:
            plt.plot(self.cycles, self.adj_fam, 'g--', label='fit: a=%5.3f, b=%5.3f, c=%5.3f. RMSE: %5.3f' %
                                                             (*self.params_fam, self.rmse_fam))
        if self.adj_vic is not None:
            plt.plot(self.cycles, self.adj_vic, 'm--', label='fit: a=%5.3f, b=%5.3f, c=%5.3f. RMSE: %5.3f' %
                                                             (*self.params_vic, self.rmse_vic))
        plt.legend()
        plt.ylabel('Amplification')
        plt.xlabel('Cycle')
        plt.title(name)
        plt.grid()
        filename = name + ".png"
        plt.savefig(path_save / filename, dpi=150)
        plt.close()
