# ec2-spot-price: Retrieve Amazon EC2 spot instance price

This Python module provides simple functions and command to retrieve [Amazon EC2 spot instance price](https://aws.amazon.com/ec2/spot/pricing/) by AWS API


## Install

```sh
pip install ec2-spot-price
```

## Setup

You should setup [AWS authentication credentials](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html) which have permissions to access EC2 [`DescribeSpotPriceHistory`](https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_DescribeSpotPriceHistory.html) API. A simple way to do is to [create IAM user](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html) and attach [`AmazonEC2ReadOnlyAccess`](https://console.aws.amazon.com/iam/home#policies/arn:aws:iam::aws:policy/AmazonEC2ReadOnlyAccess) policy directly. (Or you can use existent credentials which have permissions to access that API)

### Access IAM console

Login to AWS console and access [IAM console](https://console.aws.amazon.com/iam/home)

### Add new IAM user

Add new IAM user like the following.

- User name: `myuser`  # whatever you want
- Access type: Programmatic access
- Set permissions: Attach existing policies directly
- Policy name: `AmazonEC2ReadOnlyAccess`
- Download .csv


### Edit ~/.aws/credentials

You can use "[named profile](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-profiles.html)" to have multiple credentials settings.

```ini:~/.aws/credentials
[myprofile]  # whatever you want, or [default]
aws_access_key_id=[copy from csv]
aws_secret_access_key=[copy from csv]
region=us-east-2  # wherever you want
```

## Usage

### Run as command

You can run `ec2_spot_price` command to retrieve spot instance prices.

If you use "named profile" in credentials file, you need to specify `AWS_PROFILE` environment variable.

```sh
export AWS_PROFILE=myprofile
```

Then, run command `ec2_spot_price` (or `python /path/to/ec2_spot_price.py`).

```sh
% ec2_spot_price -h
usage: ec2_spot_price.py [-h] [-r REGION_NAMES] [-i INSTANCE_TYPES]
                         [-o OS_TYPES] [-s SEP] [-v]

retrieve Amazon EC2 spot instance price

optional arguments:
  -h, --help            show this help message and exit
  -r REGION_NAMES, --region_names REGION_NAMES
                        filter regions. if "" is specified, retrieve all of
                        the regions. (default: "us-east-1,us-east-2,us-
                        west-1,us-west-2")
  -i INSTANCE_TYPES, --instance_types INSTANCE_TYPES
                        filter instance types e.g. "g3.4xlarge,p2.xlarge".
                        (default: retrieve all of the instance types)
  -o OS_TYPES, --os_types OS_TYPES
                        filter OS types. (default: "Linux/UNIX")
  -s SEP, --sep SEP     separator of CSV. (default: ",")
  -v, --verbose         increase output verbosity
```

You can specify region names by `-r`, instance types by `-i` and OS types by `-o`. For example, the following command shows CSV of `us-east-1,us-east-2` regions, `c5.xlarge,c5d.xlarge` instances and `Linux/UNIX` OS (default value).

```sh
% ec2_spot_price -r "us-east-1,us-east-2" -i "c5.xlarge,c5d.xlarge"
SpotPrice,AvailabilityZone,InstanceType,ProductDescription,Timestamp
0.038000,us-east-2a,c5.xlarge,Linux/UNIX,2021-02-21 02:12:51+00:00
0.038000,us-east-2b,c5.xlarge,Linux/UNIX,2021-02-21 02:12:51+00:00
0.038000,us-east-2c,c5.xlarge,Linux/UNIX,2021-02-21 02:12:51+00:00
0.038000,us-east-2c,c5d.xlarge,Linux/UNIX,2021-02-21 08:05:53+00:00
0.038100,us-east-2a,c5d.xlarge,Linux/UNIX,2021-02-21 04:50:26+00:00
0.038100,us-east-2b,c5d.xlarge,Linux/UNIX,2021-02-21 03:59:40+00:00
0.066400,us-east-1f,c5d.xlarge,Linux/UNIX,2021-02-20 20:03:30+00:00
0.071700,us-east-1b,c5.xlarge,Linux/UNIX,2021-02-21 07:37:58+00:00
0.071800,us-east-1a,c5d.xlarge,Linux/UNIX,2021-02-20 16:31:38+00:00
0.073600,us-east-1d,c5.xlarge,Linux/UNIX,2021-02-21 06:21:58+00:00
0.075000,us-east-1c,c5.xlarge,Linux/UNIX,2021-02-21 08:54:30+00:00
0.077100,us-east-1a,c5.xlarge,Linux/UNIX,2021-02-21 08:03:27+00:00
0.081500,us-east-1d,c5d.xlarge,Linux/UNIX,2021-02-21 07:55:25+00:00
0.082700,us-east-1c,c5d.xlarge,Linux/UNIX,2021-02-21 03:41:22+00:00
0.091100,us-east-1b,c5d.xlarge,Linux/UNIX,2021-02-21 09:45:08+00:00
0.103000,us-east-1f,c5.xlarge,Linux/UNIX,2021-02-21 06:55:57+00:00
```

In this case, you should use `c5.xlarge` at `us-east-2` region.

An another example to retrieve all of the spot prices in all regions with verbose option.

```sh
% ec2_spot_price -r "" -i "" -o "" -v > spot_prices.csv
2021-02-21 20:21:38,686 INFO get_spot_price: retrieving from eu-north-1...
2021-02-21 20:21:45,047 INFO get_spot_price: retrieving from eu-north-1...done. 1455 items.
...
2021-02-21 20:23:18,585 INFO get_spot_price: retrieving from us-west-2...
2021-02-21 20:23:26,142 INFO get_spot_price: retrieving from us-west-2...done. 4880 items.
2021-02-21 20:23:26,145 INFO get_spot_prices: retrieved 49627 items from ['eu-north-1', 'ap-south-1', 'eu-west-3', 'eu-west-2', 'eu-west-1', 'ap-northeast-2', 'ap-northeast-1', 'sa-east-1', 'ca-central-1', 'ap-southeast-1', 'ap-southeast-2', 'eu-central-1', 'us-east-1', 'us-east-2', 'us-west-1', 'us-west-2'].
```

Then open `spot_prices.csv` with spread sheet application like Excel.


### Use as module

There are two functions. `get_spot_prices` retrieves spot prices as list. `spot_prices_to_csv` convert spot prices to CSV.

```python
% python
>>> import sys
>>> import ec2_spot_price
>>> r = ec2_spot_price.get_spot_prices(['us-east-1', 'us-east-2'], ['c5.xlarge', 'c5d.xlarge'], ['Linux/UNIX'])
>>> len(r)
16
>>> ec2_spot_price.spot_prices_to_csv(r, path_or_buf=sys.stdout, index=False, sort=True)
SpotPrice,AvailabilityZone,InstanceType,ProductDescription,Timestamp
0.038000,us-east-2a,c5.xlarge,Linux/UNIX,2021-02-21 02:12:51+00:00
0.038000,us-east-2b,c5.xlarge,Linux/UNIX,2021-02-21 02:12:51+00:00
0.038000,us-east-2c,c5.xlarge,Linux/UNIX,2021-02-21 02:12:51+00:00
0.038000,us-east-2c,c5d.xlarge,Linux/UNIX,2021-02-21 08:05:53+00:00
0.038100,us-east-2a,c5d.xlarge,Linux/UNIX,2021-02-21 04:50:26+00:00
0.038100,us-east-2b,c5d.xlarge,Linux/UNIX,2021-02-21 03:59:40+00:00
0.066400,us-east-1f,c5d.xlarge,Linux/UNIX,2021-02-20 20:03:30+00:00
0.071700,us-east-1b,c5.xlarge,Linux/UNIX,2021-02-21 07:37:58+00:00
0.071800,us-east-1a,c5d.xlarge,Linux/UNIX,2021-02-20 16:31:38+00:00
0.073600,us-east-1d,c5.xlarge,Linux/UNIX,2021-02-21 06:21:58+00:00
0.075000,us-east-1c,c5.xlarge,Linux/UNIX,2021-02-21 08:54:30+00:00
0.077100,us-east-1a,c5.xlarge,Linux/UNIX,2021-02-21 08:03:27+00:00
0.081500,us-east-1d,c5d.xlarge,Linux/UNIX,2021-02-21 07:55:25+00:00
0.082700,us-east-1c,c5d.xlarge,Linux/UNIX,2021-02-21 03:41:22+00:00
0.091100,us-east-1b,c5d.xlarge,Linux/UNIX,2021-02-21 09:45:08+00:00
0.103000,us-east-1f,c5.xlarge,Linux/UNIX,2021-02-21 06:55:57+00:00
```

An another example to retrieve all of the spot prices in all regions.
You can use `pd.DataFrame` for more specific filtering.

```python
% python
>>> import pandas as pd
>>> import ec2_spot_price
>>> r = ec2_spot_price.get_spot_prices([], [], [])
>>> len(r)
49627
>>> df = pd.DataFrame(r)
>>> df = df.query('ProductDescription == "Linux/UNIX"')
>>> df = df.drop(['Timestamp', 'ProductDescription'], axis=1)
>>> df = df.sort_values(by=['SpotPrice', 'AvailabilityZone', 'InstanceType'])
>>> df = df.query('InstanceType.str.match("c5.?\.xlarge")')
>>> df.head(20)
      AvailabilityZone InstanceType SpotPrice
41314       us-east-2a    c5.xlarge  0.038000
40412       us-east-2a   c5d.xlarge  0.038000
39457       us-east-2a   c5n.xlarge  0.038000
41313       us-east-2b    c5.xlarge  0.038000
39456       us-east-2b   c5n.xlarge  0.038000
41312       us-east-2c    c5.xlarge  0.038000
40831       us-east-2c   c5d.xlarge  0.038000
39455       us-east-2c   c5n.xlarge  0.038000
41169       us-east-2b   c5d.xlarge  0.038100
39969       us-east-2c   c5a.xlarge  0.043100
40929       us-east-2b   c5a.xlarge  0.044400
2501       ap-south-1c   c5a.xlarge  0.052800
1836       ap-south-1a   c5a.xlarge  0.053300
2406       ap-south-1b   c5a.xlarge  0.053400
1926       ap-south-1a   c5n.xlarge  0.054100
1816       ap-south-1b   c5d.xlarge  0.054100
2858       ap-south-1a    c5.xlarge  0.054200
2750       ap-south-1a   c5d.xlarge  0.054200
1810       ap-south-1b    c5.xlarge  0.054200
2109       ap-south-1b   c5n.xlarge  0.054200
```

## Links

- https://aws.amazon.com/ec2/spot/pricing/
- https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-spot-instances-history.html
- https://docs.aws.amazon.com/cli/latest/reference/ec2/describe-spot-price-history.html
- https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_DescribeSpotPriceHistory.html
- https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users_create.html
- https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html#configuration


## Author

Susumu OTA
