from R0_Estimation.datatype import Country, PreprocessInfo
from R0_Estimation.io import load_sird_data, load_rho_df, load_tg_df, load_regions
from R0_Estimation.io import save_r0_df, load_population, load_number_of_tests, load_links
from R0_Estimation.preprocess import get_t_value, get_rho_df

import pandas as pd
import math


def get_estimate_r0_df(country, sird_info, test_info, delay):
    sird_dict = load_sird_data(country, sird_info.get_hash())
    rho_df = load_rho_df(country, sird_info, test_info, delay)
    if rho_df is None:
        rho_df = get_rho_df(country, sird_info, test_info, delay)
    tg_df = load_tg_df(country)

    regions = load_regions(country)
    estimate_dates = rho_df.columns.to_list()

    r0_df = pd.DataFrame(index=regions, columns=estimate_dates)
    r0_df.index.name = 'regions'

    population_df = load_population(country)
    test_num_df = load_number_of_tests(country, test_info.get_hash())

    for region in regions:
        print(f'estmate r0 value in {region}')
        region_sird = sird_dict[region]
        region_population = population_df.loc[region, 'population']

        for estimate_date in estimate_dates:
            rho = rho_df.loc[region, estimate_date]
            infected = region_sird.loc[estimate_date, 'infected']
            test_num = test_num_df.loc[region, estimate_date]
            suspect = (1 + (infected/region_population)) * test_num
            y_t = suspect * rho + infected
            t_value = get_t_value(country, region, estimate_date)
            log_y = 0 if y_t == 0 else math.log(y_t)
            lamda = log_y / t_value
            tg = tg_df.loc[region, 'Tg']
            r0 = 1 + lamda * tg + rho * (1 - rho) * pow(lamda * tg, 2)
            r0_df.loc[region, estimate_date] = r0

    save_r0_df(r0_df, country, sird_info.get_hash(), test_info.get_hash(), delay)
    return r0_df


if __name__ == '__main__':
    country = Country.US
    link_df = load_links(country)

    sird_info = PreprocessInfo(country=country, start=link_df['start_date'], end=link_df['end_date'],
                              increase=True, daily=True, remove_zero=True,
                              smoothing=True, window=9, divide=False)
    test_info = PreprocessInfo(country=country, start=link_df['start_date'], end=link_df['end_date'],
                               increase=False, daily=True, remove_zero=True,
                               smoothing=True, window=5, divide=False)
    delay = 1

    r0_df = get_estimate_r0_df(country, sird_info, test_info, delay)
