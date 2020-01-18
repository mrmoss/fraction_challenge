#!/usr/bin/env python3

def evalulate_line(line):
	return 'fail'

def unit_tests():
	tests=[('1/2 * 3_3/4','1_7/8'),
		('2_3/8 + 9/8','3_1/2')]

	for test,answer in tests:
		print('Testing "%s" == "%s"'%(test,answer))

		calculated=evalulate_line(test)

		if calculated==answer:
			print('\t PASS')
		else:
			print('\t FAIL (GOT "%s")'%calculated)

if __name__=='__main__':
	try:
		unit_tests()
	except KeyboardInterrupt:
		exit(-1)
