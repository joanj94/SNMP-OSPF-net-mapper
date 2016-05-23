 # -*- coding: utf-8 -*-

import argparse
import netsnmp

if __name__ == '__main__':
	parser = argparse.ArgumentParser(
		formatter_class=argparse.ArgumentDefaultsHelpFormatter,
		description='OSPF net mapper based in SNMP')
	parser.add_argument('-t', '--target', required=True, default='localhost', help='Target IP')
	parser.add_argument('-c', '--community', required=True, default='public', help='Community name')

	args = parser.parse_args()
	if args.target:
	    t = args.target
	if args.community:
	    c = args.community
	#end parse
