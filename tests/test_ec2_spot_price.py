from ec2_spot_price import __version__, get_spot_prices, spot_prices_to_csv


def test_version():
    assert __version__ == '0.1.17'

def test_get_spot_prices():
    r = get_spot_prices(['us-east-1', 'us-east-2', 'us-west-1', 'us-west-2'],
                        ['c5.xlarge', 'c5d.xlarge'],
                        ['Linux/UNIX'])
    assert len(r) == 28

def test_spot_prices_to_csv():
    r = get_spot_prices(['us-east-1', 'us-east-2', 'us-west-1', 'us-west-2'],
                        ['c5.xlarge', 'c5d.xlarge'],
                        ['Linux/UNIX'])
    csv = spot_prices_to_csv(r)
    assert len(csv) == 2034
