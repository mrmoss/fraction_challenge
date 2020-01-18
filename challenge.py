#!/usr/bin/env python3
import re

def parse_fraction(lexeme):
	'''
	'''
	exprs=['[-]?[\d]+[_][-]?[\d]+[/][-]?[\d]+','[-]?[\d]+[/][-]?[\d]+','[-]?[\d]+']

	for expr in exprs:
		if re.findall(expr,lexeme):
			parts=[int(num) for num in re.findall(exprs[-1],lexeme)]
			while len(parts)<3:
				parts=[0]+parts
			return parts

	return None

def evaluate_line(line):
	'''
	'''
	valid_ops='+-*/'

	lexemes=line.strip().split()
	for lexeme in lexemes:

		if len(lexeme)==1 and lexeme in valid_ops:
			next_op=lexeme
			continue

		fraction=parse_fraction(lexeme)

		if fraction is not None:
			whole,num,top=fraction
			print(whole,num,top)
			continue

		raise Exception('Unexpected token "%s"'%lexeme)

	return 'fail'

def unit_tests():
	'''
	'''
	tests=[('1/2 * 3_3/4','1_7/8'),
		('2_3/8 + 9/8','3_1/2')]

	for test,answer in tests:
		print('Testing "%s" == "%s"'%(test,answer))

		calculated=evaluate_line(test)

		if calculated==answer:
			print('\t PASS')
		else:
			print('\t FAIL (GOT "%s")'%calculated)

		print('')

if __name__=='__main__':
	try:
		unit_tests()
	except KeyboardInterrupt:
		exit(-1)
