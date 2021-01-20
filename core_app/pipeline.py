import re
import pathlib
import subprocess
from django.conf import settings
import pandas as pd
from scipy.optimize import curve_fit
import numpy as np
import matplotlib

matplotlib.use('agg')
import matplotlib.pyplot as plt


media_root = settings.MEDIA_ROOT
cpg_list = ['W1_2554', 'W3_0222', 'S1_1033', 'S3_1292', 'G1_1884', 'G3_0126']


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
        pathlib.Path(path_save + self.case_num).mkdir(parents=True, exist_ok=True)
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
        plt.savefig(path_save + self.case_num + "/" + name + ".png", dpi=150)
        plt.close()


def handle_uploaded_file(f):
    path = media_root + "/data/data.txt"
    with open(path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    return print('Data have been saved')


def read_txt_pcr():
    with open(media_root + "/data/data.txt", 'r') as f:
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
        with open(media_root + "/results/" + filename, 'w') as f:
            f.writelines(dict_files[filename])
    return print('Data have been preprocessed')


def replace_label(string):
    dict_label = {'S1_1033-Allele 2_Unmeth': 'S1_1033-Allele 2_U', 'S1_1033-Allele 1_Meth': 'S1_1033-Allele 1_M',
                  'S3_1292.1-Allele 2_U': 'S3_1292-Allele 2_U', 'S3_1292.1-Allele 1_M': 'S3_1292-Allele 1_M',
                  'G1_1884.1-Allele 2_U': 'G1_1884-Allele 2_U', 'G1_1884.1-Allele 1_M': 'G1_1884-Allele 1_M',
                  'G3_0126.1-Allele 2_U': 'G3_0126-Allele 2_U', 'G3_0126.1-Allele 1_M': 'G3_0126-Allele 1_M',
                  'S3_1292.1': 'S3_1292', 'G1_1884.1': 'G1_1884', 'G3_0126.1': 'G3_0126',
                  'Allele 2_Unmeth': 'Allele 2_U', 'Allele 1_Meth': 'Allele 1_M',
                  'B04-2075':'B04-3075', 'B10-1192B':'B10-1192', 'B04':'B04-3075'
                  }
    if string in list(dict_label.keys()):
        return dict_label[string]
    else:
        return string


def standard_names():
    file = media_root + "/results/Sample_Setup.csv"
    setup = pd.read_csv(file, sep="\t")
    setup['Sample Name'] = [name.split(sep="_")[0] if name is not np.nan else name for name in setup['Sample Name']]
    setup['Sample Name'] = [replace_label(label) for label in setup['Sample Name']]
    setup.to_csv(file, sep='\t', index=False)
    return print('Data have been standardized.')


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
    return a * (np.exp(b*x + c) / (1 + np.exp(b*x + c)))


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


def processing_data():
    file = media_root + "/results/Sample_Setup.csv"
    setup = import_setup(file)
    setup2 = setup.query("task == 'UNKNOWN'")
    data = import_data(media_root + "/results/Amplification_Data.csv")
    sample_name = setup2.sample_name.unique()[0]

    d = np.empty((12, 8))
    row_names = []

    for count, well in enumerate(setup2.well_pos):
        well_data = data[data.well_pos == well]

        cycles = well_data.query("allele == 'Allele 1_M'")['cycle'].values
        fam = well_data.query("allele == 'Allele 1_M'")['delta_rn'].values
        vic = well_data.query("allele == 'Allele 2_U'")['delta_rn'].values

        pcr = PCR(case_num=sample_name, well_pos=well, cycles=cycles, amp_fam=fam, amp_vic=vic)

        pcr.adj_fam, pcr.params_fam, pcr.rmse_fam = fit(x=pcr.cycles, y=pcr.amp_fam)
        row = [*pcr.params_fam,  pcr.rmse_fam]

        pcr.adj_vic, pcr.params_vic, pcr.rmse_vic = fit(x=pcr.cycles, y=pcr.amp_vic)
        row = row + [*pcr.params_vic, pcr.rmse_vic]

        d[count] = row
        row_names.append(sample_name + "_" + well)

        pcr.plot_curve(path_save=media_root + "/results/plots/")

    dataframe = pd.DataFrame(data=d, index=row_names, columns=['plateau_fam', 'slope_fam', 'intercept_fam', 'rmse_fam',
                                                               'plateau_vic', 'slope_vic', 'intercept_vic', 'rmse_vic'])

    dataframe['snp'] = setup2.snp.values

    dataframe.to_csv(media_root + '/results/dataframe.csv')

    return print('Dataframe has been written.')


def run_r_script():
    # Change accordingly to your Rscript.exe & R script path
    r_path = "/Library/Frameworks/R.framework/Resources/bin/Rscript"
    script_path = media_root + "/r_scripts/predict_plsda.R"
    # Used as input arguments to the R code
    args = "~/epigen_app/media/results/dataframe.csv"
    # Execute command
    cmd = [r_path, script_path, args]
    result = subprocess.check_output(cmd, universal_newlines=True)
    # Display result
    return print("The result is:", result)



