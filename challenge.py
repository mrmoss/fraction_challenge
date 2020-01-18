#!/usr/bin/env python3
import enum
import re

class State(enum.Enum):
	'''
	Enum for tracking the state machine for parsing lines.
	'''
	FIRSTNUMBER=0
	NUMBER=1
	OPERATOR=2

class Fraction:
	'''
	Basic fraction class.
	There is a Fraction class in the fraction module that would do what we want here...
	'''

	def __init__(self,whole,num,den):
		'''
		Takes a whole number, but only uses num and den internally.
		'''
		self._num=whole*den+num
		self._den=den

	def __add__(self,rhs):
		num=self._num*rhs._den+self._den*rhs._num
		den=self._den*rhs._den
		return Fraction(0,num,den)

	def __add__(self,rhs):
		num=self._num*rhs._den-self._den*rhs._num
		den=self._den*rhs._den
		return Fraction(0,num,den)

	def __mul__(self,rhs):
		num=self._num*rhs._num
		den=self._den*rhs._den
		return Fraction(0,num,den)

	def __div__(self,rhs):
		num=self._num*rhs._den
		den=self._den*rhs._num
		return Fraction(0,num,den)

	def __str__(self):
		return '%d_%d/%d'%(0,self._num,self._den)

def parse_number(lexeme):
	'''
	Parses a number that looks like (where w, n, and d are all ints (- sign is ok)):
		w_n/d
		n/d
		w
	Returns a 3-tuple (w,n,d) on success.
	Returns None of failure.
	'''

	#Attempt parsing via regex strings (ORDER OF THESE MATTER)
	exprs=['[-]?[\d]+[_][-]?[\d]+[/][-]?[\d]+','[-]?[\d]+[/][-]?[\d]+','[-]?[\d]+']
	for expr in exprs:

		if re.findall(expr,lexeme):

			#Parse all numbers and convert to integers
			parts=[int(num) for num in re.findall(exprs[-1],lexeme)]

			#Left pad with zeros
			while len(parts)<3:
				parts=[0]+parts

			#Success parse - return
			return parts

	#Nothing found - return None
	return None

def evaluate_line(line):
	'''
	Evaluates a single line of w_n/d fractional numbers with operators: +-*/
	Each w_n/d and operator will be separated by one or more spaces.
	'''
	answer=None
	next_op=None
	valid_ops='+-*/'
	state=State.FIRSTNUMBER

	#Parse line
	lexemes=line.strip().split()

	#Evaluate line
	for ind,lexeme in enumerate(lexemes):

		#Found an operator
		if len(lexeme)==1 and lexeme in valid_ops:

			#Wrong state - error
			if state!=State.OPERATOR:
				raise Exception('Unexpected operator "%s"'%lexeme)

			#Last lexeme is an operator - error
			if ind+1>=len(lexemes):
				raise Exception('Expected number after "%s"'%lexeme)

			#Set next op and change state
			state=State.NUMBER
			next_op=lexeme
			continue

		#Parse number
		number=parse_number(lexeme)

		#Found number
		if number is not None:

			#Wrong state - error
			if state not in [State.FIRSTNUMBER,State.NUMBER]:
				raise Exception('Unexpected number "%s"'%lexeme)

			#Parse 3 parts
			whole,num,den=number

			#First number - no evaluation
			if state==State.FIRSTNUMBER:
				answer=Fraction(whole,num,den)

			#Another number, evaluate operation
			else:

				#Run operator
				if next_op=='+':
					answer+=Fraction(whole,num,den)
				elif next_op=='-':
					answer-=Fraction(whole,num,den)
				elif next_op=='*':
					answer*=Fraction(whole,num,den)
				elif next_op=='/':
					answer/=Fraction(whole,num,den)
				else:
					raise Exception('Invalid operator "%s"'%next_op)

			#Change state
			state=State.OPERATOR
			continue

		raise Exception('Unexpected token "%s"'%lexeme)

	return answer

def unit_tests():
	'''
	Runs unit tests, returns nothing.
	'''
	tests=[('1/2 * 3_3/4','1_7/8'),
		('2_3/8 + 9/8','3_1/2'),
		('1','1'),
		('1/2','1/2'),
		('3_1/2','3_1/2'),
		('2_3/8 +','Expected number after "+"'),
		('2_3/8 + +','Unexpected operator "+"'),
		('2_3/8 9/8','Unexpected number "9/8"'),
		('+ 9/8','Unexpected operator "+"'),
		('9/8 woierjwe','Unexpected token "woierjwe"')]

	for test,answer in tests:
		print('Testing "%s" == "%s"'%(test,answer))

		try:
			calculated=evaluate_line(test)
		except Exception as error:
			calculated=str(error)

		if calculated==answer:
			print('\t PASS')
		else:
			print('\t FAIL (GOT %s)'%calculated)

		print('')

if __name__=='__main__':
	try:
		unit_tests()
	except KeyboardInterrupt:
		exit(-1)
