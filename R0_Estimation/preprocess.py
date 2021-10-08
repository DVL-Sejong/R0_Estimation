from R0_Estimation.datatype import Country
from R0_Estimation.io import load_number_of_tests, load_sird_data, load_regions
from R0_Estimation.io import save_rho_df, load_first_confirmed_date, save_tg_df
from R0_Estimation.util import get_period
from datetime import datetime

import pandas as pd


def get_dataset_dates(country):
    num_test_df = load_number_of_tests(country)
    columns = num_test_df.columns.to_list()

    start_date1 = None
    end_date1 = datetime.strptime(columns[-1], '%Y-%m-%d')
    for column in columns:
        test_list = num_test_df[column]
        if len([elem for elem in test_list if elem == 0]) == 0:
            start_date1 = datetime.strptime(column, '%Y-%m-%d')
            break

    first_confirmed_df = load_first_confirmed_date(country)
    first_dates = first_confirmed_df['first_date'].to_list()
    first_dates = [datetime.strptime(elem, '%Y-%m-%d') for elem in first_dates]
    start_date2 = min(first_dates)

    sird_hash, sird_dict = load_sird_data(country)
    sird_dates = sird_dict[list(sird_dict.keys())[0]].index.tolist()
    start_date3 = datetime.strptime(sird_dates[0], '%Y-%m-%d')
    end_date3 = datetime.strptime(sird_dates[-1], '%Y-%m-%d')

    start_date = max(start_date1, start_date2, start_date3)
    end_date = min(end_date1, end_date3)
    period = get_period(start_date, end_date, out_date_format='%Y-%m-%d')
    return period


def get_rho_df(country):
    regions = load_regions(country)
    dataset_dates = get_dataset_dates(country)

    rho_df = pd.DataFrame(index=regions, columns=dataset_dates)
    rho_df.index.name = 'regions'

    sird_hash, sird_dict = load_sird_data(country)
    test_num_df = load_number_of_tests(country)

    for region in regions:
        for common_date in dataset_dates:
            confirmed_value = sird_dict[region].loc[common_date, 'infected']
            test_numbers = test_num_df.loc[region, common_date]
            rho_value = confirmed_value / test_numbers
            rho_df.loc[region, common_date] = rho_value

    save_rho_df(country, sird_hash, rho_df)
    return rho_df


def get_tg_df(country):
    regions = load_regions(country)
    tg_df = pd.DataFrame(index=regions, columns=['Tg'])
    tg_df.index.name = 'regions'
    tg_df.loc[:, :] = 6.9

    save_tg_df(country, tg_df)
    return tg_df


def get_t_value(country, region, target_date):
    first_confirmed_df = load_first_confirmed_date(country)
    first_date = datetime.strptime(first_confirmed_df.loc[region, 'first_date'], '%Y-%m-%d')
    t_value = (datetime.strptime(target_date, '%Y-%m-%d') - first_date).days + 1
    return t_value


if __name__ == '__main__':
    country = Country.INDIA
    t_value = get_t_value(country, 'West Bengal', '2020-03-19')
    print(t_value)
