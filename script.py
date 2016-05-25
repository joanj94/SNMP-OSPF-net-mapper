 # -*- coding: utf-8 -*-

import argparse
import netsnmp
import util
import itertools
from netaddr import *
import random
from graphviz import Digraph

ips_router = {}

class router:
	def __init__(self, name = None, interfaces = {}, route_table = {}, nbr = {}):
		self.name = name
		self.interfaces = interfaces
		self.route_table = route_table
		self.nbr = nbr
	#end of init


	def __str__(self):
		s =  "Router "+self.name+" Info:\n"
		s = s+"+++++++++++++++++++++++++++++++++++++++++++++++++++++\n"
		s = s+"    Interfaces: \n"
		for x in self.interfaces:
			s = s+self.interfaces[x].__str__()
		s = s+"    Route Table: \n"
		for x in self.route_table:
			s = s+self.route_table[x].__str__()
		s = s+"+++++++++++++++++++++++++++++++++++++++++++++++++++++\n"
		return s
	#end of print
#end of router class


class interface:
	def __init__(self, speed=None, ip=None, mask = None, desc = None):
		self.speed = speed +" b/s"
		self.ip = ip
		self.mask = mask
		self.desc = desc
	#end of init


	def __str__(self):
		return "        --------------------------------\n        Interface - "+self.desc+":\n        IP = "+self.ip+"\n        Mask = "+self.mask+"\n        Speed = "+self.speed+"\n        --------------------------------\n"
	#end of print
#end of interface class


class route:
	def __init__(self, network=None, mask=None, next_hop=None, type = None, proto = None):
		self.network = network
		self.mask = mask
		self.next_hop = next_hop
		self.type = type
		self.proto = proto
	#end of init


	def print_type(self):
		if self.type == '4':
			return "Indirect"
		elif self.type == '3':
			return "Direct"
		elif self.type == '2':
			return "Local"
		elif self.type == '1':
			return "Other"
	#end of getting the type of the route


	def print_proto(self):
		if self.proto == '1':
			return "Other"
		elif self.proto == '2':
			return "Local"
		elif self.proto == '3':
			return "Netmgmt"
		elif self.proto == '4':
			return "ICMP"
		elif self.proto == '5':
			return "EGP"
		elif self.proto == '6':
			return "GGP"
		elif self.proto == '7':
			return "HELLO"
		elif self.proto == '8':
			return "RIP"
		elif self.proto == '9':
			return "IS-IS"
		elif self.proto == '10':
			return "ES-IS"
		elif self.proto == '11':
			return "ciscoIgrp"
		elif self.proto == '12':
			return "bbnSpfIgp"
		elif self.proto == '13':
			return "OSPF"
		elif self.proto == '14':
			return "BGP"
	#end of getting the protocol of the route


	def __str__(self):
		return "        --------------------------------\n        Route - "+self.print_type()+" - "+self.print_proto()+":\n        Network = "+self.network+"\n        Mask = "+self.mask+"\n        Mext Hop = "+self.next_hop+"\n        --------------------------------\n"
	#end of print
#end of route class


class traceroute:
	def __init__(self, o_r=None, d_r=None, o_ip = None, d_ip = None, hops=[]):
		self.o_r = o_r
		self.d_r = d_r
		self.o_ip = o_ip
		self.d_ip = d_ip
		self.hops = hops
	#end of init


	def __str__(self):
		s = ""
		for x in self.hops:
			if x != self.o_r and x != self.d_r:
				s = s+x+"->"

		return "Traceroute: "+self.o_r+"/"+self.o_ip+"->"+s+self.d_r+"/"+self.d_ip+"\n"

#end of traceroute class


def get_interfaces(ip):
	res = netsnmp.snmpwalk(netsnmp.Varbind('ipAdEntAddr'), Version = 2, DestHost = ip, Community=c)#snmpwalk -v 2c -c c t ipAddEntAddr
	interfaces = {}
	for i_ip in res:
		ifNum = netsnmp.snmpget(netsnmp.Varbind('ipAdEntIfIndex.'+i_ip), Version = 2, DestHost = ip, Community=c)[0] #snmpget -v 2c -c c t ipAddEntIfIndex.i_ip

		operStatusResult = netsnmp.snmpget(netsnmp.Varbind('ifOperStatus.'+ifNum), Version = 2, DestHost = ip, Community=c) #snmpget -v 2c -c c t ifOperStatus.ifNum
		typeResult = netsnmp.snmpget(netsnmp.Varbind('ifType.'+ifNum), Version = 2, DestHost = ip, Community=c) #snmpget -v 2c -c c t ifType.+ifNum

		if typeResult[0] == '6' and operStatusResult[0] == '1':
			speed = netsnmp.snmpget(netsnmp.Varbind('ifSpeed.'+ifNum), Version = 2, DestHost = ip, Community=c) #snmpget -v 2c -c c t ifSpeed.ifNum
			mask = netsnmp.snmpget(netsnmp.Varbind('ipAdEntNetMask.'+i_ip), Version = 2, DestHost = ip, Community=c) #snmpget -v 2c -c c t ipAddEntNetMask.i_ip
			desc = netsnmp.snmpget(netsnmp.Varbind('ifDescr.'+ifNum), Version = 2, DestHost = ip, Community=c) #snmpget -v 2c -c c t ifDescr.ifNum
			interfaces[i_ip] = (interface(speed = speed[0], ip = i_ip, mask = mask[0], desc=desc[0]))
		#no loopback and active ones
	#search for all active ethernet interfaces
	return interfaces
#end of get interfaces


def make_route_table(ip):
	result = {}

	networks = netsnmp.snmpwalk(netsnmp.Varbind('ipRouteDest'), Version = 2, DestHost = ip, Community=c)#snmpwalk -v 2c -c c t ipRouteDest
	masks = netsnmp.snmpwalk(netsnmp.Varbind('ipRouteMask'), Version = 2, DestHost = ip, Community=c)#snmpmask -v 2c -c c t ipRouteMask
	next_hops = netsnmp.snmpwalk(netsnmp.Varbind('ipRouteNextHop'), Version = 2, DestHost = ip, Community=c)#snmpwalk -v 2c -c c t ipRouteNextHop
	types = netsnmp.snmpwalk(netsnmp.Varbind('ipRouteType'), Version = 2, DestHost = ip, Community=c)#snmpwalk -v 2c -c c t ipRouteType
	protos = netsnmp.snmpwalk(netsnmp.Varbind('ipRouteProto'), Version = 2, DestHost = ip, Community=c)#snmpwalk -v 2c -c c t ipRouteProto

	for x in xrange(len(networks)):
		result[networks[x]] = (route(network = networks[x], mask = masks[x], next_hop = next_hops[x], type = types[x], proto = protos[x]))

	return result
#end of make table from an ip


def get_router_info(ip):
	r_name = netsnmp.snmpwalk(netsnmp.Varbind('sysName'), Version = 2, DestHost = ip, Community=c)#snmpwalk -v 2c -c c t sysName
	ifs = get_interfaces(ip)
	for x in ifs:
		ips_router[ifs[x].ip] = r_name[0]
	#save the relation between ifs/ip and the router

	if r_name:
		return router(name=r_name[0], interfaces=ifs, route_table=make_route_table(ip))
#end of get router info


def get_unique_ips(r):
	ip = r.interfaces[random.choice(r.interfaces.keys())].ip #get any ip
	return netsnmp.snmpwalk(netsnmp.Varbind('ospfNbrIpAddr'), Version = 2, DestHost = ip, Community=c)
#end of get unique ips from router


def get_all_routers_from_one(r):
	ips = util.Stack()
	visited_r = set()
	visited_ip = set()
	result = {}
	result [r.name] = r
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
					result [r_router.name] = r_router
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


def mix_all_ips(routers):
	ips = []
	for r in routers:
		for i in routers[r].interfaces:
			ips.append((routers[r].interfaces[i].ip,r))
	#add all the ip interfaces of the router list
	return itertools.ifilter(lambda x: x[0][1] != x[1][1], itertools.permutations(ips,2)) #return the combination without same router in the pair
#end of mixing all ips of the routers


def get_interface_network(i):
	return (IPAddress(i.ip) & IPAddress(i.mask))
#end of getting the network for that Interface


def get_next_hop(x):
	next_hops = set()

	net = get_interface_network(routers[x[1][1]].interfaces[x[1][0]]) #get the network

	if net.__str__() in routers[x[0][1]].route_table:
		next_hop = routers[x[0][1]].route_table[net.__str__()].next_hop
	#if the router have the route defined
	else:
		next_hop = routers[x[0][1]].route_table['0.0.0.0'].next_hop
	#the router uses the default route

	next_router = ips_router[next_hop]
	next_hops.add(next_router)

	if next_router != ips_router[next_hop]:
		next_hops.add(get_next_hops([[(next_hop,next_router),(x[1][0],x[1][1])]]))
	#the next router is not the destination one, get the next hops

	return traceroute(o_r=x[0][1], d_r=x[1][1], o_ip=x[0][0], d_ip=x[1][0], hops=next_hops)
#end of getting the next hops


def get_next_hops(l):
	res = []
	for x in l:
		res.append(get_next_hop(x))
	#get all the hops
	return res
#end of getting the next hops function


def print_next_hops(ips_list):
	for x in get_next_hops(ips_list):
		print (x)
#end of printing the ips hops


def set_neighbours(r):
	temp = {}
	for x in get_unique_ips(r):
		temp[ips_router[x]] = x
	return temp
#end of setting the neighbours from one router


def set_all_nbr():
	for x in routers:
		routers[x].nbr = set_neighbours(routers[x])
#end of setting to all the roouters their neighbours


def print_routers_info():
	for x in routers:
		print routers[x]
#print routers information


def print_all_hops():
	for x in routers:
		print_next_hops(mix_all_ips(routers))
#end of printing all the hops between the ips


def generate_graph(path):
	dot = Digraph(comment='Network graph')
	for r in routers:
		dot.node(r,r)
	#add the nodes
	for r in routers:
		for nbr in routers[r].nbr:
			label = "Peer IP: "+routers[r].nbr[nbr]+"\nSpeed: "+routers[nbr].interfaces[routers[r].nbr[nbr]].speed
			dot.edge(r,nbr,label=label)
	#set the edges between the routers
	dot.render(path)
#end of generating a graph


if __name__ == '__main__':
	parser = argparse.ArgumentParser(
		formatter_class=argparse.ArgumentDefaultsHelpFormatter,
		description='OSPF network mapper based in SNMP')
	parser.add_argument('-t', '--target', required=True, help='Target IP')
	parser.add_argument('-c', '--community', required=True, help='Community name')
	parser.add_argument('-pi', '--print_ip', action='store_true', help='Print all hops in the possible combinations between the routers')
	parser.add_argument('-pg', '--print_graph', required=False, help='Print a graph with the name provided')

	args = parser.parse_args()
	if args.target:
	    t = args.target
	if args.community:
	    c = args.community
	#end obligatory ArgumentParser

	routers = get_all_routers_from_one(get_router_info(t)) #get all the routers
	print_routers_info()

	if args.print_ip:
		print_all_hops()
	if args.print_graph:
		set_all_nbr() #set all the neighbours
		generate_graph(args.print_graph)
	#end optional ArgumentParser

#end of main
