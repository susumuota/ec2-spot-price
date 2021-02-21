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


logger = logging.getLogger(__name__)


def get_spot_prices(region_names=[], instance_types=[], os_types=[],
                    page_size=1000, max_items=10000):
    def get_region_names():
        ec2 = boto3.client('ec2')
        # https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_DescribeRegions.html
        return [r['RegionName'] for r in ec2.describe_regions()['Regions']]
    def get_spot_price(region_name, instance_types, os_types):
        ec2 = boto3.client('ec2', region_name=region_name)
        logger.info(f'retrieving from {region_name}...')
        # https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_DescribeSpotPriceHistory.html
        # https://boto3.amazonaws.com/v1/documentation/api/latest/guide/paginators.html
        paginator = ec2.get_paginator('describe_spot_price_history')
        page_iterator = paginator.paginate(
            InstanceTypes=instance_types,
            ProductDescriptions=os_types,
            StartTime=datetime.now(timezone.utc).isoformat(), # only latest one
            PaginationConfig={'PageSize': page_size, 'MaxItems': max_items})
        rs = sum([p['SpotPriceHistory'] for p in page_iterator], [])
        logger.info(f'retrieving from {region_name}...done. {len(rs)} items.')
        return rs
    rs = region_names or get_region_names()
    ps = sum([get_spot_price(r, instance_types, os_types) for r in rs], [])
    if ps and len(ps) > 0:
        logger.info(f'retrieved {len(ps)} items from {rs}.')
    else:
        logger.warning(f'No items found. args: {region_names}, {instance_types}, {os_types}')
    return ps

def spot_prices_to_csv(spot_prices, path_or_buf=None,
                       columns=['SpotPrice', 'AvailabilityZone', 'InstanceType',
                                'ProductDescription', 'Timestamp'],
                       sep=',', header=True, index=True,
                       sort=False, ascending=True):
    if spot_prices and len(spot_prices) > 0:
        df = pd.DataFrame(spot_prices)
        if sort:
            df.sort_values(by=columns, ascending=ascending, inplace=True)
        return df.to_csv(path_or_buf=path_or_buf, columns=columns, sep=sep,
                         header=header, index=index)
    else:
        return '' # or None?


def main():
    parser = argparse.ArgumentParser(description='retrieve Amazon EC2 spot instance price')
    parser.add_argument('-r', '--region_names', type=str,
                        default='us-east-1,us-east-2,us-west-1,us-west-2',
                        help='filter regions. if "" is specified, retrieve all of the regions. (default: "us-east-1,us-east-2,us-west-1,us-west-2")')
    parser.add_argument('-i', '--instance_types', type=str,
                        default=None,
                        help='filter instance types e.g. "g3.4xlarge,p2.xlarge". (default: retrieve all of the instance types)')
    parser.add_argument('-o', '--os_types', type=str,
                        default='Linux/UNIX',
                        help='filter OS types. (default: "Linux/UNIX")')
    parser.add_argument('-s', '--sep', type=str,
                        default=',',
                        help='separator of CSV. (default: ",")')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='increase output verbosity')
    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(format='%(asctime)s %(levelname)s %(funcName)s: %(message)s')
        logging.getLogger('ec2_spot_price').setLevel(logging.INFO)
        logging.getLogger(__name__).setLevel(logging.INFO)
    r = args.region_names.split(',') if args.region_names else []
    i = args.instance_types.split(',') if args.instance_types else []
    o = args.os_types.split(',') if args.os_types else []
    spot_prices_to_csv(get_spot_prices(r, i, o),
                       path_or_buf=sys.stdout, sep=args.sep, index=False, sort=True)
    return 0


if __name__ == '__main__':
    sys.exit(main())
