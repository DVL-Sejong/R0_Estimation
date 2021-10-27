from R0_Estimation.datatype import Country, PreprocessInfo, InfoType
from R0_Estimation.estimation import get_estimate_r0_df
from R0_Estimation.io import load_links

import argparse


def get_args():
    parser = argparse.ArgumentParser(description='r0_estimation')

    parser.add_argument(
        "--country", type=str, default='italy',
        choices=['italy', 'india', 'us', 'china'],
        help="Country name"
    )

    args = parser.parse_args()
    return args


def main(args):
    country = Country(args.country.upper())
    link_df = load_links(country)

    pre_info = PreprocessInfo(country=country, start=link_df['start_date'], end=link_df['end_date'],
                              increase=True, daily=True, remove_zero=True,
                              smoothing=True, window=5, divide=False, info_type=InfoType.PRE)
    test_info = PreprocessInfo(country=country, start=link_df['start_date'], end=link_df['end_date'],
                               increase=False, daily=True, remove_zero=True,
                               smoothing=True, window=5, divide=False, info_type=InfoType.TEST)

    r0_df = get_estimate_r0_df(country, pre_info, test_info)
    return r0_df


if __name__ == '__main__':
    args = get_args()
    r0_df = main(args)
