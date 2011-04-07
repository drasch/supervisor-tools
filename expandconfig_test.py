#!/usr/bin/env python2.7


import expandconfig
import unittest
import ConfigParser
import io
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
		input_expected = """
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
		config_expected = self.load_config(input_expected)

		config_new = self.expander.expand(config)
		self.compare_configs(config_expected, config_new)

	def test_one_expansion(self):
		input_data = """
[sectiona]
queue=a;b
settingb=stuff
settingc=stuff
		"""
		input_expected = """
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
		config_expected = self.load_config(input_expected)

		config_new = self.expander.expand(config)

		self.compare_configs(config_expected, config_new)


	def compare_configs(self, configa, configb):
		sectionsa = sorted(configa.sections())
		sectionsb = sorted(configb.sections())
		self.assertEqual(sectionsa, sectionsb)

		for s in configa.sections():
			optionsa = sorted(configa.options(s))
			optionsb = sorted(configb.options(s))
			self.assertEqual(optionsa, optionsb)

	def load_config(config_text):
		config = ConfigParser.RawConfigParser(allow_no_value=True)
		config.readfp(io.BytesIO(config_text))
		return config

	load_config = staticmethod(load_config)


if __name__ == '__main__':
	unittest.main()
