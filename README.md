# ec2-spot-price

Library and command for retrieving Amazon EC2 spot instance price


## Install

```sh
pip install ec2-spot-price
```

## Setup

You need to have IAM user to access EC2's DescribeSpotPriceHistory API.
A simple way to do is to add new user and attach AmazonEC2ReadOnlyAccess
policy.

Or you can use existent user which have permissions to access that API.

### Goto IAM Console

https://console.aws.amazon.com/iam/home

### Add new IAM user

```
User name: myuser  # whatever you want
Access type: Programmatic access
Set permissions: Attach existing policies directly
Policy name: AmazonEC2ReadOnlyAccess
Download .csv
```

### Edit ~/.aws/credentials

You can use "named profile" to have multiple credentials settings.
See https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-profiles.html

```
[myprofile]  # or [default]
aws_access_key_id=[copy from csv]
aws_secret_access_key=[copy from csv]
region=us-east-2  # wherever you want
```

## Usage

### Run Script

If you use [myprofile], you need to specify AWS_PROFILE environment
variable. If you use [default] section, you can omit AWS_PROFILE.

```
export AWS_PROFILE=myprofile
```


```
ec2_spot_price -r us-east-1 -i c5.xlarge
SpotPrice,AvailabilityZone,InstanceType,ProductDescription,Timestamp
0.072000,us-east-1b,c5.xlarge,Linux/UNIX,2021-02-20 19:20:57+00:00
0.074100,us-east-1d,c5.xlarge,Linux/UNIX,2021-02-20 17:39:28+00:00
0.076800,us-east-1c,c5.xlarge,Linux/UNIX,2021-02-20 16:06:29+00:00
0.077700,us-east-1a,c5.xlarge,Linux/UNIX,2021-02-20 19:12:58+00:00
0.106100,us-east-1f,c5.xlarge,Linux/UNIX,2021-02-20 14:32:58+00:00
```

### Use library

```
import sys
import ec2_spot_price
r = ec2_spot_price.get_spot_prices(['us-east-1'], ['g4dn.4xlarge'], ['Linux/UNIX'])
ec2_spot_price.spot_prices_to_csv(r, sys.stdout)
,SpotPrice,AvailabilityZone,InstanceType,ProductDescription,Timestamp
0,0.361200,us-east-1d,g4dn.4xlarge,Linux/UNIX,2021-02-19 22:39:19+00:00
1,0.361200,us-east-1f,g4dn.4xlarge,Linux/UNIX,2021-02-19 22:39:19+00:00
2,0.361200,us-east-1c,g4dn.4xlarge,Linux/UNIX,2021-02-19 22:39:19+00:00
3,0.361200,us-east-1b,g4dn.4xlarge,Linux/UNIX,2021-02-19 22:39:19+00:00
4,0.361200,us-east-1a,g4dn.4xlarge,Linux/UNIX,2021-02-19 22:39:19+00:00
```

## See also

https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_DescribeSpotPriceHistory.html
https://boto3.amazonaws.com/v1/documentation/api/latest/guide/quickstart.html#configuration
https://aws.amazon.com/ec2/spot/pricing/


## Author

Susumu OTA


