import pandas as pd
from .models import Classification


def get_classification(path_folder, sample):
    rf_data = pd.read_csv(path_folder + 'dataframe_rf.csv')

    Classification.objects.create(sample=sample,
                                  subgroup=rf_data.iloc[0]['subgroup'],
                                  probability_wnt=round(rf_data.iloc[0]['probability WNT'], 4),
                                  probability_shh=round(rf_data.iloc[0]['probability SHH'], 4),
                                  probability_gg=round(rf_data.iloc[0]['probability non-WNT/non-SHH'], 4),
                                  )
