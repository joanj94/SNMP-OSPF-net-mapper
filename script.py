 # -*- coding: utf-8 -*-

import argparse
import netsnmp
import util

class router:
	def __init__(self, name = None, interfaces = None):
		self.name = name
		self.interfaces = interfaces
	#end of init


	def __str__(self):
		s =  "Router "+self.name+" Info:\n    Interfaces: \n" 
		for x in self.interfaces:
			s = s+x.__str__()
		return s
#end of router class


class interface:
	def __init__(self, speed=None, ip=None, mask = None, desc = None):
		self.speed = speed
		self.ip = ip
		self.mask = mask
		self.desc = desc
	#end of init

	def __str__(self):
		return "        --------------------------------\n        Interface - "+self.desc+":\n        IP = "+self.ip+"\n        Mask = "+self.mask+"\n        Speed = "+self.speed+" b/s\n        --------------------------------\n"
	#end of print
#end of interface class


def get_interfaces(ip):
	res = netsnmp.snmpwalk(netsnmp.Varbind('ipAdEntAddr'), Version = 2, DestHost = ip, Community=c)#snmpwalk -v 2c -c c t ipAddEntAddr
	interfaces = []
	for i_ip in res:
		ifNum = netsnmp.snmpget(netsnmp.Varbind('ipAdEntIfIndex.'+i_ip), Version = 2, DestHost = ip, Community=c)[0] #snmpget -v 2c -c c t ipAddEntIfIndex.i_ip

		operStatusResult = netsnmp.snmpget(netsnmp.Varbind('ifOperStatus.'+ifNum), Version = 2, DestHost = ip, Community=c) #snmpget -v 2c -c c t ifOperStatus.ifNum
		typeResult = netsnmp.snmpget(netsnmp.Varbind('ifType.'+ifNum), Version = 2, DestHost = ip, Community=c) #snmpget -v 2c -c c t ifType.+ifNum	

		if typeResult[0] == '6' and operStatusResult[0] == '1':
			speed = netsnmp.snmpget(netsnmp.Varbind('ifSpeed.'+ifNum), Version = 2, DestHost = ip, Community=c) #snmpget -v 2c -c c t ifSpeed.ifNum
			mask = netsnmp.snmpget(netsnmp.Varbind('ipAdEntNetMask.'+i_ip), Version = 2, DestHost = ip, Community=c) #snmpget -v 2c -c c t ipAddEntNetMask.i_ip
			desc = netsnmp.snmpget(netsnmp.Varbind('ifDescr.'+ifNum), Version = 2, DestHost = ip, Community=c) #snmpget -v 2c -c c t ifDescr.ifNum
			interfaces.append(interface(speed = speed[0], ip = i_ip, mask = mask[0], desc=desc[0]))
		#no loopback and active ones
	#search for all active ethernet interfaces
	return interfaces
#end of get interfaces


def get_router_info(ip):
	r_name = netsnmp.snmpwalk(netsnmp.Varbind('sysName'), Version = 2, DestHost = ip, Community=c)#snmpwalk -v 2c -c c t sysName
	if r_name:
		return router(name=r_name[0], interfaces=get_interfaces(ip))
#end of get router info


def get_unique_ips(r):
	temp = set()
	for x in r.interfaces:
		for i in netsnmp.snmpwalk(netsnmp.Varbind('ospfLsdbLsid'), Version = 2, DestHost = x.ip, Community=c):
 			temp.add(i)
	#get all the first ips without repeats
	return temp


def get_all_routers_from_one(r):
	ips = util.Stack()
	visited_r = set()
	visited_ip = set()
	result = [r]
	visited_r.add(r.name) #add the start ip to prevent rediscover the same router

	for x in get_unique_ips(r):
		ips.push(x)
	#add the ips

	while not ips.isEmpty():
		ip = ips.pop()
		if ip not in visited_ip:
			visited_ip.add(ip)
			r_router = get_router_info(ip)
			if r_router:				
				if r_router.name not in visited_r:
					result.append(r_router)
					visited_r.add(r_router.name)
					for x in get_unique_ips(r_router):
						ips.push(x)
					#add the new ips
				#if it's a new router
			#if router is founded
		#make sure we don't repeat ips
	#Search all ips	
	return result
#end of get all info of the routers


if __name__ == '__main__':
	parser = argparse.ArgumentParser(
		formatter_class=argparse.ArgumentDefaultsHelpFormatter,
		description='OSPF net mapper based in SNMP')
	parser.add_argument('-t', '--target', required=True, help='Target IP')
	parser.add_argument('-c', '--community', required=True, help='Community name')

	args = parser.parse_args()
	if args.target:
	    t = args.target
	if args.community:
	    c = args.community
	#end parse

	r = get_router_info(t)
	r2 = get_all_routers_from_one(r)
	for x in r2:
		print x
#end of main
	