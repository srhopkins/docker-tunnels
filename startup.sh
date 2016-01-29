#!/bin/sh

# Copy all user defined hosts into dnsmasq hosts directory /etc/hosts.d
if [ -d /hosts ]; then
	cp /hosts/* /etc/hosts.d
fi

# Generate and run user tunnels/gateways/jumps
if [ -d /tunnels ]; then
	/opt/docker_tunnels.py
	chmod +x /tunnels/*.sh
	for script in /tunnels/*.sh; do
		$script
	done
fi

if [ -d /hosts -o -d /tunnels ]; then
	/etc/init.d/dnsmasq start
	resolv=$(egrep '(^nameserver|^search)' /etc/resolv.conf)
        echo -e "nameserver 127.0.0.1\n$resolv" > /etc/resolv.conf
fi

if [ -f /deployment/init.sh ];
then
	echo "Running custom init script"
	chmod +x /deployment/init.sh
	/deployment/init.sh
fi

# Run bash to keep container running and provide interactive
# mode if not using custom init.sh script.
bash
