#!/usr/bin/env python

import twitter
import sys
import yaml
import logging

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()

screen_name = sys.argv[1]
conf_file = 'twitter.yaml'

try:
    conf = yaml.load(open(conf_file, 'rb').read())
except:
    log.exception('error: unable to read {} config file:'.format(conf_file))

api = twitter.Api(**conf)
statuses = api.GetUserTimeline(screen_name=screen_name, count=200)

f = open(screen_name + '.txt', 'w')
f.writelines(s.text.encode('ascii', 'ignore') + '\n' for s in statuses)
f.close()
