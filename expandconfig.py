#!/usr/bin/env python2.7

import ConfigParser
import io,sys
import re
import itertools

sample_config = """
[stuff]
engine=1..4
queue=admin;small;large;medium
command=%(queue)s %(engine)s
"""


def parse_expand(value):
	"""Expand text in a field to a set of items

	This accepts the following patterns:
	>>> parse_expand("3..5")
	[3, 4, 5]
	>>> parse_expand("a;b;c")
	['a', 'b', 'c']
	>>> parse_expand("leaveintact")
	['leaveintact']
	"""

	expanded = [value]
	match = re.match(r'^(\d+)\.\.(\d+)$', value)
	if (match):
		expanded = range(int(match.group(1)), int(match.group(2))+1)
	elif (value.find(';')>=0):
		expanded = value.split(';')
	return expanded


def expand(config):
	config_out = ConfigParser.ConfigParser(allow_no_value=True)
	expand_fields = ['queue', 'engine']
	for i in config.sections():
		expansions = []
		print "section", i
		for f in expand_fields:
			expanded_field = parse_expand(config.get(i,f))
			expansions.append(expanded_field)

		for f in itertools.product(*expansions):
			new_section_name="%s-%s" % (i,"-".join(map(str,f)))
			config_out.add_section(new_section_name)
			values = dict(config.items(i))
			values.update(zip(expand_fields, f))
			print values
			for k,v in values.items():
				config_out.set(new_section_name,k,v)
	return config_out


config = ConfigParser.RawConfigParser(allow_no_value=True)
config.readfp(io.BytesIO(sample_config))

config.get("stuff", "command")

config_new = expand(config)
config_new.write(sys.stdout)


