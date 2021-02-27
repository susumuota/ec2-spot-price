from ec2_spot_price import __version__, spot_prices, print_csv, print_table


def test_version():
    assert __version__ == '0.2.3'


def test_spot_prices():
    prices = spot_prices(['us-east-1', 'us-east-2', 'us-west-1', 'us-west-2'],
                         ['c5.xlarge', 'c5d.xlarge'],
                         ['Linux/UNIX'])
    assert len(prices) == 28


def test_print_csv(capsys):
    prices = spot_prices(['us-east-1', 'us-east-2', 'us-west-1', 'us-west-2'],
                         ['c5.xlarge', 'c5d.xlarge'],
                         ['Linux/UNIX'])
    print_csv(prices)
    captured = capsys.readouterr()
    assert len(captured.out) == 1791


def test_print_table(capsys):
    prices = spot_prices(['us-east-1', 'us-east-2', 'us-west-1', 'us-west-2'],
                         ['c5.xlarge', 'c5d.xlarge'],
                         ['Linux/UNIX'])
    print_table(prices)
    captured = capsys.readouterr()
    assert len(captured.err) == 2368
