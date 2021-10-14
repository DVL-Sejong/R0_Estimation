from R0_Estimation.datatype import Country, PreprocessInfo, InfoType
from R0_Estimation.io import load_sird_data, load_tg_df, load_regions, save_debug_dict
from R0_Estimation.io import save_r0_df, load_population, load_links
from R0_Estimation.preprocess import get_t_value, get_rho_df, get_delayed_number_of_tests
from R0_Estimation.util import generate_dataframe

import math


def get_empty_dfs_for_debugging(country, sird_info, test_info, delay):
    rho_df = get_rho_df(country, sird_info, test_info, delay)
    estimate_dates = rho_df.columns.to_list()

    regions = load_regions(country)
    suspect_df = generate_dataframe(regions, estimate_dates, 'regions')
    yt_df = generate_dataframe(regions, estimate_dates, 'regions')
    t_df = generate_dataframe(regions, estimate_dates, 'regions')
    log_y_df = generate_dataframe(regions, estimate_dates, 'regions')
    lambda_df = generate_dataframe(regions, estimate_dates, 'regions')

    debug_dict = {'suspect': suspect_df, 'yt': yt_df, 't': t_df,
                  'log_y': log_y_df, 'lambda': lambda_df}
    return debug_dict


def get_estimate_r0_df(country, sird_info, test_info, delay):
    sird_dict = load_sird_data(country, sird_info)
    rho_df = get_rho_df(country, sird_info, test_info, delay)
    tg_df = load_tg_df(country)

    regions = load_regions(country)
    estimate_dates = rho_df.columns.to_list()

    debug_dict = get_empty_dfs_for_debugging(country, sird_info, test_info, delay)
    r0_df = generate_dataframe(regions, estimate_dates, 'regions')

    population_df = load_population(country)
    test_num_df = get_delayed_number_of_tests(country, test_info, delay)

    for region in regions:
        print(f'estmate r0 value in {region}')
        region_sird = sird_dict[region]
        region_population = population_df.loc[region, 'population']

        for estimate_date in estimate_dates:
            rho = rho_df.loc[region, estimate_date]
            infected = region_sird.loc[estimate_date, 'infected']
            test_num = test_num_df.loc[region, estimate_date]
            suspect = (1 + (infected/region_population)) * test_num
            debug_dict['suspect'].loc[region, estimate_date] = suspect

            y_t = suspect * rho + infected
            debug_dict['yt'].loc[region, estimate_date] = y_t

            t_value = get_t_value(country, region, estimate_date)
            debug_dict['t'].loc[region, estimate_date] = t_value

            log_y = -100 if y_t == 0 else math.log(y_t)
            debug_dict['log_y'].loc[region, estimate_date] = log_y

            lamda = log_y / t_value
            debug_dict['lambda'].loc[region, estimate_date] = lamda

            tg = tg_df.loc[region, 'Tg']
            r0 = 1 + lamda * tg + rho * (1 - rho) * pow(lamda * tg, 2)
            r0_df.loc[region, estimate_date] = r0

    save_debug_dict(debug_dict, country, sird_info.get_hash(), test_info.get_hash(), delay)
    save_r0_df(r0_df, country, sird_info.get_hash(), test_info.get_hash(), delay)
    return r0_df


if __name__ == '__main__':
    country = Country.INDIA
    link_df = load_links(country)

    sird_info = PreprocessInfo(country=country, start=link_df['start_date'], end=link_df['end_date'],
                              increase=True, daily=True, remove_zero=True,
                              smoothing=True, window=5, divide=False, info_type=InfoType.SIRD)
    test_info = PreprocessInfo(country=country, start=link_df['start_date'], end=link_df['end_date'],
                               increase=False, daily=True, remove_zero=True,
                               smoothing=True, window=5, divide=False, info_type=InfoType.TEST)
    delay = 7

    r0_df = get_estimate_r0_df(country, sird_info, test_info, delay)
