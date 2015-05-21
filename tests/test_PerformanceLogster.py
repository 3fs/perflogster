from perf_logster.PerformanceLogster import PerformanceLogster
from logster.logster_helper import MetricObject
import unittest
import sys
import re

class test_performance_logster(unittest.TestCase):

    def test_full(self):
        # init parser
        p = PerformanceLogster('--mapping=tests/test.map')

        samples = [
            '{ "timestamp": "2014-10-10T06:30:32+00:00", "request": { "remote_addr": "192.168.56.1", "request": "GET /profile/me HTTP/1.1", "status": "200", "request_time": "0.406", "upstream_response_time": "0.406" } }',
            '{ "timestamp": "2014-10-10T06:30:36+00:00", "request": { "remote_addr": "192.168.56.1", "request": "GET / HTTP/1.1", "status": "200", "request_time": "0.413", "upstream_response_time": "0.413" } }'
        ]

        # parse samples
        for sample in samples:
            p.parse_line(sample)

        expected = [
            MetricObject('http_200.unknown.GET.upstreamTime.count', 1),
            MetricObject('http_200.unknown.GET.upstreamTime.mean', 413.0, 'ms'),
            MetricObject('http_200.unknown.GET.upstreamTime.median', 413.0, 'ms'),
            MetricObject('http_200.unknown.GET.upstreamTime.90th_percentile', 413.0, 'ms'),
            MetricObject('http_200.profile.GET.upstreamTime.count', 1),
            MetricObject('http_200.profile.GET.upstreamTime.mean', 406.0, 'ms'),
            MetricObject('http_200.profile.GET.upstreamTime.median', 406.0, 'ms'),
            MetricObject('http_200.profile.GET.upstreamTime.90th_percentile', 406.0, 'ms'),
            MetricObject('http_200.profile.GET.responseTime.count', 1),
            MetricObject('http_200.profile.GET.responseTime.mean', 406.0, 'ms'),
            MetricObject('http_200.profile.GET.responseTime.median', 406.0, 'ms'),
            MetricObject('http_200.profile.GET.responseTime.90th_percentile', 406.0, 'ms'),
            MetricObject('http_200.unknown.GET.responseTime.count', 1),
            MetricObject('http_200.unknown.GET.responseTime.mean', 413.0, 'ms'),
            MetricObject('http_200.unknown.GET.responseTime.median', 413.0, 'ms'),
            MetricObject('http_200.unknown.GET.responseTime.90th_percentile', 413.0, 'ms'),
        ]

        outputMetrics = p.get_state(1)

        # validate number of metrics
        self.assertEqual(len(expected), len(outputMetrics))

        # compare all metrics objects
        for i in range(0, len(expected)-1):
            self.assertEqual(expected[i].name, outputMetrics[i].name)
            self.assertEqual(expected[i].value, outputMetrics[i].value)
            self.assertEqual(expected[i].units, outputMetrics[i].units)

    def test_parse_line(self):
        samples = [
            {
                'input': '{ "timestamp": "2014-10-10T06:30:32+00:00", "request": { "remote_addr": "192.168.56.1", "request": "GET /login HTTP/1.1", "status": "200", "request_time": "0.406", "upstream_response_time": "0.406" } }',
                'output': {'http_200.login.GET.upstreamTime': {'values': [406.0], 'unit': 'ms'}, 'http_200.login.GET.responseTime': {'values': [406.0], 'unit': 'ms'}},
            },
            {
                'input': '{ "timestamp": "2014-10-10T06:30:36+00:00", "request": { "remote_addr": "192.168.56.1", "request": "GET /profile HTTP/1.1", "status": "200", "request_time": "0.413", "upstream_response_time": "0.413" } }',
                'output': {'http_200.unknown.GET.upstreamTime': {'values': [413.0], 'unit': 'ms'}, 'http_200.unknown.GET.responseTime': {'values': [413.0], 'unit': 'ms'}},
            },
            {
                'input': '{ "timestamp": "2014-10-10T06:30:36+00:00", "request": { "remote_addr": "192.168.56.1", "request": "GET /logout HTTP/1.1", "status": "499", "request_time": "0.404", "upstream_response_time": "-" } }',
                'output': {'http_499.logout.GET.responseTime': {'values': [404.0], 'unit': 'ms'}},
            }
        ]

        for sample in samples:
            # init parser
            p = PerformanceLogster()

            # stub path_regs
            p.path_regs = (
                ('login', re.compile('^/login.*')),
                ('logout', re.compile('^/logout.*')),
            )

            # parse the line
            p.parse_line(sample['input'])

            # times should match
            self.assertEqual(p.times, sample['output'])

    def test_sanitize_request_method(self):
        samples = [
            ['GET', 'get'],
            ['POST', 'POST'],
            ['DELETE', 'DELETE'],
            ['invalid', 'WGET'],
            ['invalid', 'WWWWWWWWPOST'],
            ['invalid', 'ONETOUCH']
        ]

        p = PerformanceLogster()

        for sample in samples:
            self.assertEqual(sample[0], p.sanitize_request_method(sample[1]))
