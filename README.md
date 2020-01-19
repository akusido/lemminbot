# Run Book / System Operation Manual
!(https://img.shields.io/pypi/pyversions/requests?style=for-the-badge) ![serious-business](https://img.shields.io/badge/nope-red?logo=stackexchange&style=for-the-badge)

## System overview

**lemminbot:** This script does weird stuff with irrelevant data

### Business overview

Captures (_collects_) images for the purposes of timelapse photography.

### Technical overview

Python script designed to run on a schedule, utilizing [requests](https://pypi.org/project/requests/) on py3.4 and above to contact external API and parse the URI for the image.

### Service Level Agreements (SLAs)

Best-effort.
> Third parties may have their own SLAs for components of this system.

### Service owner

Turun teknologiakiinteistöt
nvf.io

### Contributing applications, daemons, services, middleware

[Django REST Framework](https://www.django-rest-framework.org/) for the Web API
AWS S3 for hosting the images, generating thumbnails etc.
Alpine Linux providing python running in the container for this service

## System characteristics

### Hours of operation

24 hours per day, 7 days per week, except when it doesn't.

#### Hours of operation - core features

API, AWS and service running continuously.

#### Hours of operation - secondary features

Daylight preferred, but at least 04:00-13:00 UTC (60 frames)

### Data and processing flows

Scheduled task runs `python lemminbot.py` at boot and every ~10 minutes after. The script parses JSON it expects to get from the Web API to check what the current timestamp/filename is - and if that does not exist on disk, parses the path to download it.

### Infrastructure and network design

Virtual machine (256MB RAM, 20GB disk) with no open ports and only self-initiated outbound connections. IPv4 NAT preferred for routing.

### Fault Tolerance and High Availability

Single point of failure.
If the API endpoint is dead or returns malformed data, no images can be retrieved.
If the container running the service develops a fault (such as disk full), no automated recovery is available.

### Throttling and partial shutdown

The script will not attempt to download new images if `dest_filename.temp_suffix` is found. You can pre-populate the path with such files by `touch`ing the corresponding timestamp before the script runs.

### Expected traffic and load

On a slow single-core shared-fs system, it takes from 20 up to 45 seconds before the script finishes parsing the responses of each endpoint. Successful requests consume roughly 6MB of bandwidth from AWS.

### Environmental differences

Storing the downloaded frames in /tmp is not a good idea if the machine running the script is ephemeral. Do **rsync** the files regularly, preferably after 00:00 UTC to capture a folder cleanly.

### Tools

The _transfer.sh_ script can be modified to your needs.

## Required resources

> What compute, storage, database, metrics, logging, and scaling resources are needed? What are the minimum and expected maximum sizes (in CPU cores, RAM, GB disk space, GBit/sec, etc.)?

### Required compute resources

Local: _enough to finish running the script in under 10 minutes_
Remote: t1.micro for the API and thumbnailer?

### Required storage resources

around 700MB per 'APIURL[site]' per 24 hours.
Currently consuming over 500GB per year.

### Required bandwidth & other

Enough bandwidth to finish downloading before timeout; 256kbps is enough?
If using rsync over TCP/IP, roughly double the amount of storage in data transfers. Otherwise just the ingress bandwidth.

## System configuration

### Configuration management

Configured once, documented lazily. This is me trying to fix that.

### Security, secrets and access control

Public API endpoints, accessible without authentication on the internet.
This script open source. 'transfer.sh' contains path to secrets.
_unattended-upgrades_ keeps the underlying operating system up-to-date.

### Backup requirements

Enough storage to replicate the archive (4TB+).
sha256sum and rsync are your friends.

### Backup procedures

> sync; /env/bin/bash transfer.sh

## Monitoring and alerting

[netdata](netdata.cloud), except not really anymore.

### Log message format

STDOUT, `print("/tmp/timestamp.iowait => /media/frames/...")`

### Events and error messages

Not saved non-interactively. Scheduler reports process start times.

### Metrics

python3 startup requires moderate amounts of CPU and RAM.
Scheduled to run once every 10 minutes with average execution time of 60s.

### Health checks

The status of the container is not monitored, or if it is, the alerts are not looked at very often.
The Web API is unmanaged and AWS S3 runs on the free tier.

## Operational tasks

### Deployment

> git clone `whatever`; vagrant up

#### Postprocess frames into thumbnails with `jpegtran`:

```PowerShell
SET exe="\\path\to\cjpeg\or\mozjpeg"

forfiles *.jpg /C "%exe% -crop "WxHf+X+Y" -outfile '%~ni.thumb.jpg' '%~i'"
```

#### Stack processed frames into quads and produce a timelapse with `ffmpeg`

```shell
cd "//frames/first" && ffmpeg -i "%4d.thumb.jpg" -c copy "../topleft.mpeg"
cd "//frames/second" && ffmpeg -i "%4d.thumb.jpg" -c copy "../topright.mpeg"
cd "//frames/third" && ffmpeg -i "%4d.thumb.jpg" -c copy "../botleft.mpeg"
cd "//frames/fourth" && ffmpeg -i "%4d.thumb.jpg" -c copy "../botright.mpeg"

ffmpeg -i topleft.mpeg -i botleft.mpeg -i topright.mpeg -i botright.mpeg -i sidebar.mp4 -filter_complex \
"[0][1]vstack[lefthalf];[2][3]vstack[righthalf];[lefthalf][righthalf][4]hstack=inputs=3[v]" \
-map "[v]" -c:v libx264 %custom_encoding_parameters% output_timelapse.mp4
```

### Routine tasks and sanity checks

Browse through the logs and alerts, maybe cleanup /tmp.
Look at the images in storage/archive.

### Troubleshooting

Run the script interactively, see what happens.
Visit APIURL in a browser. Does DNS still work? (_it's always DNS_...)

#### Daylight-saving time changes

The downloaded data should stick to RFC3339, but origin may handle it differently. ***Postprocessing may be required.***

### Failover and Recovery

LOL, this is a hobby project, nothing is redundant and data loss is permanent. If the data is really important to you, ask the service owner for a copy?

> EOF, thank you for reading me

Templates ![CC BY-SA 4.0](https://licensebuttons.net/l/by-sa/3.0/88x31.png) Skelton Thatcher Consulting and contributors
