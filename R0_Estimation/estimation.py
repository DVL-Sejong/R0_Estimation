from R0_Estimation.datatype import Country, PreprocessInfo, InfoType
from R0_Estimation.io import load_tg_df, load_regions, save_debug_dict, load_preprocessed_data
from R0_Estimation.io import save_r0_df, load_links
from R0_Estimation.preprocess import get_t_value, get_rho_df
from R0_Estimation.util import generate_dataframe

import math


def get_empty_dfs_for_debugging(country, rho_df):
    estimate_dates = rho_df.columns.to_list()

    regions = load_regions(country)
    yt_df = generate_dataframe(regions, estimate_dates, 'regions')
    t_df = generate_dataframe(regions, estimate_dates, 'regions')
    log_y_df = generate_dataframe(regions, estimate_dates, 'regions')
    lambda_df = generate_dataframe(regions, estimate_dates, 'regions')

    debug_dict = {'yt': yt_df, 't': t_df, 'log_y': log_y_df, 'lambda': lambda_df}
    return debug_dict


def get_estimate_r0_df(country, pre_info, test_info):
    pre_dict = load_preprocessed_data(country, pre_info)
    rho_df = get_rho_df(country, pre_info, test_info)
    tg_df = load_tg_df(country)

    regions = load_regions(country)
    estimate_dates = rho_df.columns.to_list()

    debug_dict = get_empty_dfs_for_debugging(country, rho_df)
    r0_df = generate_dataframe(regions, estimate_dates, 'regions')

    for region in regions:
        print(f'estmate r0 value in {region}')
        region_pre = pre_dict[region]

        for estimate_date in estimate_dates:
            rho = rho_df.loc[region, estimate_date]

            y_t = region_pre.loc[estimate_date, 'active']
            debug_dict['yt'].loc[region, estimate_date] = y_t

            t_value = get_t_value(country, region, estimate_date)
            debug_dict['t'].loc[region, estimate_date] = t_value

            log_y = math.log(y_t)
            debug_dict['log_y'].loc[region, estimate_date] = log_y

            lamda = log_y / t_value
            debug_dict['lambda'].loc[region, estimate_date] = lamda

            tg = tg_df.loc[region, 'Tg']
            r0 = 1 + lamda * tg + rho * (1 - rho) * pow(lamda * tg, 2)
            r0_df.loc[region, estimate_date] = r0

    save_debug_dict(debug_dict, country, pre_info.get_hash(), test_info.get_hash())
    save_r0_df(r0_df, country, pre_info.get_hash(), test_info.get_hash())
    return r0_df


if __name__ == '__main__':
    country = Country.ITALY
    link_df = load_links(country)

    pre_info = PreprocessInfo(country=country, start=link_df['start_date'], end=link_df['end_date'],
                              increase=True, daily=True, remove_zero=True,
                              smoothing=True, window=5, divide=False, info_type=InfoType.PRE)
    test_info = PreprocessInfo(country=country, start=link_df['start_date'], end=link_df['end_date'],
                               increase=False, daily=True, remove_zero=True,
                               smoothing=True, window=5, divide=False, info_type=InfoType.TEST)

    r0_df = get_estimate_r0_df(country, pre_info, test_info)
