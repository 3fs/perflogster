# perf-logster

Custom parser module for [logster](https://github.com/etsy/logster) used to collect and process performance data.

## Requirements

### Nginx

Nginx needs to be set up with:

```
log_format perf_json '{"timestamp": "$time_iso8601", '
                      '"request": {'
                      '"remote_addr": "$remote_addr", '
                      '"request": "$request", '
                      '"status": "$status", '
                      '"request_time": "$request_time", '
                      '"upstream_response_time": "$upstream_response_time"}}';

# add following inside a specific server configuration block
access_log /var/log/$hostname-performance.log perf_json;
```

### Logster

[Logster](https://github.com/etsy/logster) needs to be installed on the server.

## Running it

Logster needs to be called with our custom module:

```
./logster PerformanceLogster /var/log/app.com-performance.log --parser-options '--percentiles 25,75,90 --mapping=/path/to/my.map'
```

Parser supports following options:

- `percentiles` Comma-separated list of integer percentiles to track: (default: "90")
- `mapping` Path to a mapping file

## Mapping file

The mapping file is a list of pairs composed of a label and a regular expression.

Example:

```
archive ^/news/archive/.*
news    ^/news.*
profile ^/profile.*
```

Mind that the order of elements in the list is important as the first match will be used.

If the path can't be matched to any of the listed expressions a label `unknown` will be used. This can be renamed by adding `my label .*` to the end of the list.

## Example

Given that we use the following map:

```
news    ^/news/.*
profile ^/profile/.*
```

And that logster picks up new log entries:

```
{"timestamp": "2015-05-21T06:30:32+00:00", "request": {"remote_addr": "192.168.56.1", "request": "GET /profile/me HTTP/1.1", "status": "200", "request_time": "0.036", "upstream_response_time": "0.046"}}
{"timestamp": "2015-05-21T06:30:34+00:00", "request": {"remote_addr": "192.168.56.1", "request": "GET /profile HTTP/1.1", "status": "200", "request_time": "0.041", "upstream_response_time": "0.041"}}
{"timestamp": "2015-05-21T06:30:36+00:00", "request": {"remote_addr": "192.168.56.1", "request": "GET /logout HTTP/1.1", "status": "200", "request_time": "0.023", "upstream_response_time": "0.024"}}
```

Following metrics would be generated:

```
1432129111 http_200.unknown.GET.upstreamTime.count 0.105263157895
1432129111 http_200.unknown.GET.upstreamTime.mean 32.0
1432129111 http_200.unknown.GET.upstreamTime.median 32.0
1432129111 http_200.unknown.GET.upstreamTime.90th_percentile 39.2
1432129111 http_200.unknown.GET.responseTime.count 0.105263157895
1432129111 http_200.unknown.GET.responseTime.mean 32.0
1432129111 http_200.unknown.GET.responseTime.median 32.0
1432129111 http_200.unknown.GET.responseTime.90th_percentile 39.2
1432129111 http_200.profile.GET.upstreamTime.count 0.0526315789474
1432129111 http_200.profile.GET.upstreamTime.mean 36.0
1432129111 http_200.profile.GET.upstreamTime.median 36.0
1432129111 http_200.profile.GET.upstreamTime.90th_percentile 36.0
1432129111 http_200.profile.GET.responseTime.count 0.0526315789474
1432129111 http_200.profile.GET.responseTime.mean 36.0
1432129111 http_200.profile.GET.responseTime.median 36.0
1432129111 http_200.profile.GET.responseTime.90th_percentile 36.0
```

## Developing

```
git clone git@github.com:3fs/perf-logster.git
cd perf-logster
make dev
make qa
```
