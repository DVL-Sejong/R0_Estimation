from R0_Estimation.datatype import get_country_name, Country, PreprocessInfo, InfoType
from os.path import join, abspath, dirname, split, isfile
from dataclasses import fields
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


def load_number_of_tests(country, test_info):
    test_number_path = join(DATASET_PATH, get_country_name(country),
                            'number_of_tests', test_info.get_hash())

    try:
        origin_path = join(test_number_path, 'number_of_tests.csv')
        origin_test_num_df = pd.read_csv(origin_path, index_col='regions')
        return origin_test_num_df
    except FileNotFoundError as e:
        print(e)
        save_setting(test_info, 'req_test_info')
        return None


def load_dict(country, data_path, data_info, data_name, index_col):
    region_path_list = glob(data_path)

    if len(region_path_list) == 0:
        print(f'{data_name} dataset in {data_path} is not exists!')
        save_setting(data_info, f'req_{data_name}_info')
        raise FileNotFoundError(data_path)

    data_dict = dict()
    for data_path in region_path_list:
        _, elem = split(data_path)
        elem = elem.split('.csv')[0]

        if data_info is None:
            if elem == 'r0':
                continue
        else:
            if elem not in load_regions(country):
                continue

        elem_df = pd.read_csv(data_path, index_col=index_col)
        data_dict.update({elem: elem_df})

    return data_dict


def load_preprocessed_data(country, pre_info):
    print(f'load {get_country_name(country)} preprocessed data')
    pre_path = join(DATASET_PATH, get_country_name(country), 'preprocessed', pre_info.get_hash(), '*.csv')
    pre_dict = load_dict(country, pre_path, pre_info, 'preprocessed', 'date')
    return pre_dict


def load_debug_dict(country, pre_hash, test_hash):
    print(f'load variables for debugging in {get_country_name(country)}')
    debug_path = join(RESULT_PATH, get_country_name(country), f'{pre_hash}_{test_hash}', '*.csv')
    debug_dict = load_dict(country, debug_path, None, 'debug', 'regions')
    return debug_dict


def load_r0_df(country, pre_hash, test_hash):
    r0_path = join(RESULT_PATH, get_country_name(country),
                   f'{pre_hash}_{test_hash}', 'r0.csv')
    r0_df = pd.read_csv(r0_path, index_col='regions')
    return r0_df


def load_rho_df(country, pre_info, test_info):
    print(f'load {get_country_name(country)} rho dataframe')
    rho_path = join(DATASET_PATH, get_country_name(country), 'rho',
                    f'{pre_info.get_hash()}_{test_info.get_hash()}', 'rho.csv')
    try:
        rho_df = pd.read_csv(rho_path, index_col='regions')
        return rho_df
    except FileNotFoundError as e:
        print(e)
        return None


def load_tg_df(country):
    tg_path = join(DATASET_PATH, get_country_name(country), 'tg.csv')
    tg_df = pd.read_csv(tg_path, index_col='regions')
    return tg_df


def save_r0_df(r0_df, country, pre_hash, test_hash):
    r0_path = join(RESULT_PATH, get_country_name(country), f'{pre_hash}_{test_hash}')
    Path(r0_path).mkdir(parents=True, exist_ok=True)
    saving_path = join(r0_path, 'r0.csv')
    r0_df.to_csv(saving_path)
    print(f'saving r0 dataframe to {saving_path}')


def save_rho_df(rho_df, country, pre_hash, test_hash):
    rho_path = join(DATASET_PATH, get_country_name(country), 'rho',
                    f'{pre_hash}_{test_hash}')
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


def save_debug_dict(debug_dict, country, pre_hash, test_hash):
    debug_path = join(RESULT_PATH, get_country_name(country), f'{pre_hash}_{test_hash}')
    Path(debug_path).mkdir(parents=True, exist_ok=True)

    for key, debug_df in debug_dict.items():
        key_path = join(debug_path, f'{key}.csv')
        debug_df.to_csv(key_path)
        print(f'saving {key} values to {key_path}')


def save_setting(param_class, class_name):
    if param_class is None:
        return

    new_param_dict = dict()
    new_param_dict.update({'hash': param_class.get_hash()})

    for field in fields(param_class):
        if field.name[0] == '_' or field.name == 'info_type': continue
        new_param_dict.update({field.name: getattr(param_class, field.name)})

    param_df = pd.DataFrame(columns=list(new_param_dict.keys()))
    param_df = param_df.append(new_param_dict, ignore_index=True)
    param_df = param_df.set_index('hash')

    filename = f'{class_name}.csv'
    if isfile(join(SETTING_PATH, filename)):
        df = pd.read_csv(join(SETTING_PATH, filename), index_col='hash')
        if param_class.get_hash() not in df.index.tolist():
            df = param_df.append(df, ignore_index=False)
            df.to_csv(join(SETTING_PATH, filename))
            print(f'updating settings to {join(SETTING_PATH, filename)}')
    else:
        param_df.to_csv(join(SETTING_PATH, filename))
        print(f'saving settings to {join(SETTING_PATH, filename)}')


if __name__ == '__main__':
    country = Country.INDIA
    link_df = load_links(country)

    pre_info = PreprocessInfo(country=country, start=link_df['start_date'], end=link_df['end_date'],
                              increase=True, daily=True, remove_zero=True,
                              smoothing=True, window=5, divide=False, info_type=InfoType.PRE)
    test_info = PreprocessInfo(country=country, start=link_df['start_date'], end=link_df['end_date'],
                               increase=False, daily=True, remove_zero=True,
                               smoothing=True, window=5, divide=False, info_type=InfoType.TEST)

    load_debug_dict(country, pre_info.get_hash(), test_info.get_hash())
