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
from mycroft.util.parse import extractnumber, is_numeric, normalize

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


math_operations = ["+", "-", "/", "*", "!", "^", "**", "exp", "log", "sqrt",
                   "(",
              ")", "sqr", "qb", "pow", "=", "is"]


class ElementalOperation():
    def __init__(self, x=0, y=0, op="+"):
        self.constants = {"pi": math.pi}
        self.variables = {}
        self.num_1 = x
        self.num_2 = y
        self.op = str(op)
        self.nice = False

    def set_nice(self):
        self.nice = True

    def define_var(self, var, value="unknown"):
        self.variables[var] = str(value)

    def _operate(self, operation, x=0, y=1):
        # TODO equations
        if operation == "is":
            self.define_var(str(x), str(y))
            return str(x) + " = " + str(y)
        if str(x) in self.constants:
            x = self.constants[str(x)]
        if str(y) in self.constants:
            y = self.constants[str(y)]
        if str(x) in self.variables:
            x = self.variables[str(x)]
        if str(y) in self.variables:
            y = self.variables[str(y)]
        if not is_numeric(x) and is_numeric(y):
            return str(x) + " " + operation + " " + str(float(y))
        if is_numeric(x) and not is_numeric(y):
            return str(float(x)) + " " + operation + " " + str(y)
        if not is_numeric(x) and not is_numeric(y):
            return str(x) + " " + operation + " " + str(y)
        x = float(x)
        y = float(y)
        result = ""
        if operation == "+":
            result = x + y
        elif operation == "/":
            result = x / y
        elif operation == "-":
            result = x - y
        elif operation == "*":
            result = x * y
        elif operation == "%":
            result = x % y
        elif operation == "sqrt":
            result = math.sqrt(x)
        elif operation == "!":
            result = math.factorial(x)
        elif operation == "log":
            result = math.log(x, y)
        elif operation == "exp":
            result = math.exp(x)
        elif operation in ["^", "**", "pow"]:
            result = math.pow(x, y)
        elif operation == "sqr":
            result = math.pow(x, 2)
        elif operation == "qb":
            result = math.pow(x, 3)
        # TODO priority
        elif operation == "(":
            pass
        elif operation == ")":
            pass
        if self.nice:
            result = nice_number(float(result)).replace(" ", "_")
        return result

    def get_expression(self):
        return str(self.num_1) + " " + self.op + " " + str(self.num_2)

    def operate(self):
        x = self.num_1
        y = self.num_2
        if x in self.constants:
            x = self.constants[x]
        if y in self.constants:
            y = self.constants[y]
        if x in self.variables:
            x = self.variables[x] if self.variables[x] != "unknown" else x
        if y in self.variables:
            y = self.variables[y] if self.variables[y] != "unknown" else y
        return self._operate(self.op, x, y)

    def set(self, x, y, op):
        self.num_1 = x
        self.num_2 = y
        self.op = str(op)


class StringOperation():
    def __init__(self, input_str, variables=None, nice=False, lang="en-us"):
        self.lang = lang
        self.nice = nice
        if variables is None:
            variables = {}
        self.variables = variables
        self.raw_str = input_str
        self.string = normalize(input_str, self.lang)

        if is_numeric(self.string):
            self.input_operations = [["0.0", "+", self.string]]
            self.chain = [self.string]
            self.result = self.chain[0]
        else:
            self.input_operations, self.leftover = extract_expression(
                self.string, self.lang)
            self.chain, self.result = self._chained_operation(
                self.input_operations)

        self._get_result()

    def _get_vars_data(self, op):
        num1 = ""
        num2 = ""
        var1 = op[0]
        var2 = op[2]
        for i in range(0, len(op[0])):
            char = op[0][i]
            if is_numeric(char) or char == ".":
                num1 += char
                var1 = op[0][i + 1:]
        for i in range(0, len(op[2])):
            char = op[2][i]
            if is_numeric(char) or char == ".":
                num2 += char
                var2 = op[2][i + 1:]
        if not num1:
            num1 = "1"
        if not num2:
            num2 = "1"
        return num1, num2, var1, var2

    def _org_var(self, operations):
        passes = [
            # ["=", "is"],
            # ["!", "exp", "log", "^", "sqrt", "**", "sqr", "qb", "pow"],
            ["*", "/", "%"],
            ["+", "-"]
        ]

        # handle vars
        inserts = {}
        for idx, op in enumerate(operations):
            if not op:
                continue
            num1, num2, var1, var2 = self._get_vars_data(op)
            # print num1, num2, var1, var2
            if not is_numeric(op[0]) and op[0] != "prev":
                operations[idx][0] = op[0] = "prev"
                operation = [num1, "*", var1]
                inserts[idx] = operation
            elif not is_numeric(op[2]) and op[2] != "next":
                operations[idx][2] = op[2] = "next"
                operation = [num2, "*", var2]
                inserts[idx + 1] = operation
                # TODO find ( and )
        new = operations
        for insert in inserts:
            new.insert(insert, inserts[insert])
        # solve vars
        OP = ElementalOperation("0.0", "0.0", "+")
        for current_pass in passes:
            for idx, op in enumerate(operations):
                if not op:
                    continue
                # find info
                op[0] = str(op[0])
                op[2] = str(op[2])
                num1, num2, var1, var2 = self._get_vars_data(op)
                prev_op = operations[idx - 1] if idx - 1 >= 0 else ""
                next_op = operations[idx + 1] if idx + 1 < len(
                    operations) else ""

                # chain with previous
                if prev_op:
                    prev_op[0] = str(prev_op[0])
                    prev_op[2] = str(prev_op[2])
                    prevnum1, prevnum2, prevvar1, vprevar2 = self._get_vars_data(
                        prev_op)
                    if not is_numeric(op[0]) and op[0] != "prev":
                        if prev_op[1] in current_pass:
                            if prev_op[2] != "next" and prevvar2 == var1:
                                OP.set(prevnum2, num1, prev_op[1])
                                if self.nice:
                                    OP.set_nice()
                                OP.variables = self.variables
                                result = str(OP.operate())
                                operations[idx - 1][2] = result + var1
                                operations[idx][0] = "prev"

                if op[1] not in current_pass:
                    continue

                continue
                if op[1] == "(":
                    exp = []
                    end = -1
                    for i, n_op in enumerate(operations):
                        if not n_op:
                            continue
                        if n_op[1] == ")":
                            end = i
                            break
                    if end == -1:
                        operations[idx] = ""
                        continue
                    # get expression between ( )
                    exp = operations[idx, end]
                    # solve
                    res = self._chained_operation(exp)[1]
                    # extract solved ops
                    exp, leftover = extract_expression(res)
                    # replace in chain
                    operations = operations[:idx] + exp + operations[end:]
                    # count vars
        return operations

    def _chained_operation(self, operations):
        # this operation object will contain all var definitions and be
        # re-set and re used internally
        OP = ElementalOperation()
        if self.nice:
            OP.set_nice()
        OP.variables = self.variables
        # prioritize operations by this order
        passes = [
            # ["=", "is"],
            ["!", "exp", "log", "^", "sqrt", "**", "sqr", "qb", "pow"],
            ["*", "/", "%"],
            ["+", "-"]
        ]
        # organize vars and handle parenthesis
        #        operations = self._org_var(operations)

        for current_pass in passes:
            for idx, op in enumerate(operations):
                if not op or op[1] not in current_pass:
                    continue
                if is_numeric(op[0]):
                    op[0] = float(op[0])
                if is_numeric(op[2]):
                    op[2] = float(op[2])
                op[0] = str(op[0])
                op[2] = str(op[2])

                # find nums and vars
                prev_op = operations[idx - 1] if idx - 1 >= 0 else ""
                next_op = operations[idx + 1] if idx + 1 < len(
                    operations) else ""
                num1 = ""
                num2 = ""
                var1 = op[0]
                var2 = op[2]
                for i in range(0, len(op[0])):
                    char = op[0][i]
                    if is_numeric(char) or char == ".":
                        num1 += char
                        var1 = op[0][i + 1:]

                for i in range(0, len(op[2])):
                    char = op[2][i]
                    if is_numeric(char) or char == ".":
                        num2 += char
                        var2 = op[2][i + 1:]

                # check for numbers
                if op[0] in OP.constants:
                    op[0] = OP.constants[op[0]]
                if op[0] in OP.variables:
                    op[0] = OP.variables[op[0]]
                if op[2] in OP.constants:
                    op[2] = OP.constants[op[2]]
                if op[2] in OP.variables:
                    op[2] = OP.variables[op[2]]

                if is_numeric(op[0]) and op[1] in ["!", "exp", "sqrt", "^",
                                                   "**", "qb", "sqr", "pow",
                                                   "log"]:
                    OP.set(op[0], op[0], op[1])
                    result = OP.operate()
                    operations[idx] = ["0.0", "+", result]
                    continue

                # chain operation with previous member
                if op[0] == "prev":

                    if prev_op == ["0.0", "+", "0.0"]:
                        operations[idx][0] = "0.0"
                        operations[idx - 1] = ""
                    elif prev_op:
                        if is_numeric(prev_op[2]):
                            OP.set(prev_op[2], op[2], op[1])
                            operations[idx - 1][2] = "next"
                            result = OP.operate()
                            operations[idx] = ["0.0", "+", result]
                        elif prev_op[2] == "next":
                            operations[idx] = [prev_op[0], "+", op[2]]
                            operations[idx - 1] = ""

                # all numbers, solve operation
                if is_numeric(op[0]) and is_numeric(op[2]):
                    OP.set(op[0], op[2], op[1])
                    result = OP.operate()
                    operations[idx] = ["0.0", "+", result]
                    continue

                if is_numeric(op[0]) and not is_numeric(op[2]):
                    pass
                if not is_numeric(op[0]) and is_numeric(op[2]):
                    pass
                if not is_numeric(op[0]) and not is_numeric(op[2]):
                    # same expression both sides
                    if op[0] == op[2]:
                        num = num1
                        if op[1] == "-":
                            operations[idx] = ["0.0", "+", "0.0"]
                            continue
                        if op[1] == "/":
                            operations[idx] = ["0.0", "+", "1.0"]
                            continue
                        if op[1] == "*":
                            operations[idx] = [op[0], "sqr", op[0]]
                            continue
                        if op[1] == "+":
                            if not num:
                                operations[idx] = ["0.0", "+", "2.0" + op[0]]
                                continue
                            op[0] = op[0].replace(str(num), "")
                            num = str(2 * float(num))
                            operations[idx] = ["0.0", "+", num + op[0]]
                            continue
                            # TODO other ops ^ exp log sqr qb sqrt

                    # dif expression both sides
                    else:
                        if var1 == var2:
                            var = var1
                            OP.set(num1, num2, op[1])
                            result = str(OP.operate())

                            operations[idx] = ["0.0", "+", result + var]

        self.variables = OP.variables
        # clean empty elements
        result = ""
        chain = []
        for op in operations:
            chain.append(op)
            for element in op:
                if element and element != "prev" and element != "next":
                    # nice numbers in result
                    if not is_numeric(
                            element) and element not in math_operations:
                        if self.nice and element:
                            element = nice_var(element)
                    elif is_numeric(element) and self.nice:
                        element = nice_number(float(element)).replace(" ", "_")
                    result += str(element)
        return chain, result

    def _get_result(self, res=None):
        # clean

        if res is not None:
            res = res.replace(" ", "")
        else:
            res = self.result.replace(" ", "")

        if self.nice:
            words = res.split(" ")
            for idx, word in enumerate(words):
                if is_numeric(word):
                    words[idx] = nice_number(float(word))
            res = " ".join(words).replace(" ", "")

        while res and res[0] == "+":
            res = res[1:]
        res = res.replace("next", "")
        res = res.replace("prev", "")
        res = res.replace("+-", "-")
        res = res.replace("-+", "-")
        res = res.replace("++", "+")
        res = res.replace("--", "-")
        res = res.replace("+*", "*")
        res = res.replace("*+", "*")
        res = res.replace("-*", "*-")
        res = res.replace("/1", "")
        res = res.replace("/1.0", "")
        res = res.replace("sqr", " squared")
        res = res.replace("qb", " cubed")
        res = " " + res
        for op in math_operations:
            res = res.replace(op, " " + op + " ")
        # crop start zeros
        while " 0 + " in res or " 0.0 + " in res:
            res = res.replace(" 0 + ", " ")
            res = res.replace(" 0.0 + ", " ")
        res = res.replace(" 0 - ", " -")
        res = res.replace(" 0.0 - ", " -")
        self.result = res
        return res

    def solve(self, debug=False):
        if debug:
            print "normalized string:", self.string
            print "raw string:", self.raw_str

        lang = self.lang
        OP = StringOperation(self.raw_str, lang=lang, nice=self.nice)
        res = OP.result
        variables = OP.variables
        if debug:
            print "elementar operations:", OP.input_operations
            print "result:", res
            print "chain", OP.chain
        i = 0
        depth = 10
        prev_res = ""
        while not res == prev_res and i < depth:
            prev_res = res
            OP = StringOperation(res, variables=variables, lang=lang,
                                 nice=self.nice)
            res = OP.result
            variables = OP.variables
            if debug:
                print"elementar operations:", OP.input_operations
                print"result:", res
                print "chain", OP.chain
            i += 1
        if debug:
            print "vars:", OP.variables
            print "\n"
        # update result
        self._get_result(res)
        return self.result.replace("_", " ")


def nice_var(var_string):
    num = ""
    var = ""
    for i in range(0, len(var_string)):
        char = var_string[i]
        if is_numeric(char) or char == ".":
            num += char
            var = var_string[i + 1:]
        elif char in math_operations:
            words = var_string.split(" ")
            for idx, word in enumerate(words):
                if word not in math_operations:
                    words[idx] = nice_var(word)
            return " ".join(words)
    if num:
        num = nice_number(float(num)).replace(" ", "_")
        var_string = num + var
    return var_string


def solve_expression(string, nice=True, lang="en-us", debug=False):
    OP = StringOperation(string, lang=lang, nice=nice)
    res = OP.solve(debug=debug)
    res = res.replace("  ", " ")
    if res[0] == " ":
        res = res[1:]
    return res


def extract_expression(string, lang="en-us"):
    lang_lower = str(lang).lower()
    if lang_lower.startswith("en"):
        return extract_expression_en(string)


def extract_expression_en(string):
    expressions = {"+": ["add", "adding", "plus", "added"],
                   "-": ["subtract", "subtracting", "minus", "negative",
                         "subtracted"],
                   "/": ["divide", "dividing", "divided"],
                   "*": ["multiply", "multiplying", "times", "multiplied"],
                   "%": ["modulus"],
                   "!": ["factorial"],
                   #   "is": ["set"],  # TODO find better keyword for x = value
                   # "=": ["equals"],
                   "^": ["**", "^", "pow" "elevated", "power", "powered",
                         "raised"],
                   "sqr": ["squared"],
                   "sqrt": ["square_root"],
                   "qb": ["cubed", "qubed"],
                   "exp": ["exponent", "exponentiate", "exponentiated"],
                   "(": ["open"],
                   ")": ["close"]}

    noise_words = ["by", "and", "the", "in", "at", "a", "for", "an", "to",
                   "with", "off", "of", "is", "are", "can", "be"]
    string = normalize(string)
    # clean string
    for op in expressions:
        string = string.replace(op, " " + op + " ")
    words = string.replace(",", "").replace("'", "").replace('"', "") \
        .replace("square root", "square_root").split(" ")

    # replace natural language math vocabulary
    for idx, word in enumerate(words):
        for operation in expressions:
            if word in expressions[operation]:
                words[idx] = operation

    # convert all numbers
    for idx, word in enumerate(words):
        if not word:
            continue
        if extractnumber(word):
            words[idx] = str(float(extractnumber(word)))
        # join unknown vars nums
        if idx + 1 < len(words) and words[idx + 1] not in math_operations:
            # 3 x = 3x
            if is_numeric(word) and not is_numeric(words[idx + 1] and words[
                        idx + 1] not in noise_words):
                # words[idx] = str(float(words[idx])) + " * " + words[idx + 1]
                words[idx] = str(float(words[idx])) + words[idx + 1]
                words[idx + 1] = ""
        if idx - 1 >= 0 and word not in math_operations:
            # 1 2 x = 1 2x
            if not is_numeric(word) and is_numeric(words[idx - 1]) and words[
                idx] not in noise_words:
                # words[idx] = words[idx - 1] + " * " +  words[idx]
                words[idx] = words[idx - 1] + words[idx]
                words[idx - 1] = ""

    words = [word for word in words if word]

    # remove noise words
    for idx, word in enumerate(words):
        if word in noise_words:
            words[idx] = ""

    words = [word for word in words if word]
    exps = []

    # extract operations
    for idx, word in enumerate(words):
        if not word:
            continue
        # is an operation
        if word in expressions:
            operation = word
            if operation == "(" or operation == ")":
                exps.append(["prev", operation, "next"])
                continue
            if idx > 0:
                woi = words[idx - 1:idx + 2]
                words[idx - 1] = ""
                if idx + 1 < len(words):
                    words[idx + 1] = ""
                words[idx] = ""
                x = woi[0]
                try:
                    y = woi[2]
                except:
                    y = "next"
                if x == "":
                    x = "prev"
                if operation == "sqrt":
                    x = y
                exps.append([x, operation, y])
            else:
                # operation at first, is a sign
                y = words[idx + 1]
                words[idx + 1] = ""
                words[idx] = ""
                if operation == "-":
                    x = "-" + y
                    y = 0
                    operation = "+"
                    exps.append([x, operation, y])
                elif operation == "+":
                    exps.append(["0", operation, y])
                # or square root
                elif operation == "sqrt":
                    x = y
                    y = "next"
                    exps.append([x, operation, y])
                    # TODO exponent, log

    if not exps and extractnumber(string):
        exps = [["0.0", "+", str(extractnumber(string))]]
        words = [word for word in words if not is_numeric(word)]
        if words == []:
            words = ["___"]
    leftover = ""
    for word in words:
        if not word and "___" not in leftover:
            leftover += " ___"
        elif word:
            leftover += " " + word
    leftover = leftover[1:]
    return exps, leftover
