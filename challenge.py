#!/usr/bin/env python3
import enum
import re

class State(enum.Enum):
	FIRSTNUMBER=0
	NUMBER=1
	OPERATOR=2

class Fraction:
	def __init__(self,whole,num,den):
		self.num=whole*den+num
		self.den=den

	def __add__(self,rhs):
		num=self.num*rhs.den+self.den*rhs.num
		den=self.den*rhs.den
		return Fraction(0,num,den)

	def __add__(self,rhs):
		num=self.num*rhs.den-self.den*rhs.num
		den=self.den*rhs.den
		return Fraction(0,num,den)

	def __mul__(self,rhs):
		num=self.num*rhs.num
		den=self.den*rhs.den
		return Fraction(0,num,den)

	def __div__(self,rhs):
		num=self.num*rhs.den
		den=self.den*rhs.num
		return Fraction(0,num,den)

	def __str__(self):
		return '%d_%d/%d'%(0,self.num,self.den)

def parse_number(lexeme):
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
	answer=None
	next_op=None
	valid_ops='+-*/'
	state=State.FIRSTNUMBER

	#Parse line
	for lexeme in line.strip().split():

		#Found an operator
		if len(lexeme)==1 and lexeme in valid_ops:

			#Wrong state - error
			if state!=State.OPERATOR:
				raise Exception('Unexpected operator "%s"'%lexeme)

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
	'''
	tests=[('1/2 * 3_3/4','1_7/8'),
		('2_3/8 + 9/8','3_1/2'),
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
