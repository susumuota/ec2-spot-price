# -*- coding: utf-8 -*-

# Copyright 2021 Susumu OTA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import argparse
from datetime import datetime, timezone
import logging
import sys

try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:
    import importlib_metadata  # python < 3.8

import boto3
import pandas as pd
from rich import box
from rich.console import Console
from rich.progress import track
from rich.table import Table


__version__ = importlib_metadata.version(__package__)  # not __name__
logger = logging.getLogger(__name__)
console = Console(stderr=True)


SPOT_PRICE_COLUMNS = {
    'SpotPrice': {'highlight': '[bold bright_cyan]', 'name': 'Price'},
    'AvailabilityZone': {'highlight': '[bold bright_magenta]', 'name': 'Zone'},
    'InstanceType': {'highlight': '[bold bright_green]', 'name': 'Instance'},
    'ProductDescription': {'highlight': '[bold bright_yellow]', 'name': 'OS'},
    'Timestamp': {'highlight': '[bold bright_blue]', 'name': 'Timestamp'},
}


def spot_prices(regions=[], instances=[], oss=[],
                page_size=1000, max_items=10000):
    def all_regions():
        ec2 = boto3.client('ec2')
        # https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_DescribeRegions.html
        logger.debug('ec2.describe_regions...')
        rs = ec2.describe_regions()
        logger.debug(('ec2.describe_regions...done: '
                      f'retrieved {len(rs["Regions"])} items'))
        return [r['RegionName'] for r in rs['Regions']]

    def region_spot_prices(region, instances, oss):
        ec2 = boto3.client('ec2', region_name=region)
        # https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_DescribeSpotPriceHistory.html
        # https://boto3.amazonaws.com/v1/documentation/api/latest/guide/paginators.html
        paginator = ec2.get_paginator('describe_spot_price_history')
        page_iterator = paginator.paginate(
            InstanceTypes=instances,
            ProductDescriptions=oss,
            StartTime=datetime.now(timezone.utc).isoformat(),  # only latest
            PaginationConfig={'PageSize': page_size, 'MaxItems': max_items})
        logger.debug('ec2.describe_spot_price_history...')
        prices = sum([p['SpotPriceHistory'] for p in page_iterator], [])
        logger.debug(('ec2.describe_spot_price_history...done: '
                      f'retrieved {len(prices)} items from {region}'))
        return prices

    def to_df(prices_json):
        assert prices_json and len(prices_json) > 0
        df = pd.DataFrame(prices_json)
        columns = list(SPOT_PRICE_COLUMNS.keys())
        df.sort_values(by=columns, inplace=True, ascending=True)
        return df[columns]

    regions = regions or all_regions()
    prices = sum([region_spot_prices(r, instances, oss)
                  for r in track(regions, console=console, transient=True,
                                 description='Retrieving')], [])
    return to_df(prices)


def print_csv(prices_df):
    df = prices_df.copy(deep=True)
    df['Timestamp'] = df['Timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    print(df.to_csv(path_or_buf=None, index=False), end='')


def print_table(prices_df):
    df = prices_df.copy(deep=True)
    df['Timestamp'] = df['Timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    min_index = df['SpotPrice'] == df['SpotPrice'].min()
    for k, v in SPOT_PRICE_COLUMNS.items():
        df[k][min_index] = v['highlight'] + df[k][min_index]
    names = [v['name'] for v in SPOT_PRICE_COLUMNS.values()]
    table = Table(*names, box=box.HORIZONTALS)
    for row in df.itertuples(name=None):
        table.add_row(*list(row)[1:])
    console.print(table)


def main():
    parser = argparse.ArgumentParser(
        description='retrieve Amazon EC2 spot instance price.')
    parser.add_argument(
        '-r', '--region', type=str,
        default='us-east-1,us-east-2,us-west-1,us-west-2',
        help=('filter by regions. if "" is specified, retrieve all of the '
              'regions. (default: "us-east-1,us-east-2,us-west-1,us-west-2")'))
    parser.add_argument(
        '-i', '--instance', type=str, default=None,
        help=('filter by instance types e.g. "g3.4xlarge,p2.xlarge". '
              '(default: retrieve all of the instance types)'))
    parser.add_argument(
        '-o', '--os', type=str, default='Linux/UNIX',
        help='filter by OS types. (default: "Linux/UNIX")')
    parser.add_argument(
        '-csv', '--csv', action='store_true',
        help='output by CSV format. (default: False)')
    parser.add_argument(
        '-d', '--debug', action='store_true', help='show debug information.')
    parser.add_argument(
        '-V', '--version', action='version', help='show version.',
        version=f'%(prog)s {__version__}')
    args = parser.parse_args()
    if args.debug:
        logging.basicConfig(
            format='%(asctime)s %(levelname)s %(funcName)s: %(message)s')
        logging.getLogger(__name__).setLevel(logging.DEBUG)
    regions = args.region.split(',') if args.region else []
    instances = args.instance.split(',') if args.instance else []
    oss = args.os.split(',') if args.os else []
    prices = spot_prices(regions, instances, oss)
    (print_csv if args.csv else print_table)(prices)
    return 0


if __name__ == '__main__':
    sys.exit(main())
