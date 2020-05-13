from . import Netio
from pathlib import Path
import argparse
import itertools
import os
import requests
import sys
import yaml


def create_output_actions(args):
    actions = {}

    for on in flatten(args.on):
        actions[int(on)] = Netio.ACTION.ON

    for off in flatten(args.off):
        actions[int(off)] = Netio.ACTION.OFF

    return actions


def flatten(iterable):
    return itertools.chain.from_iterable(iterable)


def main():
    netio_cli(sys.argv)


def netio_cli(argv):
    # Disable warnings about certificate's subjectAltName versus commonName
    # entry.
    #
    # TODO: How to get this right?
    requests.packages.urllib3.disable_warnings()


    default_config = os.getenv('NETIO_CONFIG', 'netio.yml')


    parser = argparse.ArgumentParser(description='NETIO command line tool',
        epilog='There is explicitly no support for specifying the device password '
            'via command line arguments for not having it ending up in history '
            'and process listings. Please use a configuration file. See '
            '\'netio.yml.example\' for an example.'
            'You may specify the default configuration file in the environment '
            'variable NETIO_CONFIG.')
    parser.add_argument('--config', type=Path, default=default_config,
        help='YAML configuration for device name, certificate and password (default is {})'.format(default_config))
    parser.add_argument('--on', metavar='OUTPUT', action='append', nargs='+',
        default=[],
        help='outputs to turn on')
    parser.add_argument('--off', metavar='OUTPUT', action='append', nargs='+',
        default=[],
        help='outputs to turn off')


    args = parser.parse_args(argv[1:])

    # TOOD: Is there some config-ish format supported by Python's standard
    # library?
    with args.config.open() as f:
        config = yaml.load(f)


    # If the certificate is given as a relative path. Its position is assumed
    # relative to the config file.
    #
    # TODO: Allow HTTP connections without a cert.
    cert = Path(config['cert'])
    if not cert.is_absolute():
        cert = args.config.parent / cert


    # TODO: Make URL scheme configurable.
    url = 'http://{}/netio.json'.format(config['device'])
    auth = ('write', config['password'])
    actions = create_output_actions(args)

    device = Netio(url, auth_rw=auth, verify=None)
    device.set_outputs(actions)




if __name__ == '__main__':
    main()
