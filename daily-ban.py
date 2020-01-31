import subprocess as subp
badSigns = ['php', 'chmod', 'wget', '/shell', 'admin', 'mysql']
bannedIPs = set()

with open('/var/log/apache2/access.log') as f:
    for line in f:
        for sign in badSigns:
            if sign in line:
                bannedIPs.add(line.split()[0])

for IP in bannedIPs:
    subp.run(['iptables', '-A', 'INPUT', '-s', IP, '-j', 'DROP'], capture_output=True)
    print('Banned IP', IP)
