#!/usr/bin/env python

import ConfigParser
import sys
import re
import itertools
import StringIO

# for python 2.5 compatibility
# http://docs.python.org/library/itertools.html#itertools.product
def product(*args, **kwds):
    # product('ABCD', 'xy') --> Ax Ay Bx By Cx Cy Dx Dy
    # product(range(2), repeat=3) --> 000 001 010 011 100 101 110 111
    pools = map(tuple, args) * kwds.get('repeat', 1)
    result = [[]]
    for pool in pools:
        result = [x+[y] for x in result for y in pool]
    for prod in result:
        yield tuple(prod)


sample_config = """
[program:stuff]
engine=1..4
queue=admin;small;large;medium
command=%(queue)s %(engine)s
"""

class ConfigExpander:
	def parse_expand(self, value):
		"""Expand text in a field to a set of items

		This accepts the following patterns:
		>>> parser = ConfigExpander()
		>>> parser.parse_expand("3..5")
		[3, 4, 5]
		>>> parser.parse_expand("a;b;c")
		['a', 'b', 'c']
		>>> parser.parse_expand("leaveintact")
		['leaveintact']
		"""

		expanded = [value]
		match = re.match(r'^(\d+)\.\.(\d+)$', value)
		if (match):
			expanded = range(int(match.group(1)), int(match.group(2))+1)
		elif (value.find(';')>=0):
			expanded = value.split(';')
		return expanded


	def expand(self, config):
		config_out = ConfigParser.ConfigParser()
		expand_fields = ['queue', 'engine']
		for i in config.sections():
			expanded_fields = []
			expansions = []
			for f in expand_fields:
				try:
					expanded_field_values = self.parse_expand(config.get(i,f))
					expanded_fields.append(f)
					expansions.append(expanded_field_values)
				except ConfigParser.NoOptionError:
					pass

			if expanded_fields == []: # no fields actually expanded, get into the loop below
				expansions = [[None]]

			expanded_section_names = []
			for f in product(*expansions):
				new_section_name=i

				if f != (None,):
					new_section_name="%s-%s" % (i,"-".join(map(str,f)))
					expanded_section_names.append(new_section_name)
				config_out.add_section(new_section_name)
				values = dict(config.items(i))
				if f != (None,):
					values.update(zip(expanded_fields, f))
				for k,v in values.items():
					config_out.set(new_section_name,k,v)
			self.register_group(i,expanded_section_names,config_out)
		return config_out
	def register_group(self, section_name, expanded_names, config_out):
		pass

class ConfigExpanderWithGroup(ConfigExpander):
	def register_group(self, section_name, expanded_names, config_out):
		strip = lambda s: s.split(":")[1]
		group_name = "group:"+strip(section_name)
		program_names = ','.join(map(strip, expanded_names))

		config_out.add_section(group_name)
		config_out.set(group_name,'programs',program_names)


if __name__ == '__main__':
	# read standard in
	config = ConfigParser.RawConfigParser()
	config.readfp(sys.stdin)
	#config.readfp(StringIO.StringIO(sample_config))

	# parse it for __expand__ section

	# output expanded
	expander = ConfigExpanderWithGroup()
	config_new = expander.expand(config)
	config_new.write(sys.stdout)

# code used for testing
if false:
	expander = ConfigExpanderWithGroup()
	config_new = expander.expand(config)
	config_new.write(middleBuffer)

	readBuffer = StringIO.StringIO(middleBuffer.getvalue())
	config = ConfigParser.ConfigParser()
	config.readfp(readBuffer)
	for i in config.sections():
			try:
					print config.get(i,"command")
			except ConfigParser.NoOptionError:
					pass
	config.write(sys.stdout)


# TODO
# make loop prettier
# add command-line parameter for expand fields
# handle expand section dynamically
