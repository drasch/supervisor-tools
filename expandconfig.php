#!/usr/bin/php5
#<?php
class IniProcessor {
	protected $mapping = array(
		"expand" => array("engine")
		"replace" => array("command"),
		"remove" => array("engines", "type", "queue" )
	);

	protected $data;

	public function __construct($filename) {
		$this->data = parse_ini_file($filename, true);
	}

	public function expand() {
		$newdata = array();
		foreach ($this->data as $section_name => $section) {
			$expanded_fields = array();
			foreach($this->mapping['expand'] as $expand) {
				$expanded_field = $this->parseExpand($section[$expand]);
				if ($expanded_field === false) {
					throw new Exception("Error expanding field on section: $section_name field: $expand");
				}
				$expanded_fields[$expand] = $expanded_field;
			}
			
			$expanded_sections = $this->crossProduct($expanded_fields);
			foreach ($expanded_sections as $key =>$newsection) {
				$newsectiondata = $section;
				foreach($newsection as $field=>$value) {
					$newsectiondata[$field] = $value;
				}
				$newvalues["$section_name-". $key] = $newsectiondata;
			} 
		}	
		$this->data = $newvalues;
	}

	public function replace() {
		foreach ($this->data as $section_name => $section) {
			foreach($this->mapping['replace'] as $replace) {
				if ($section[$replace]) {
					if (preg_match_all('|\%(\w+)\%|', $section[$replace], $matches)) {
						$replacements = array();
						foreach ($matches[0] as $i =>$match) {
							$replacements[$match] = $section[$matches[1][$i]];
						}
						$this->data[$section_name][$replace] = strtr($section[$replace], $replacements);
					}
				}
			}
		}
	}
	public function remove() {
		foreach ($this->data as $section_name => $section) {
			foreach($this->mapping['remove'] as $remove) {
				if ($section[$remove]) {
					unset($this->data[$section_name][$remove]);
				}
			}
		}
	}
	protected function parseExpand($string) {
		$expanded = array($string);

		// a..b -> an entry for each integer between a and b inclusive
		if (preg_match("/^(\d+)\.\.(\d+)$/", $string, $matches)) {
			if ($matches[1] <= $matches[2]) {
				$expanded = range($matches[1], $matches[2]);
			}
		}
		// a;b -> an entry for an and an entry for b
		elseif (strpos($string,";") !== false) { 
			$expanded = explode(";", $string);
		}
		return $expanded;
	}

	public function crossProduct($inputs) {
		$output = array();
		list($name,$avalues) = each($inputs);
		$count = 1;
		foreach ($inputs as $input) {
			$count *= count($input);	
		}

		for ($i=0; $i<$count; $i++) {
			$denominator = $count;
			$numerator = $i;
			$key = array();
			$tuple = array();
			foreach ($inputs as $name => $input) {
				$denominator /= floor(count($input));
				$tuple[$name] = $input[floor($numerator / $denominator)];
				$key[] = $name;
				$key[] = $tuple[$name];
				$numerator %= $denominator;
			}
			$output[implode("-",$key)] = $tuple;
		}
		return $output;
	}

	public function dump() {
		foreach($this->data as $section_name=>$section) {
			print("[$section_name]\n");
			foreach ($section as $field=>$value) {
				print("$field=\"$value\"\n");
			}
		}
	}
}
										
if ($argc != 1) {
	echo "usage: expandconfig.php <input.ini>";
}

$ini = new IniProcessor($argv[1]);
$ini->expand();
$ini->replace();
$ini->remove();
$ini->dump();
