#!/usr/bin/env python2.7

import ConfigParser
import io
import sys
import re
import itertools

sample_config = """
[stuff]
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
		config_out = ConfigParser.ConfigParser(allow_no_value=True)
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

			for f in itertools.product(*expansions):
				new_section_name=i

				if f != (None,):
					new_section_name="%s-%s" % (i,"-".join(map(str,f)))
				config_out.add_section(new_section_name)
				values = dict(config.items(i))
				if f != (None,):
					values.update(zip(expanded_fields, f))
				for k,v in values.items():
					config_out.set(new_section_name,k,v)
		return config_out

if __name__ == '__main__':
	# read standard in
	config = ConfigParser.RawConfigParser(allow_no_value=True)
	config.readfp(sys.stdin)

	# parse it for __expand__ section

	# output expanded
	expander = ConfigExpander()
	config_new = expander.expand(config)
	config_new.write(sys.stdout)


#	config = ConfigParser.RawConfigParser(allow_no_value=True)
#	config.readfp(io.BytesIO(sample_config))
#
#	config.get("stuff", "command")
#
#	expander = ConfigExpander()
#	config_new = expander.expand(config)
#	config_new.write(sys.stdout)



# TODO
# read standard in
# make loop prettier
# handle expand section dynamically
