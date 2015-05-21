###  Author: Dominik Znidar <dominik.znidar@3fs.si>
###
###  Collects data from custom performance log and spits out aggregated
###  metric values (MetricObjects) based on the data found inside the lines.
###
###  Request paths are sanitized to smaller set (check path_regs). Path will be
###  classified as 'unknown' if a match is not found.
###
###  Based on MetricLogster which is Copyright 2011, Etsy, Inc.

import re
import optparse
import json

from logster.parsers import stats_helper

from logster.logster_helper import MetricObject, LogsterParser
from logster.logster_helper import LogsterParsingException

class PerformanceLogster(LogsterParser):

    def __init__(self, option_string=None):
        '''Initialize any data structures or variables needed for keeping track
        of the tasty bits we find in the log we are parsing.'''

        self.counts = {}
        self.times = {}

        if option_string:
            options = option_string.split(' ')
        else:
            options = []

        optparser = optparse.OptionParser()
        optparser.add_option('--percentiles', '-p', dest='percentiles', default='90',
                            help='Comma-separated list of integer percentiles to track: (default: "90")')

        optparser.add_option('--mapping', '-m', dest='mapping', default='',
                            help='Path to a mapping file')

        opts, args = optparser.parse_args(args=options)

        self.percentiles = opts.percentiles.split(',')

        # General regular expressions, expecting the metric name to be included in the log file.

        self.request_reg = re.compile('^(?P<method>\w+) (?P<path>[^\s]+)')

        self.path_regs = self.parse_mapping_file(opts.mapping)

        self.valid_request_methods = [
            'GET',
            'POST',
            'HEAD',
            'DELETE',
            'PUT',
            'OPTIONS'
        ]
        self.invalid_request_method = 'invalid'

    def parse_line(self, line):
        '''This function should digest the contents of one line at a time, updating
        object's state variables. Takes a single argument, the line to be parsed.'''

        try:
            # parse json
            obj = json.loads(line)
            # read data
            status = obj['request']['status']
            requestTime = float(obj['request']['request_time']) * 1000
            request = obj['request']['request']
            # upstream time can be set to "-" and could fail
            try:
                upstreamTime = float(obj['request']['upstream_response_time']) * 1000
            except Exception, e:
                upstreamTime = False

            # extract request method (GET, ...) and path (/profile/..), skip the line if it fails
            path_match = self.request_reg.match(request)
            if path_match:
                bits = path_match.groupdict()
                method = bits['method']
                path = bits['path']
            else:
                raise LogsterParsingException, "failed to extract request method and path"

            # compose the root path
            rootPath = 'http_%s.%s.%s' % (status, self.sanitize_request_path(path), self.sanitize_request_method(method))

            # add timer metric for response time
            requestTimePath = rootPath + ".responseTime"
            if not self.times.has_key(requestTimePath):
                self.times[requestTimePath] = {'unit': 'ms', 'values': []};
            self.times[requestTimePath]['values'].append(requestTime)

            # add timer for upstream time (if available)
            if not type(upstreamTime) is bool:
                upstreamTimePath = rootPath + ".upstreamTime"
                if not self.times.has_key(upstreamTimePath):
                    self.times[upstreamTimePath] = {'unit': 'ms', 'values': []};
                self.times[upstreamTimePath]['values'].append(requestTime)

        except Exception, e:
            raise LogsterParsingException, "parsing failed with %s" % e

    def get_state(self, duration):
        '''Run any necessary calculations on the data collected from the logs
        and return a list of metric objects.'''

        self.duration = duration
        metrics = []

        # loop all the collected timers
        for time_name in self.times:
            values = self.times[time_name]['values']
            unit = self.times[time_name]['unit']
            # add counter
            if self.duration > 0:
                metrics.append(MetricObject(time_name+'.count', len(values) / self.duration))
            # calculate statistical values
            metrics.append(MetricObject(time_name+'.mean', stats_helper.find_mean(values), unit))
            metrics.append(MetricObject(time_name+'.median', stats_helper.find_median(values), unit))
            metrics += [MetricObject('%s.%sth_percentile' % (time_name,percentile), stats_helper.find_percentile(values,int(percentile)), unit) for percentile in self.percentiles]

        return metrics

    def sanitize_request_path(self, path):
        # loop path_regs and try to find the first match
        for (group, reg) in self.path_regs:
            # check if regexp matches the path
            if reg.match(path):
                return group

        # classify as unknown if match is not found
        return "unknown"

    def sanitize_request_method(self, method):
        method = method.upper()
        if method in self.valid_request_methods:
            return method
        return self.invalid_request_method

    def parse_mapping_file(self, mapping_file):
        # read all lines from the mapping filfe
        if not(mapping_file):
            return ()

        try:
            lines = [line.rstrip('\n') for line in open(mapping_file)]
        except IOError, e:
            raise LogsterParsingException("failed to read file %s with error \"%s\"" % (mapping_file, e))

        mapping_re = re.compile('^(?P<group>[\w-]+)\s+(?P<regexp>.*)$')

        mapping = ()

        # loop all lines
        for line in lines:
            # check if line matches the expected format (mapping_re)
            matches = mapping_re.match(line)
            if matches:
                # append to path_regs tupple
                mapping += ((matches.group('group'), re.compile(matches.group('regexp'))),)

        return mapping
