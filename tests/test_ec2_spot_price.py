from ec2_spot_price import __version__, get_spot_prices, print_csv, print_table


def test_version():
    assert __version__ == '0.2.1'

def test_get_spot_prices():
    sp = get_spot_prices(['us-east-1', 'us-east-2', 'us-west-1', 'us-west-2'],
                        ['c5.xlarge', 'c5d.xlarge'],
                        ['Linux/UNIX'])
    assert len(sp) == 28

def test_print_csv(capsys):
    sp = get_spot_prices(['us-east-1', 'us-east-2', 'us-west-1', 'us-west-2'],
                        ['c5.xlarge', 'c5d.xlarge'],
                        ['Linux/UNIX'])
    print_csv(sp)
    captured = capsys.readouterr()
    assert len(captured.out) == 1791

def test_print_table(capsys):
    sp = get_spot_prices(['us-east-1', 'us-east-2', 'us-west-1', 'us-west-2'],
                        ['c5.xlarge', 'c5d.xlarge'],
                        ['Linux/UNIX'])
    print_table(sp)
    captured = capsys.readouterr()
    assert len(captured.err) == 2368
