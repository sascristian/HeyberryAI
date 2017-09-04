# -*- coding: iso-8859-15 -*-

# Copyright 2017 Mycroft AI, Inc.
#
# This file is part of Mycroft Core.
#
# Mycroft Core is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Mycroft Core is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Mycroft Core.  If not, see <http://www.gnu.org/licenses/>.

import math
from mycroft.util.parse import extractnumber, is_numeric

FRACTION_STRING_EN = {
    2: 'half',
    3: 'third',
    4: 'forth',
    5: 'fifth',
    6: 'sixth',
    7: 'seventh',
    8: 'eigth',
    9: 'ninth',
    10: 'tenth',
    11: 'eleventh',
    12: 'twelveth',
    13: 'thirteenth',
    14: 'fourteenth',
    15: 'fifteenth',
    16: 'sixteenth',
    17: 'seventeenth',
    18: 'eighteenth',
    19: 'nineteenth',
    20: 'twentyith'
}

FRACTION_STRING_PT = {
    2: 'meio',
    3: u'terço',
    4: 'quarto',
    5: 'quinto',
    6: 'sexto',
    7: u'sétimo',
    8: 'oitavo',
    9: 'nono',
    10: u'décimo',
    11: 'onze avos',
    12: 'doze avos',
    13: 'treze avos',
    14: 'catorze avos',
    15: 'quinze avos',
    16: 'dezasseis avos',
    17: 'dezassete avos',
    18: 'dezoito avos',
    19: 'dezanove avos',
    20: u'vigésimo',
    30: u'trigésimo',
    100: u'centésimo',
    1000: u'milésimo'
}


def nice_number(number, lang="en-us", speech=True, denominators=None):
    """Format a float to human readable functions

    This function formats a float to human understandable functions. Like
    4.5 becomes 4 and a half for speech and 4 1/2 for text
    Args:
        number (str): the float to format
        lang (str): the code for the language text is in
        speech (bool): to return speech representation or text representation
        denominators (iter of ints): denominators to use, default [1 .. 20]
    Returns:
        (str): The formatted string.
    """
    result = convert_number(number, denominators)
    if not result:
        return str(round(number, 3))

    if not speech:
        whole, num, den = result
        if num == 0:
            return str(whole)
        else:
            return '{} {}/{}'.format(whole, num, den)

    lang_lower = str(lang).lower()
    if lang_lower.startswith("en"):
        return nice_number_en(result)
    elif lang_lower.startswith("pt"):
        return nice_number_pt(result)
    # TODO: Normalization for other languages
    return str(number)


def nice_number_en(result):
    """ English conversion for nice_number """
    whole, num, den = result
    if num == 0:
        return str(whole)
    den_str = FRACTION_STRING_EN[den]
    if whole == 0:
        if num == 1:
            return_string = 'a {}'.format(den_str)
        else:
            return_string = '{} {}'.format(num, den_str)
    elif num == 1:
        return_string = '{} and a {}'.format(whole, den_str)
    else:
        return_string = '{} and {} {}'.format(whole, num, den_str)
    if num > 1:
        return_string += 's'
    return return_string


def nice_number_pt(result):
    """ Portuguese conversion for nice_number """
    whole, num, den = result
    if num == 0:
        return str(whole)
    # denominador
    den_str = FRACTION_STRING_PT[den]
    # fracções
    if whole == 0:
        if num == 1:
            # um décimo
            return_string = 'um {}'.format(den_str)
        else:
            # três meio
            return_string = '{} {}'.format(num, den_str)
    # inteiros >10
    elif num == 1:
        # trinta e um
        return_string = '{} e {}'.format(whole, den_str)
    # inteiros >10 com fracções
    else:
        # vinte e 3 décimo
        return_string = '{} e {} {}'.format(whole, num, den_str)
    # plural
    if num > 1:
        return_string += 's'
    return return_string


def extract_expression(string, lang="en-us"):
    print "\n" + string + " equals:"
    lang_lower = str(lang).lower()
    if lang_lower.startswith("en"):
        return extract_expression_en(string)


def extract_expression_en(string):
    expressions = {"+": ["add", "adding", "plus"],
                   "-": ["subtract", "subtracting", "minus", "negative"],
                   "/": ["divide", "dividing"],
                   "*": ["multiply", "multiplying", "times"],
                   "%": ["modulus"],
                   "!": ["factorial"],
                   "is": ["equals"],
                   "^": ["**", "elevated"],
                   "exp": ["exponent", "exponentiated"],
                   "(": ["open"],
                   ")": ["close"]}
    constants = {"pi": math.pi}
    variables = {}
    for op in expressions:
        string = string.replace(op, " " + op + " ")
    words = string.replace(",", "").split(" ")
    for idx, word in enumerate(words):
        for operation in expressions:
            if word in expressions[operation]:
                words[idx] = operation
    result = 0
    start = 0
    operation = None
    inserts = []
    divs = []

    def operate(operation, x=0, y=1):
        print x, y
        if not is_numeric(x) or not is_numeric(y):
            return str(x) + " " + operation + " " + str(y)
        x = float(x)
        y = float(y)
        if operation == "+":
            return x + y
        if operation == "/":
            return x / y
        if operation == "-":
            return x - y
        if operation == "*":
            return x * y
        if operation == "%":
            return x % y
        # TODO
        if operation == "sqrt":
            return math.sqrt(x)
        if operation == "!":
            return math.factorial(x)
        if operation == "log":
            pass
        if operation == "exp":
            return math.exp(y)
        if operation == "^":
            return x ** y
        if operation == "(":
            pass
        if operation == ")":
            pass
        return 1

    priority = ["(", ")", "!"]
    for idx, word in enumerate(words):
        if not word:
            continue
        if extractnumber(word):
            word = extractnumber(word)
        if word in constants:
            words[idx] = str(constants[word])
        elif word in variables:
            if variables[word] != "unknown":
                words[idx] = str(variables[word])
        elif word in expressions:
            if word == "is":
                variable = words[idx - 1]
                variables[variable] = "unknown"
                if is_numeric(words[idx + 1]):
                    variables[variable] = words[idx + 1]
            else:
                woi = words[start:idx]
                candidate = " ".join(woi)
                num = extractnumber(candidate)
                if not num:
                    if word == "+" or word == "-":
                        inserts.append([candidate, operation])
                    else:
                        divs.append([candidate + word + words[
                            idx + 2], operation])
                else:
                    inserts.append([num, operation])
                operation = word
                start = idx + 1
        elif not is_numeric(word):
            if word not in variables:
                variables[word] = "unknown"

        if idx == len(words) - 1:
            if operation:
                num = " ".join(words[start:])
                try:
                    num = float(num)
                except:
                    inserts.append([num, operation]
                                   )
    print divs, inserts

    for variable, operation in divs:
        if is_numeric(variable):
            result = operate(operation, result, variable)
        else:
            if variable and variable != " " and result and operation:
                result = str(variable) + "+" + str(result)
    for variable, operation in inserts:
        if is_numeric(variable):
            result = operate(operation, result, variable)

        else:
            if variable and variable != " " and result and operation:
                result = str(variable) + operation + " " + str(result)

    return str(result).strip(" ")


def convert_number(number, denominators):
    """ Convert floats to mixed fractions """
    int_number = int(number)
    if int_number == number:
        return int_number, 0, 1

    frac_number = abs(number - int_number)
    if not denominators:
        denominators = range(1, 21)

    for denominator in denominators:
        numerator = abs(frac_number) * denominator
        if (abs(numerator - round(numerator)) < 0.01):
            break
    else:
        return None

    return int_number, int(round(numerator)), denominator


if __name__ == "__main__":
    print extract_expression("x + 2 +3+5")
    print extract_expression("2 minus 3 + x")
    print extract_expression("- 5 + x + 1")
    print extract_expression("3! + 1")
    print extract_expression("x equals 4, x! + 1")
    print extract_expression("minus 1 + pi")
    print extract_expression("ten + negative 1")
    print extract_expression("2 exp 2")
    print extract_expression("2 ^ 3 + x / y")
    print extract_expression("6 !")
    print extract_expression("2 + x / y + 3")
