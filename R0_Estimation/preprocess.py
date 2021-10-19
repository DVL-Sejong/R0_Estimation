from R0_Estimation.datatype import Country, PreprocessInfo, get_country_name, InfoType
from R0_Estimation.io import load_number_of_tests, load_regions, load_links, load_rho_df
from R0_Estimation.io import load_preprocessed_data
from R0_Estimation.io import save_rho_df, load_first_confirmed_date, save_tg_df
from R0_Estimation.util import get_period, generate_dataframe
from datetime import datetime


def get_dataset_dates(country, pre_info, test_info):
    num_test_df = load_number_of_tests(country, test_info)
    columns = num_test_df.columns.to_list()

    # test_numbers
    start_date1 = None
    end_date1 = datetime.strptime(columns[-1], '%Y-%m-%d')
    for column in columns:
        test_list = num_test_df[column]
        if len([elem for elem in test_list if elem == 0]) == 0:
            start_date1 = datetime.strptime(column, '%Y-%m-%d')
            break

    # first_confirmed
    first_confirmed_df = load_first_confirmed_date(country)
    first_dates = first_confirmed_df['first_date'].to_list()
    first_dates = [datetime.strptime(elem, '%Y-%m-%d') for elem in first_dates]
    start_date2 = min(first_dates)

    # preprocessed
    pre_dict = load_preprocessed_data(country, pre_info)
    pre_dates = pre_dict[next(iter(pre_dict))].index.tolist()
    start_date3 = datetime.strptime(pre_dates[0], '%Y-%m-%d')
    end_date3 = datetime.strptime(pre_dates[-1], '%Y-%m-%d')

    start_date = max(start_date1, start_date2, start_date3)
    end_date = min(end_date1, end_date3)
    period = get_period(start_date, end_date, out_date_format='%Y-%m-%d')
    return period


def get_rho_df(country, pre_info, test_info):
    print(f'get rho of {get_country_name(country)}')
    pre_dict = load_preprocessed_data(country, pre_info)
    test_num_df = load_number_of_tests(country, test_info)

    regions = load_regions(country)
    dataset_dates = get_dataset_dates(country, pre_info, test_info)
    rho_df = generate_dataframe(regions, dataset_dates, 'regions')

    for region in regions:
        for i, common_date in enumerate(dataset_dates):
            confirmed_value = pre_dict[region].loc[common_date, 'confirmed']
            test_numbers = test_num_df.loc[region, common_date]
            rho_df.loc[region, common_date] = confirmed_value / test_numbers

    save_rho_df(rho_df, country, pre_info.get_hash(), test_info.get_hash())
    return rho_df


def get_tg_df(country):
    tg_df = generate_dataframe(load_regions(country), ['Tg'], 'regions')
    tg_df.loc[:, :] = 6.9
    save_tg_df(country, tg_df)
    return tg_df


def get_t_value(country, region, target_date):
    first_confirmed_df = load_first_confirmed_date(country)
    first_date = datetime.strptime(first_confirmed_df.loc[region, 'first_date'], '%Y-%m-%d')
    t_value = (datetime.strptime(target_date, '%Y-%m-%d') - first_date).days + 1
    return t_value


if __name__ == '__main__':
    country = Country.ITALY
    link_df = load_links(country)

    pre_info = PreprocessInfo(country=country, start=link_df['start_date'], end=link_df['end_date'],
                               increase=True, daily=True, remove_zero=True,
                               smoothing=True, window=5, divide=False, info_type=InfoType.PRE)
    test_info = PreprocessInfo(country=country, start=link_df['start_date'], end=link_df['end_date'],
                               increase=True, daily=True, remove_zero=True,
                               smoothing=True, window=5, divide=False, info_type=InfoType.TEST)

    rho_df = get_rho_df(country, pre_info, test_info)
    tg_df = get_tg_df(country)
