from R0_Estimation.datatype import get_country_name, Country, PreprocessInfo
from os.path import join, abspath, dirname, split
from pathlib import Path
from glob import glob

import pandas as pd


ROOT_PATH = Path(abspath(dirname(__file__))).parent
DATASET_PATH = join(ROOT_PATH, 'dataset')
SETTING_PATH = join(ROOT_PATH, 'settings')
RESULT_PATH = join(ROOT_PATH, 'results')


def load_links(country=None):
    link_path = join(DATASET_PATH, 'links.csv')
    link_df = pd.read_csv(link_path, index_col='country')

    if country is not None:
        link_df = link_df.loc[get_country_name(country), :]

    return link_df


def load_population(country):
    population_path = join(DATASET_PATH, get_country_name(country), 'population.csv')
    population_df = pd.read_csv(population_path, index_col='regions')
    return population_df


def load_regions(country):
    population_df = load_population(country)
    regions = population_df.index.tolist()
    regions.sort()
    return regions


def load_pre_info(hash=None):
    pre_path = join(SETTING_PATH, 'pre_info.csv')
    pre_info_df = pd.read_csv(pre_path, index_col='hash')
    return pre_info_df if hash is None else pre_info_df.loc[[hash], :]


def load_first_confirmed_date(country):
    first_date_path = join(DATASET_PATH, get_country_name(country), 'first_confirmed_date.csv')
    first_confirmed_date_df = pd.read_csv(first_date_path, index_col='regions')
    return first_confirmed_date_df


def load_number_of_tests(country, test_hash):
    test_number_path = join(DATASET_PATH, get_country_name(country),
                            'number_of_tests', test_hash, 'number_of_tests.csv')
    test_num_df = pd.read_csv(test_number_path, index_col='regions')
    return test_num_df


def load_sird_data(country, sird_hash):
    print(f'load {get_country_name(country)} SIRD data')
    country_path = join(DATASET_PATH, get_country_name(country), 'sird', sird_hash, '*.csv')
    sird_region_path_list = glob(country_path)

    sird_dict = dict()
    for sird_path in sird_region_path_list:
        _, region = split(sird_path)
        region = region.split('.csv')[0]

        if region not in load_regions(country):
            continue

        region_df = pd.read_csv(sird_path, index_col='date')
        sird_dict.update({region: region_df})

    return sird_dict


def load_r0_df(country, sird_hash, test_hash, delay):
    r0_path = join(RESULT_PATH, get_country_name(country),
                   f'{sird_hash}_{test_hash}_{delay}', 'r0.csv')
    r0_df = pd.read_csv(r0_path, index_col='regions')
    return r0_df


def load_rho_df(country, sird_hash, test_hash, delay):
    rho_path = join(DATASET_PATH, get_country_name(country), 'rho',
                    f'{sird_hash}_{test_hash}_{delay}', 'rho.csv')
    rho_df = pd.read_csv(rho_path, index_col='regions')
    return rho_df


def load_tg_df(country):
    tg_path = join(DATASET_PATH, get_country_name(country), 'tg.csv')
    tg_df = pd.read_csv(tg_path, index_col='regions')
    return tg_df


def save_r0_df(r0_df, country, sird_hash, test_hash, delay):
    r0_path = join(RESULT_PATH, get_country_name(country), f'{sird_hash}_{test_hash}_{delay}')
    Path(r0_path).mkdir(parents=True, exist_ok=True)
    saving_path = join(r0_path, 'r0.csv')
    r0_df.to_csv(saving_path)
    print(f'saving r0 dataframe to {saving_path}')


def save_rho_df(rho_df, country, sird_hash, test_hash, delay):
    rho_path = join(DATASET_PATH, get_country_name(country), 'rho',
                    f'{sird_hash}_{test_hash}_{delay}')
    Path(rho_path).mkdir(parents=True, exist_ok=True)
    saving_path = join(rho_path, 'rho.csv')
    rho_df.to_csv(saving_path)
    print(f'saving rho data to {saving_path}')


def save_tg_df(country, tg_df):
    tg_path = join(DATASET_PATH, get_country_name(country))
    Path(tg_path).mkdir(parents=True, exist_ok=True)
    saving_path = join(tg_path, 'tg.csv')
    tg_df.to_csv(saving_path)
    print(f'saving Tg data to {saving_path}')


if __name__ == '__main__':
    country = Country.INDIA
    link_df = load_links(country)

    sird_info = PreprocessInfo(country=country, start=link_df['start_date'], end=link_df['end_date'],
                               increase=True, daily=True, remove_zero=True,
                               smoothing=True, window=9, divide=False)

    load_sird_data(country, sird_info.get_hash())
