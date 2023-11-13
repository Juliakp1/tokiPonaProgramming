# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #
# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #
#
# This is the code runner for the toki pona programming language, please run it before reading it!
#
# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #
# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

import os

from rply import LexerGenerator
lg = LexerGenerator()
lg.add('ID', r'\[(\_([jklmnpstw]?[aeiou][n]?)+)+\]') 		# how does this work this perfectly
lg.add('WORDS', r'\"[a-zA-Z_ \\\(\)\?\!\:]+\"')   # no limitations for the letters in strings here, unlike the variable names
lg.add('INT', r'nanpa')
lg.add('STR', r'nimi')
lg.add('ARR', r'kulupu')
lg.add('WHILE', r'awen la')
lg.add('ELSE', r'ante la')
lg.add('IF', r'la')
lg.add('THEN', r'ni')
lg.add('END', r'pini')
lg.add('COMP', r'sama sama')
lg.add('PRINT', r'toki')
lg.add('INPUT', r'kute')
lg.add('OPEN_PARENS', r'\(')
lg.add('CLOSE_PARENS', r'\)')
lg.add('EQUALS', r'sama')
lg.add('SUB', r'ala en')
lg.add('ADD', r'en')
lg.add('MUL', r'namako')
lg.add('DIV', r'kipisi')
lg.add('SIMPLE', r"\b(?:luka|tu|mute|wan)\b")	# it will separate all of the numbers, this will be dealt with shortly
lg.add('NEG', r"ala")	# this is a negative number
lg.ignore('\s+')    # ignores all whitespace
lexer = lg.build()

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #
# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

from rply.token import BaseBox

class Program(BaseBox):
    def __init__(self, decls,cmmds):
        self.decls = decls
        self.cmmds = cmmds

    def accept(self, visitor):
        visitor.visit_program(self)

# ------------------------------------------- #
# Declarations

class Declarations(BaseBox):
    def __init__(self, decl,decls):
        self.decl = decl
        self.decls = decls

    def accept(self, visitor):
        visitor.visit_declarations(self)

class Declaration(BaseBox):
    def __init__(self, id,tp):
        self.id = id
        self.tp = tp

    def accept(self, visitor):
        visitor.visit_declaration(self)

# ------------------------------------------- #
# Commands

class Commands(BaseBox):
    def __init__(self, cmmd,cmmds):
        self.cmmd = cmmd
        self.cmmds = cmmds

    def accept(self, visitor):
        return visitor.visit_commands(self)

class Attribution(BaseBox):
    def __init__(self, id, expr, index):
        self.id = id
        self.expr = expr
        self.index = index

    def accept(self, visitor):
        return visitor.visit_attribution(self)

# ------------------------------------------- #

class Expr(BaseBox):
    def accept(self, visitor):
        method_name = 'visit_{}'.format(self.__class__.__name__.lower())
        visit = getattr(visitor, method_name)
        return visit(self)

class IfElse(BaseBox):
    def __init__(self, expr1, expr2, cmmdif, cmmdelse):
        self.expr1=expr1
        self.expr2=expr2
        self.cmmdif=cmmdif
        self.cmmdelse=cmmdelse

    def accept(self, visitor):
        visitor.visit_ifelse(self)

class While (BaseBox):
    def __init__(self, expr1, expr2, cmmds):
        self.expr1=expr1
        self.expr2=expr2
        self.cmmds=cmmds

    def accept(self, visitor):
        visitor.visit_while(self)

# ------------------------------------------- #
# Number and its classifications

class Compounds(Expr):
    def __init__(self, simple, compounds,neg):
        self.simple = simple
        self.compounds = compounds
        self.neg = neg
    def accept(self, visitor):
        return visitor.visit_compounds(self)

# ------------------------------------------- #
# Other expressions

class Print(Expr):
    def __init__(self, value):
        self.value = value
    def accept(self, visitor):
        visitor.visit_print(self)

class Input(Expr):
    def __init__(self, id):
        self.id = id
    def accept(self, visitor):
        visitor.visit_input(self)

class Id(Expr):
    def __init__(self, value, index):
        self.value = value
        self.index = index
    def accept(self, visitor):
        return visitor.visit_id(self)
    
class String(Expr):
    def __init__(self, value):
        self.value = value
    def accept(self, visitor):
        return visitor.visit_string(self)

# -- the basic binary operations, they are all handeled by the BinaryOp class -- #
class BinaryOp(Expr):
    def __init__(self, left, right):
        self.left = left
        self.right = right
class Add(BinaryOp):
  pass
class Sub(BinaryOp):
  pass
class Mul(BinaryOp):
  pass
class Div(BinaryOp):
  pass

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #
# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

from rply import ParserGenerator

pg = ParserGenerator(
    # A list of all token names, accepted by the lexer.
    ['EQUALS', 'COMP',
     'ADD', 'SUB', 'MUL', 'DIV', 
     'WHILE', 'IF', 'ELSE', 'THEN', 'END', 
     'ID', 'SIMPLE', 'NEG',
     'WORDS',
     'INT', 'STR', 'ARR',
     'OPEN_PARENS', 'CLOSE_PARENS', 
     'PRINT', 'INPUT'
    ],
    # A list of precedence rules with ascending precedence, to
    # disambiguate ambiguous production rules.
    precedence=[
        ('left', ['ADD', 'SUB']),
        ('left', ['MUL', 'DIV'])
    ]
)

# ------------------------------------------- #

@pg.production('program : declarations commands')
def program(p):
    return Program(p[0],p[1])

@pg.production('declarations : declaration')
def declarations(p):
    return Declarations(p[0],None)

@pg.production('declarations : declaration declarations')
def declarations(p):
    return Declarations(p[0],p[1])

@pg.production('declaration : INT ID')
def declaration_integer(p):
    return Declaration(p[1].getstr(), "int")

@pg.production('declaration : STR ID')
def declaration_integer(p):
    return Declaration(p[1].getstr(), "str")

@pg.production('declaration : ARR ID')
def declaration_integer(p):
    return Declaration(p[1].getstr(), "arr")

# ------------------------------------------- #
# Commands (anything that isnt a declaration)

@pg.production('commands : attribution commands')
def command_commands(p):
    return Commands(p[0],p[1])
@pg.production('commands : attribution')
def commands_command(p):
    return Commands(p[0],None)

@pg.production('commands : if-else commands')
def command_commands(p):
    return Commands(p[0],p[1])
@pg.production('commands : if-else')
def command_commands(p):
    return Commands(p[0],None)

@pg.production('commands : while commands')
def command_commands(p):
    return Commands(p[0],p[1])
@pg.production('commands : while')
def command_commands(p):
    return Commands(p[0],None)

@pg.production('commands : print commands')
def command_commands(p):
    return Commands(p[0],p[1])
@pg.production('commands : print')
def command_commands(p):
    return Commands(p[0],None)

@pg.production('commands : input commands')
def command_commands(p):
    return Commands(p[0],p[1])
@pg.production('commands : input')
def command_commands(p):
    return Commands(p[0],None)

# ------------------------------------------- #
# Commands

@pg.production('attribution : ID EQUALS expression')
def commands_attribution(p):
    return Attribution(p[0].getstr(), p[2], None)

@pg.production('attribution : ID OPEN_PARENS compounds CLOSE_PARENS EQUALS expression')
def commands_attribution(p):
    return Attribution(p[0].getstr(), p[5], p[2])

@pg.production('if-else : IF OPEN_PARENS expression COMP expression CLOSE_PARENS THEN commands ELSE commands END')
def expression_ifelse1(p):
    return IfElse (p[2],p[4],p[7],p[9])
@pg.production('if-else : IF OPEN_PARENS expression COMP expression CLOSE_PARENS THEN commands END')
def expression_ifelse2(p):
    return IfElse (p[2],p[4],p[7],None)
@pg.production('if-else : IF OPEN_PARENS expression COMP expression CLOSE_PARENS ELSE commands END ')
def expression_ifelse3(p):
    return IfElse (p[2],p[4],None,p[7])

@pg.production('while : WHILE OPEN_PARENS expression COMP expression CLOSE_PARENS THEN commands END')
def expression_while(p):
    return While (p[2],p[4],p[7])

@pg.production('print : PRINT expression')
def expression_print(p):
    return Print(p[1])

@pg.production('input : INPUT ID')
def expression_input(p):
    return Input(p[1].getstr())

# ------------------------------------------- #

@pg.production('compounds : SIMPLE')
def compounds_compound(p):
    return Compounds(p[0],None, 1)
@pg.production('compounds : SIMPLE NEG')
def compounds_compound2(p):
    return Compounds(p[0],None, -1)
@pg.production('compounds : SIMPLE compounds')
def compound_compounds3(p):
    return Compounds(p[0],p[1], 1)
@pg.production('compounds : SIMPLE compounds NEG')
def compound_compounds4(p):
    return Compounds(p[0],p[1], -1)

# ------------------------------------------- #

@pg.production('expression : ID')
def expression_id(p):
    return Id(p[0].getstr(), None)
@pg.production('expression : ID OPEN_PARENS compounds CLOSE_PARENS')
def expression_id(p):
    return Id(p[0].getstr(), p[2])

@pg.production('expression : WORDS')
def expression_id(p):
    return String(p[0].getstr())

@pg.production('expression : SIMPLE')
def compounds_compound(p):
    return Compounds(p[0],None, 1)
@pg.production('expression : SIMPLE NEG')
def compounds_compound2(p):
    return Compounds(p[0],None, -1)
@pg.production('expression : SIMPLE compounds')
def compound_compounds3(p):
    return Compounds(p[0],p[1], 1)
@pg.production('expression : SIMPLE compounds NEG')
def compound_compounds4(p):
    return Compounds(p[0],p[1], -1)

@pg.production('expression : expression ADD expression')
@pg.production('expression : expression SUB expression')
@pg.production('expression : expression MUL expression')
@pg.production('expression : expression DIV expression')
def expression_binop(p):
    left = p[0]
    right = p[2]
    if p[1].gettokentype() == 'ADD':
        return Add(left, right)
    elif p[1].gettokentype() == 'SUB':
        return Sub(left, right)
    elif p[1].gettokentype() == 'MUL':
        return Mul(left, right)
    elif p[1].gettokentype() == 'DIV':
        return Div(left, right)
    else:
        raise AssertionError('Oops, this should not be possible!')

# @pg.error
# def error_handler(token):
#     raise ValueError("Ran into a %s where it wasn't expected" % token.gettokentype())

parser = pg.build()

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #
# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

ST={}

class Visitor(object):
  pass

class SymbolTable(Visitor):
    def visit_program(self, prog):
        prog.decls.accept(self)

    def visit_declarations(self, d):
        d.decl.accept(self)
        if d.decls!=None:
          d.decls.accept(self)

    def visit_declaration(self, d):
        ST[d.id]=d.tp

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #
# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

class Decorator(Visitor):

    def visit_program(self, i):
        i.cmmds.accept(self)

    # ------------------------------------------- #

    def visit_commands(self, d):
        d.cmmd.accept(self)
        if d.cmmds!=None:
          d.cmmds.accept(self)

    def visit_attribution(self, i):
        if i.id in ST:
          i.decor_type=ST[i.id]
        else:
          raise AssertionError('id not declared')
        i.expr.accept(self)

    # ------------------------------------------- #

    def visit_while(self, i):
        i.expr1.accept(self)
        i.expr2.accept(self)
        i.cmmds.accept(self)

    def visit_ifelse(self, i):
        i.expr1.accept(self)
        i.expr2.accept(self)
        if i.cmmdif!=None:
          i.cmmdif.accept(self)
        if i.cmmdelse!=None:
          i.cmmdelse.accept(self)
    # ------------------------------------------- #
    
    def visit_print(self, i):
        pass
    
    def visit_input(self, i):
        if i.id in ST:
          i.decor_type=ST[i.id]
        else:
          raise AssertionError('id not declared')
    
    def visit_string(self, i):
        i.decor_type="str"

    def visit_compounds(self, i):
        if i.compounds!=None:
          i.compounds.accept(self)
        i.decor_type="int"

    # ------------------------------------------- #

    def visit_id(self, i):
        if i.value in ST:
          i.decor_type=ST[i.value]
        else:
          raise AssertionError('id not declared')

    def visit_add(self, a):
        a.left.accept(self)
        a.right.accept(self)
        if a.left.decor_type=="int" and a.right.decor_type=="int":
          a.decor_type="int"
        elif a.left.decor_type=="str" and a.right.decor_type=="str":
          a.decor_type="str"
        elif a.left.decor_type=="arr" or a.right.decor_type=="arr":
          pass # not an issue!
        else:
          raise AssertionError('id values incompatible')

    def visit_sub(self, a):
        a.left.accept(self)
        a.right.accept(self)
        if a.left.decor_type=="int" and a.right.decor_type=="int":
          a.decor_type="int"
        elif a.left.decor_type=="str" and a.right.decor_type=="str":
          a.decor_type="str"
        elif a.left.decor_type=="arr" or a.right.decor_type=="arr":
          pass # not an issue!
        else:
          raise AssertionError('id values incompatible')

    def visit_mul(self, a):
        a.left.accept(self)
        a.right.accept(self)
        if a.left.decor_type=="int" and a.right.decor_type=="int":
          a.decor_type="int"
        elif a.left.decor_type=="str" and a.right.decor_type=="str":
          a.decor_type="str"
        elif a.left.decor_type=="arr" or a.right.decor_type=="arr":
          pass # not an issue!
        else:
          raise AssertionError('id values incompatible')

    def visit_div(self, a):
        a.left.accept(self)
        a.right.accept(self)
        if a.left.decor_type=="int" and a.right.decor_type=="int":
          a.decor_type="int"
        elif a.left.decor_type=="str" and a.right.decor_type=="str":
          a.decor_type="str"
        elif a.left.decor_type=="arr" or a.right.decor_type=="arr":
          pass # not an issue!
        else:
          raise AssertionError('id values incompatible')

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #
# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

class TypeVerifier(Visitor):

    def visit_program(self, i):
        i.cmmds.accept(self)

    def visit_commands(self, d):
        d.cmmd.accept(self)
        if d.cmmds!=None:
          d.cmmds.accept(self)

    def visit_print(self, i):
        pass

    def visit_input(self, i):
        pass

    def visit_ifelse(self, i):
        if i.expr1.decor_type!=i.expr2.decor_type:
          raise AssertionError('type error')
    def visit_while(self, i):
        if i.expr1.decor_type!=i.expr2.decor_type:
          raise AssertionError('type error')


    def visit_attribution(self, i):
        if i.decor_type=="int" and i.expr.decor_type!="int":
            raise AssertionError('type error')
        if i.decor_type=="str" and i.expr.decor_type!="str":
            raise AssertionError('type error')
        # array can recieve both, no verification needed
        

# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #
# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

variables={}
class Eval(Visitor):

  def __init__(self):
    self.test=0  
  
  def visit_program(self,var):
    var.cmmds.accept(self)

  def visit_commands(self,var):
    var.cmmd.accept(self)
    if (var.cmmds!=None):
      var.cmmds.accept(self)

  def visit_command(self,var):
    var.cmmd.accept(self)

  def visit_attribution(self,var):
    result=var.expr.accept(self)
    if (var.index!=None):
      index=var.index.accept(self)
      if var.id not in variables:
        variables[var.id]={}
      variables[var.id][index]=result
    else:
      variables[var.id]=result

  # ----------------------------------------------------- #

  def visit_ifelse(self, i):
    if(i.expr1.accept(self) == i.expr2.accept(self)):
      if i.cmmdif!=None:
        i.cmmdif.accept(self)
    else:
      if i.cmmdelse!=None:
        i.cmmdelse.accept(self)

  def visit_while(self, i):
    while (i.expr1.accept(self) == i.expr2.accept(self)):
        i.cmmds.accept(self)

  # ----------------------------------------------------- #
  # Other important functions
  
  def visit_id(self,i):
    if i.value not in variables:
      raise AssertionError('id uninitialized')
    if (i.index!=None):
      index = i.index.accept(self)
      return variables[i.value][index]
    return variables[i.value]
  
  def visit_string(self,var):
    value = var.value[1:-1]
    return value
  
  def visit_compounds(self,number):
    value = str(number.simple)
    ones = value.count('wan')
    twos = value.count('tu')
    fives = value.count('luka')
    twentys = value.count('mute')
    hundreds = value.count('ale')
    trueNumber = ones + twos*2 + fives*5 + twentys*20 + hundreds*100
    if (number.compounds!=None):
      trueNumber += number.compounds.accept(self)
    return trueNumber*number.neg

  def visit_print(self,var):
    value = var.value.accept(self)
    if type(value) != int and type(value) != dict:
      value = value.replace("\\n", "\n") # due to problems with encoding
    print(value, end=" ")

  def visit_input(self,i):
    inp = input()
    if ST[i.id] == "int":
      if inp.isnumeric() == False:
          raise AssertionError('String in int variable')
      inp = int(inp)
    variables[i.id] = inp

  # ----------------------------------------------------- #
  # arithmetic operations

  def visit_add(self,add):
    return add.left.accept(self)+add.right.accept(self)
  def visit_sub(self,add):
    return add.left.accept(self)-add.right.accept(self)
  def visit_mul(self,add):
    return add.left.accept(self)*add.right.accept(self)
  def visit_div(self,add):
    return add.left.accept(self)/add.right.accept(self)


# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #
#                                                actual code                                                  #
# -=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- #

# Pre coded snippets, avaliable in the ipynb 
simpleTesting = "nanpa [_nanpa_wan] nanpa [_nanpa_tu] nanpa [_nanpa_tu_wan] [_nanpa_wan] sama luka wan [_nanpa_tu] sama tu [_nanpa_tu_wan] sama [_nanpa_wan] en [_nanpa_tu] toki [_nanpa_tu_wan]"
testArray = "kulupu [_kulupu] [_kulupu] (wan) sama luka wan [_kulupu] (tu) sama tu [_kulupu] (wan tu) sama [_kulupu] (tu) en [_kulupu] (wan) toki [_kulupu]"
testString = "nimi [_kulupu] nimi [_nanpa] nimi [_kulupu_nanpa] [_kulupu] sama \"kulupu\" [_nanpa] sama \"nanpa\" [_kulupu_nanpa] sama [_kulupu] en \" \" en [_nanpa] toki [_kulupu_nanpa]"
testIfsWhiles = "nanpa [_lete] nanpa [_luka_sike] [_lete] sama wan [_luka_sike] sama wan awen la ([_lete] sama sama wan) ni la ([_luka_sike] sama sama luka luka) ni [_lete] sama tu ante la toki [_luka_sike] [_luka_sike] sama [_luka_sike] en wan pini pini"
testInput = "nanpa [_nanpa] nimi [_sitelen] toki \"input a number\" kute [_nanpa] toki \"\\n\" toki [_nanpa] toki \"\\ninput a string\" kute [_sitelen] toki \"\\n\" toki [_sitelen]"

# makes them global (hopefully)
variables={} 
ST={}

def run_code(codeString):
  variables={} # resets the variables
  ST={} # resets the symbol table
  
  print("")
  lexy=lexer.lex(codeString)
  arvore=parser.parse(lexy)
  arvore.accept(SymbolTable())
  arvore.accept(Decorator())
  arvore.accept(TypeVerifier())
  arvore.accept(Eval())
  print("")

# -------------------------------------------- #

print("")
print("Welcome to the toki pona code interpreter!")
print("If you havent looked at the ipynb notebook, please do so before looking at this!")
print("Type \"help\" for help")
print("Type \"exit\" to exit")
print("")

while True:

  inp = input(">> ")

  if inp == "exit" or inp == "quit":
    break

  elif inp == "help":
    print("Type \"help\" for help (you are here)")
    print("Type \"exit\" or \"quit\" to exit")
    print("Type \"simple\" to run the simplelest addition code")
    print("Type \"array\" to run the array testing code")
    print("Type \"string\" to run the sring testing code")
    print("Type \"if\" to run the if/while testing code")
    print("Type \"input\" to run the input/output testing code")
    print("Type \"custom\" to run your own custom code")

  elif inp == "simple":
    run_code(simpleTesting)
  elif inp == "array":
    run_code(testArray)
  elif inp == "string":
    run_code(testString)
  elif inp == "if":
    run_code(testIfsWhiles)
  elif inp == "input":
    run_code(testInput)

  elif inp == "custom":
     # this will take a txt, turn it into a string, and run it
    print("Type the name of the file you want to run")
    print("Example: \"codes\guessingGame.txt\"")
    inp = input(">> ")
    file_dir = os.path.dirname(os.path.realpath('__file__'))
    file_name = os.path.join(file_dir, inp)
    try:
      f = open(file_name, "r")
      f.close()
    except:
      print("File not found")
      break
    f = open(file_name, "r")
    print("File found! Running...")
    run_code(f.read())
    f.close()

  else:
    print("Command not found")

print("Goodbye! \n")