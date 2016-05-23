 # -*- coding: utf-8 -*-

import argparse
import netsnmp

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
	def __init__(self, speed=None, ip=None, mask = None):
		self.speed = speed
		self.ip = ip
		self.mask = mask
	#end of init

	def __str__(self):
		return "        --------------------------------\n        Interface - "+self.ip+":\n        Speed = "+self.speed+"\n        Mask = "+self.mask+"\n        --------------------------------\n"
	#end of print
#end of interface class


def get_interfaces(ip):
	res = netsnmp.snmpwalk(netsnmp.Varbind('ipAdEntAddr'), Version = 2, DestHost = ip, Community=c)#snmpwalk -v 2c -c c t ipAddEntAddr
	interfaces = []
	for i_ip in res:
		ifNum = netsnmp.snmpget(netsnmp.Varbind('ipAdEntIfIndex.'+ip), Version = 2, DestHost = ip, Community=c)[0] #snmpget -v 2c -c c t ipAddEntIfIndex.ip

		operStatusResult = netsnmp.snmpget(netsnmp.Varbind('ifOperStatus.'+ifNum), Version = 2, DestHost = ip, Community=c) #snmpget -v 2c -c c t ifOperStatus.ifNum
		typeResult = netsnmp.snmpget(netsnmp.Varbind('ifType.'+ifNum), Version = 2, DestHost = ip, Community=c) #snmpget -v 2c -c c t ifType.+ifNum	

		if typeResult[0] == '6' and operStatusResult[0] == '1':
			speed = netsnmp.snmpget(netsnmp.Varbind('ifSpeed.'+ifNum), Version = 2, DestHost = ip, Community=c) #snmpget -v 2c -c c t ifSpeed.ifNum
			mask = netsnmp.snmpget(netsnmp.Varbind('ipAdEntNetMask.'+ip), Version = 2, DestHost = ip, Community=c) #snmpget -v 2c -c c t ipAddEntNetMask.ip
			interfaces.append(interface(speed = speed[0], ip = i_ip, mask = mask[0]))
		#no loopback and active one
	#search for all active ethernet interfaces
	return interfaces
#end of get interfaces


def get_router_info(ip):
	r_name = netsnmp.snmpwalk(netsnmp.Varbind('sysName'), Version = 2, DestHost = ip, Community=c)[0]#snmpwalk -v 2c -c c t sysName
	return router(name=r_name, interfaces=get_interfaces(ip))
#end of get router info


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
	print (r)
#end of main
	