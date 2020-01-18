#!/usr/bin/env python3
'''
This is a simple challenge that does fraction based arithmetic.
Parts of this are done for the sake of the challenge (gcd and fractional math).
There are modules that do all of this...but it seemed like cheating...
'''
import enum
import sys
import re

def gcd(alpha, beta):
    '''
    Classic gcd - this exists in the math module...but for the sake of the challenge?
    Returns greatest common factor between two ints.
    Will not return 0.
    '''
    while beta:
        alpha, beta = beta, alpha%beta
    if alpha == 0:
        return 1
    return alpha

def simplify_fraction(num, den):
    '''
    Simplifies a numerator and denomenator into a whole part, numerator, and denomenator.
    Returns tuple (whole, num, den).
    '''
    whole = num//den
    num %= den

    while True:
        common_den = gcd(num, den)
        if common_den == 1:
            break
        num //= common_den
        den //= common_den

    return whole, num, den

class State(enum.Enum):
    '''
    Enum for tracking the state machine for parsing lines.
    '''
    FIRSTNUMBER = 0
    OPERATOR = 1
    NUMBER = 2

class Fraction:
    '''
    Basic fraction class.
    There's a Fraction class in the fraction module that would do what we want here...
    '''

    def __init__(self, whole, num, den):
        '''
        Takes a whole number, but only uses num and den internally.
        '''

        #Fix negative values
        if num < 0:
            whole = -whole
            num = abs(num)
        if den < 0:
            whole = -whole
            den = abs(den)

        #Convert w_n/d to n/d
        self._num = whole*den+num
        self._den = den

    def __add__(self, rhs):
        num = self._num*rhs._den+self._den*rhs._num
        den = self._den*rhs._den
        return Fraction(0, num, den)

    def __sub__(self, rhs):
        num = self._num*rhs._den-self._den*rhs._num
        den = self._den*rhs._den
        return Fraction(0, num, den)

    def __mul__(self, rhs):
        num = self._num*rhs._num
        den = self._den*rhs._den
        return Fraction(0, num, den)

    def __truediv__(self, rhs):
        num = self._num*rhs._den
        den = self._den*rhs._num
        return Fraction(0, num, den)

    def __str__(self):

        #Simplify
        whole, num, den = simplify_fraction(self._num, self._den)

        #No numerator - just return whole
        if num == 0:
            return '%d'%whole

        #No whole number, just return num/den
        if whole == 0:
            return '%d/%d'%(num, den)

        #Return all three parts
        return '%d_%d/%d'%(whole, num, den)

def parse_number(lexeme):
    '''
    Lexeme should be a str or Fraction.
    If lexeme is a Fraction, this function will return it.
    If lexee is a str, this function parses numbers that
    look like (where w, n, and d are all ints (- sign is ok)):
        w_n/d
        n/d
        w
    On success: Returns Fraction.
    On failure: Returns None.
    '''

    #Passed a Fraction - return it
    if isinstance(lexeme, Fraction):
        return lexeme

    #Attempt parsing via regex strings (ORDER OF THESE MATTER)
    exprs = [r'[-]?[\d]+[_][-]?[\d]+[/][-]?[\d]+',
             r'[-]?[\d]+[/][-]?[\d]+',
             r'[-]?[\d]+']
    for expr in exprs:
        if ''.join(re.findall(expr, lexeme)) == lexeme:

            #Parse all numbers and convert to integers
            parts = [int(num) for num in re.findall(exprs[-1], lexeme)]

            #w_n/d - no pad
            if len(parts) == 3:
                return Fraction(*parts)

            #n/d - left pad
            if len(parts) == 2:
                return Fraction(0, *parts)

            #w - right pad
            if len(parts) == 1:
                return Fraction(*parts, 0, 1)

    #Nothing found - return None
    return None

def apply_operation(lhs, op_str, rhs):
    '''
    Applies an operation string as an operation to given lhs and rhs.
    Returns a Fraction.
    '''
    if op_str == '+':
        return lhs+rhs
    if op_str == '-':
        return lhs-rhs
    if op_str == '*':
        return lhs*rhs
    if op_str == '/':
        return lhs/rhs
    raise Exception('Invalid operator "%s"'%op_str)

def evaluate_line(line):
    '''
    Evaluates a single line of w_n/d fractional numbers with operators: +-*/
    Each w_n/d and operator will be separated by one or more spaces.
    Returns Fraction.
    '''
    #Empty line
    if not line:
        return Fraction(0, 0, 1)

    #Order of operations
    op_order = ['*/', '+-']

    #Valid operators
    valid_ops = ''.join(op_order)

    #Split line into tokens
    lexemes = line.strip().split()

    #Set operators to skip to ensure order of operations
    for current_ops in op_order:

        #Scratch array for the next run of lexemes
        next_lexemes = []

        #Final return answer
        answer = Fraction(0, 0, 1)

        #Next operator to execute
        next_op = None

        #State machine state
        state = State.FIRSTNUMBER

        #Evaluate line
        for lexeme_ind, lexeme in enumerate(lexemes):

            #Found an operator
            if isinstance(lexeme, str) and len(lexeme) == 1 and lexeme in valid_ops:

                #Wrong state - error
                if state != State.OPERATOR:
                    raise Exception('Unexpected operator "%s"'%lexeme)

                #Last lexeme is an operator - error
                if lexeme_ind+1 >= len(lexemes):
                    raise Exception('Expected number after "%s"'%lexeme)

                #Set next op and change state
                state = State.NUMBER
                next_op = lexeme
                continue

            #Parse lexeme into a Fraction (if needed)
            number = parse_number(lexeme)

            #Found number
            if number is not None:

                #Wrong state - error
                if state not in [State.FIRSTNUMBER, State.NUMBER]:
                    raise Exception('Unexpected number "%s"'%lexeme)

                #First number - no evaluation
                if state == State.FIRSTNUMBER:
                    answer = number

                #Next operation is not in the current order:
                #  Add the current answer and the operations to the stack
                #  Set answer to current node
                elif next_op not in current_ops:
                    next_lexemes += [str(answer), next_op]
                    answer = number

                #Another number, evaluate operation
                else:
                    answer = apply_operation(answer, next_op, number)

                #Change state
                state = State.OPERATOR
                continue

            #Not a number or operator - error
            raise Exception('Unexpected token "%s"'%lexeme)

        #Add final answer to stack
        next_lexemes.append(answer)

        #Rerun with new batch of lexemes
        lexemes = next_lexemes

    return answer

def unit_tests():
    '''
    Runs unit tests, returns nothing.
    '''
    tests = [('1/2 * 3_3/4', '1_7/8'),
             ('2_3/8 + 9/8', '3_1/2'),
             ('2_3/8 - 9/8', '1_1/4'),
             ('2_3/8 * 9/8', '2_43/64'),
             ('2_3/8 / 9/8', '2_1/9'),
             ('1', '1'),
             ('1/2', '1/2'),
             ('3_1/2', '3_1/2'),
             ('-3_1/2', '-3_1/2'),
             ('3_-1/2', '-3_1/2'),
             ('3_1/-2', '-3_1/2'),
             ('2_3/8 +', 'Expected number after "+"'),
             ('2_3/8 + +', 'Unexpected operator "+"'),
             ('2_3/8 9/8', 'Unexpected number "9/8"'),
             ('+ 9/8', 'Unexpected operator "+"'),
             ('9/8 woierjwe', 'Unexpected token "woierjwe"'),
             ('2 * 3 + 4 * 5', '26'),
             ('', '0')]

    for test, answer in tests:
        try:
            calculated = str(evaluate_line(test))
        except Exception as error:
            calculated = str(error)

        outcome = 'PASS'
        if calculated != answer:
            outcome = 'FAIL (GOT "%s")'%calculated

        print('%s - Testing "%s" == "%s"'%(outcome, test, answer))

def main():
    '''
    Interpreter that continually prompts user for a line, evaluates, and prints the answer.
    Returns nothing.
    '''

    #Print banner
    print('Fraction interpreter v1.0')
    print('Use Ctrl+C or Ctrl+D to exit')

    #Interpreter loop
    while True:

        #Prompt user
        sys.stdout.write('? ')
        sys.stdout.flush()

        #Grab line from user
        line = sys.stdin.readline()

        #Ctrl+D
        if not line:
            print('Exiting...')
            sys.exit(-1)

        #Attempt evaluation
        try:
            answer = str(evaluate_line(line))

        #Error
        except Exception as error:
            answer = str(error)

        #Print response
        print('= %s\n'%answer)

if __name__ == '__main__':
    try:
        #unit_tests()
        main()

    #Ctrl+C
    except KeyboardInterrupt:
        sys.exit(-1)
