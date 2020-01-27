#!/usr/bin/python3
import gzip

badSigns = ['php', 'chmod', 'wget', '/shell', 'admin', 'mysql']
logs = [open('/var/log/apache2/access.log', 'rt'), open('/var/log/apache2/access.log.1', 'rt')]
logLines = []
badIPs = set()

i = 2
while i:
    try:
        logs.append(gzip.open('/var/log/apache2/access.log.{}.gz'.format(i), 'rt'))
        i += 1
    except FileNotFoundError:
        i = False

for log in logs:
    logLines.extend([line for line in log])

print('retrieved {} from {} files'.format(len(logLines), len(logs)))

for line in logLines:
    line = line.lower()
    for sign in badSigns:
        if sign in line:
            badIPs.add('Require not ip ' + line.split()[0])
            continue

for f in logs: f.close()

print('found {} bad IPs'.format(len(badIPs)))

with open('/etc/apache2/conf-available/bad-hacker-ips.conf', 'wt') as f:
    f.write('\n'.join(badIPs))