#!/usr/bin/env python


import expandconfig
import unittest
import ConfigParser
import StringIO
import sys

class TestExpandConfig(unittest.TestCase):
	def setUp(self):
		self.expander = expandconfig.ConfigExpander()


	def test_noexpansions_stays_intact(self):
		input_data = """
[sectiona]
settinga=stuff
settingb=stuff
settingc=stuff

[sectionb]
settingc=stuff
settingd=stuff
		"""

		config_expected = self.load_config(input_data)
		config_new = self.expander.expand(config_expected)

		self.compare_configs(config_expected, config_new)

	def test_both_expansions(self):
		input_data = """
[sectiona]
queue=a;b
engine=1
settingb=stuff
settingc=stuff
		"""
		output_expected = """
[sectiona-a-1]
queue=a
engine=1
settingb=stuff
settingc=stuff

[sectiona-b-1]
engine=1
queue=b
settingb=stuff
settingc=stuff
		"""

		config = self.load_config(input_data)
		config_expected = self.load_config(output_expected)

		config_new = self.expander.expand(config)
		self.compare_configs(config_expected, config_new)

	def test_one_expansion(self):
		input_data = """
[sectiona]
queue=a;b
settingb=stuff
settingc=stuff
		"""
		output_expected = """
[sectiona-a]
queue=a
settingb=stuff
settingc=stuff

[sectiona-b]
queue=b
settingb=stuff
settingc=stuff
		"""

		config = self.load_config(input_data)
		config_expected = self.load_config(output_expected)

		config_new = self.expander.expand(config)

		self.compare_configs(config_expected, config_new)

	def test_two_expansions(self):
		input_data = """
[sectiona]
queue=a;b
engine=1..2
settingb=stuff
settingc=stuff
		"""
		output_expected = """
[sectiona-a-1]
queue=a
engine=1
settingb=stuff
settingc=stuff

[sectiona-a-2]
queue=a
engine=2
settingb=stuff
settingc=stuff

[sectiona-b-1]
queue=b
engine=1
settingb=stuff
settingc=stuff

[sectiona-b-2]
queue=b
engine=2
settingb=stuff
settingc=stuff
		"""

		config = self.load_config(input_data)
		config_expected = self.load_config(output_expected)

		config_new = self.expander.expand(config)

		self.compare_configs(config_expected, config_new)

	def test_group_expander(self):
		input_data = """
[program:sectiona]
queue=a;b
engine=1..2
settingb=stuff
settingc=stuff
		"""

		config = self.load_config(input_data)

		group_expander = expandconfig.ConfigExpanderWithGroup()
		config_new = group_expander.expand(config)

		programs = config_new.get("group:sectiona", "programs")
		self.assertEqual("sectiona-a-1,sectiona-a-2,sectiona-b-1,sectiona-b-2", programs)


	def compare_configs(self, configa, configb):
		sectionsa = sorted(configa.sections())
		sectionsb = sorted(configb.sections())
		self.assertEqual(sectionsa, sectionsb)

		for s in configa.sections():
			optionsa = sorted(configa.options(s))
			optionsb = sorted(configb.options(s))
			self.assertEqual(optionsa, optionsb)

	def load_config(config_text):
		config = ConfigParser.RawConfigParser()
		config.readfp(StringIO.StringIO(config_text))
		return config

	load_config = staticmethod(load_config)


if __name__ == '__main__':
	unittest.main()
