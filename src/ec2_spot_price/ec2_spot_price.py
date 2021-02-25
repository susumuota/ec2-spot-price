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

import boto3
import pandas as pd
from rich import box
from rich.console import Console
from rich.progress import track
from rich.table import Table


logger = logging.getLogger(__name__)
console = Console(stderr=True)


SPOT_PRICE_COLUMNS = {
    'SpotPrice': {'highlight': '[bold bright_cyan]', 'name': 'Price'},
    'AvailabilityZone': {'highlight': '[bold bright_magenta]', 'name': 'Zone'},
    'InstanceType': {'highlight': '[bold bright_green]', 'name': 'Instance'},
    'ProductDescription': {'highlight': '[bold bright_yellow]', 'name': 'OS'},
    'Timestamp': {'highlight': '[bold bright_blue]', 'name': 'Timestamp'},
}


def get_spot_prices(region_names=[], instance_types=[], os_types=[],
                    page_size=1000, max_items=10000):
    def get_regions():
        ec2 = boto3.client('ec2')
        # https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_DescribeRegions.html
        return [r['RegionName'] for r in ec2.describe_regions()['Regions']]

    def get_prices(region_name, instance_types, os_types):
        ec2 = boto3.client('ec2', region_name=region_name)
        # https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_DescribeSpotPriceHistory.html
        # https://boto3.amazonaws.com/v1/documentation/api/latest/guide/paginators.html
        paginator = ec2.get_paginator('describe_spot_price_history')
        page_iterator = paginator.paginate(
            InstanceTypes=instance_types,
            ProductDescriptions=os_types,
            StartTime=datetime.now(timezone.utc).isoformat(),  # only latest
            PaginationConfig={'PageSize': page_size, 'MaxItems': max_items})
        return sum([p['SpotPriceHistory'] for p in page_iterator], [])

    def to_df(json):
        assert json and len(json) > 0
        df = pd.DataFrame(json)
        columns = list(SPOT_PRICE_COLUMNS.keys())
        df.sort_values(by=columns, inplace=True, ascending=True)
        return df[columns]

    regions = region_names or get_regions()
    prices = sum([get_prices(r, instance_types, os_types)
                  for r in track(regions, console=console, transient=True,
                                 description='Retrieving')], [])
    return to_df(prices)


def print_csv(prices):
    df = prices.copy(deep=True)
    df['Timestamp'] = df['Timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
    print(df.to_csv(path_or_buf=None, index=False), end='')


def print_table(prices):
    df = prices.copy(deep=True)
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
        description='retrieve Amazon EC2 spot instance price')
    parser.add_argument(
        '-r', '--region_names', type=str,
        default='us-east-1,us-east-2,us-west-1,us-west-2',
        help=('filter regions. if "" is specified, retrieve all of the '
              'regions. (default: "us-east-1,us-east-2,us-west-1,us-west-2")'))
    parser.add_argument(
        '-i', '--instance_types', type=str, default=None,
        help=('filter instance types e.g. "g3.4xlarge,p2.xlarge". (default: '
              'retrieve all of the instance types)'))
    parser.add_argument(
        '-o', '--os_types', type=str, default='Linux/UNIX',
        help='filter OS types. (default: "Linux/UNIX")')
    parser.add_argument(
        '-csv', '--csv', action='store_true',
        help='output CSV format. (default: False)')
    args = parser.parse_args()
    regions = args.region_names.split(',') if args.region_names else []
    instances = args.instance_types.split(',') if args.instance_types else []
    oss = args.os_types.split(',') if args.os_types else []
    prices = get_spot_prices(regions, instances, oss)
    (print_csv if args.csv else print_table)(prices)
    return 0


if __name__ == '__main__':
    sys.exit(main())
