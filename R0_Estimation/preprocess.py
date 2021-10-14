from R0_Estimation.datatype import Country, PreprocessInfo, get_country_name, InfoType
from R0_Estimation.io import load_number_of_tests, load_sird_data, load_regions, load_links, load_rho_df
from R0_Estimation.io import save_delayed_number_of_tests, load_delayed_number_of_tests
from R0_Estimation.io import save_rho_df, load_first_confirmed_date, save_tg_df
from R0_Estimation.util import get_period, generate_dataframe
from datetime import datetime


def get_delayed_number_of_tests(country, test_info, delay):
    delayed_tests_df = load_delayed_number_of_tests(country, test_info, delay)
    if delayed_tests_df is not None:
        return delayed_tests_df

    print(f'get number of tests of {get_country_name(country)}')

    if delay == 0:
        raise ValueError('delay can not be zero!')

    test_num_df = load_number_of_tests(country, test_info)

    if delay == 1:
        save_delayed_number_of_tests(test_num_df, country, test_info, delay)
        return test_num_df

    delayed_num_df = test_num_df.copy().iloc[:, delay:]
    for region, row in test_num_df.iterrows():
        for i, date in enumerate(test_num_df.columns):
            if i < delay: continue

            new_value = sum([row[test_num_df.columns[i - j]] for j in range(delay)])
            delayed_num_df.loc[region, date] = new_value

    save_delayed_number_of_tests(delayed_num_df, country, test_info, delay)
    return delayed_num_df


def get_dataset_dates(country, sird_info, test_info, delay):
    num_test_df = get_delayed_number_of_tests(country, test_info, delay)
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

    sird_dict = load_sird_data(country, sird_info)
    sird_dates = sird_dict[list(sird_dict.keys())[0]].index.tolist()
    start_date3 = datetime.strptime(sird_dates[0], '%Y-%m-%d')
    end_date3 = datetime.strptime(sird_dates[-1], '%Y-%m-%d')

    start_date = max(start_date1, start_date2, start_date3)
    end_date = min(end_date1, end_date3)
    period = get_period(start_date, end_date, out_date_format='%Y-%m-%d')
    return period


def get_rho_df(country, sird_info, test_info, delay=1):
    rho_df = load_rho_df(country, sird_info, test_info, delay)
    if rho_df is not None:
        return rho_df

    print(f'get rho of {get_country_name(country)}')
    sird_dict = load_sird_data(country, sird_info)
    test_num_df = get_delayed_number_of_tests(country, test_info, delay)

    regions = load_regions(country)
    dataset_dates = get_dataset_dates(country, sird_info, test_info, delay)
    rho_df = generate_dataframe(regions, dataset_dates[delay:], 'regions')

    for region in regions:
        for i, common_date in enumerate(dataset_dates):
            confirmed_value = sird_dict[region].loc[common_date, 'infected']
            test_numbers = test_num_df.loc[region, common_date]
            rho_df.loc[region, common_date] = confirmed_value / test_numbers

    save_rho_df(rho_df, country, sird_info.get_hash(), test_info.get_hash(), delay)
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

    sird_info = PreprocessInfo(country=country, start=link_df['start_date'], end=link_df['end_date'],
                               increase=True, daily=True, remove_zero=True,
                               smoothing=True, window=5, divide=False, info_type=InfoType.SIRD)
    test_info = PreprocessInfo(country=country, start=link_df['start_date'], end=link_df['end_date'],
                               increase=False, daily=True, remove_zero=True,
                               smoothing=True, window=5, divide=False, info_type=InfoType.TEST)
    delay = 14

    rho_df = get_rho_df(country, sird_info, test_info, delay)
