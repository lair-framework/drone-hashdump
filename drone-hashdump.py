#!/usr/bin/env python
"""drone-hashdump

Usage:
    drone-hashdump [options] <id> <file>
    drone-hashdump --version

Options:
    -h --help       Show usage.
    --version       Show version.
    -k              Allow insecure SSL connections.

"""
import os
from sys import exit
from urlparse import urlparse
from netaddr import IPAddress, AddrFormatError
from docopt import docopt
from pylair import models
from pylair import client


def main():
    arguments = docopt(__doc__, version='drone-hashdump 1.0.0')
    lair_url = ''
    try:
        lair_url = os.environ['LAIR_API_SERVER']
    except KeyError:
        print "Fatal: Missing LAIR_API_SERVER environment variable"
        exit(1)

    u = urlparse(lair_url)
    if u.username is None or u.password is None:
        print "Fatal: Missing username and/or password"
        exit(1)

    project_id = arguments['<id>']
    project = dict(models.project)
    project['id'] = project_id
    project['commands'] = [{'command': 'iphashdump', 'tool': 'iphashdump'}]
    project['tool'] = 'drone-hashdump'

    opts = client.Options(u.username, u.password, u.hostname + ":" + str(u.port), project_id, scheme=u.scheme,
                          insecure_skip_verify=arguments['-k'])


    lines = []
    cidrs = set()
    try:
        lines = [line.rstrip('\n') for line in open(arguments['<file>'])]
    except IOError as e:
        print "Fatal: Could not open file. Error: {0}".format(e)
        exit(1)
    for line in lines:
        entry = line.split(":")
        print entry
        credential = dict(models.credential)
        credential['projectId'] = project_id
        credential['username'] = entry[0]
        credential['hash'] = entry[2]+":"+entry[3] 

        project['credentials'].append(credential)

    res = client.import_project(project, opts)
    if res['status'] == 'Error':
        print "Fatal: " + res['message']
        exit(1)
    print "Success: Operation completed successfully"


if __name__ == '__main__':
    main()

