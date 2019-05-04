#!/usr/bin/env python3

# Despoina Kotsidou       am:2475	cse32475
# Anastasia Monastiridou  am:2488	cse32488

import sys
file_to_compile = ' '
firsttime   = 0
endfile     = 0
line        = 0

#############################
#                           #
#       TOKEN TYPES         #
#                           #
#############################
PROGR       = 1
ENDPROG     = 2
DECLAR      = 3
FUNC        = 4
ENDFUNC     = 5 
IN          = 6
INOUT       = 7
INANDOUT    = 8

###        STATEMENTS         ###
IF          = 9
WHILE       = 10
DOWHILE     = 11
LOOP        = 12
EXIT        = 13
FORCASE     = 14
INCASE      = 15
RETURN      = 16
PRINT       = 17
INPUT       = 18
#################################

ENDWHILE    = 19
WHEN        = 20
DEFAULT     = 21
ENDDEFAULT  = 22
ENDFORCASE  = 23
ENDIF       = 24
ENDINCASE   = 25
ELSE        = 26
ENDLOOP     = 27
THEN        = 28
OR          = 29
AND         = 30
NOT         = 31

###########  SYMBOLS  ###########
LEFTPARENTH = 32
RIGHTPARENTH= 33
LEFTBRACK   = 34
RIGHTBRACK  = 35
EQUALS      = 36
LESS        = 37
BIGGER      = 38
DIFF        = 39
LESSEQ      = 40
BIGEQ       = 41
PLUS        = 42
MINUS       = 43
TIMES       = 44
DIV         = 45
SEMICOL     = 46
COMMA       = 47
COLON       = 48
ASSIGN      = 49
ENDDOWHILE  = 50

ID          = 51
NUMBER      = 52

class Token: #Class for defining token, type of "word" found from lex  and used from the syntax analyser
    def __init__(self, mylist1, typ, lin):  
        self.mylist1= mylist1  #list of the current word being in process when lex is done 
        self.typ    = typ #the "type" of word found from lex
        self.lin    = lin #current line of file being compiled 
class Quad:
    def __init__(self, label, op, a, b, z):
        self.label = label
        self.op = op
        self.a  = a
        self.b  = b
        self.z  = z

token       = '' #we will keep the token's value here
quadList    = []
temps       = 0
nextQ = 0
program_name = ''

def nextQuad():
    return nextQ

def genQuad(op, x, y, z):
    global nextQ
    print (nextQ)
    newQuad = Quad(nextQ, op, x, y, z)
    quadList.append(newQuad)
    nextQ += 1

def newTemp():
    global temps
    newTemp = 'T_' + str(temps)
    temps += 1
    #to DO
    return newTemp

def emptylist():
    return list()

def makelist(x):
    newlist = list()
    newlist.append(x) 
    return newlist

def merge (list1, list2):
    return (list1+ list2)

def backpatch(listToFill, z):
    global quadList
    for quad in listToFill:
        quadList[quad].z = z

def printWHAT():
    print(quadList[0].op)

def writeToFile():
    global quadList
    for i in quadList:
      print(str(i.label) + ' ' + str(i.op) + ' ' +  str(i.a) + ' ' + str(i.b) + ' ' + str(i.z))

########################################################
#                                                      #
#                 SYNTAX ANALYSER                      #
#                                                      #                
########################################################

#Implementation of the grammatical model of the language "Starlet".
#The program exits if a syntax error has been found, showing the user the type of error and the line of error occurance.

def program(): #The begining of the syntax analyser.
    if token.typ == PROGR:
        lex()
        program_name = token.mylist1
        genQuad('begin_block', program_name, "_", "_")
        if token.typ == ID:
            lex()
            block()
            if token.typ == ENDPROG:
                genQuad('end_program', program_name, "_", "_")
                writeToFile()
                print("****** Congratulations ******\nYour code has been compiled without errors. ")
            else:
                print('File: ', file_to_compile )
                print ("ERROR near ", token.mylist1)
                print ("line: ", token.lin - 1)
                print ("ERROR: ' endprogram ' expected")
                exit(0)
        else:
            print('File: ', file_to_compile )
            print ("ERROR near line", token.lin - 1)
            print ("ERROR: ' ID ' expected")
            exit(0)
    else:
        print('File: ', file_to_compile )
        print ("ERROR near line", token.lin)
        print ("' program ' expected")
        exit(0)

def block():
    if token.typ == DECLAR:
        declaration()
    if token.typ == FUNC:
        subprograms()
    statements()

def declaration():
    while token.typ == DECLAR:
        lex()
        varlist()
        if token.typ == SEMICOL:
            lex()
        elif token.typ == ID:
            print("ERROR near line", token.lin - 1)
            print("ERROR: ' , ' expected")
            exit(0)
        else:
            print('File: ', file_to_compile )
            print ("ERROR near line", token.lin - 1)
            print ("ERROR: ' ; ' expected")  
            exit(0)   

def varlist():
    if token.typ == ID:
        lex()
        while token.typ == COMMA:
            lex()
            if token.typ == ID:
                lex()
            else:
                print('File: ', file_to_compile )
                print("ERROR near line", token.lin - 1)
                print("ERROR: ' ID ' expected")
                exit(0)
    
def subprograms():
    while token.typ == FUNC:
        subprogram()

def subprogram():
    if token.typ == FUNC:
        lex()
        if token.typ == ID:
            lex()
            funcbody()
            if token.typ == ENDFUNC:
                lex()
            elif token.typ>1 and token.typ<50:
                print ("ERROR near line", token.lin - 1)
                print("Syntax error")
                exit(0)
            else:
                print('File: ', file_to_compile )
                print ("ERROR near line", token.lin - 1)
                print("' endfunction ' missing")
                exit(0)
        else:
            print('File: ', file_to_compile )
            print ("ERROR near line", token.lin - 1)
            print("' function's ID ' missing ")
            exit(0)
        

def funcbody():
    formalpars()
    block()

def formalpars():
    if token.typ == LEFTPARENTH:
        lex()
        formalparlist()
        if token.typ == RIGHTPARENTH:
            lex()
        else:
            print('File: ', file_to_compile )
            print ("ERROR near line", token.lin - 1)
            print ("ERROR: ' in/inout/inandout id ' expected")
            exit(0)
    else:
        print('File: ', file_to_compile )
        print ("ERROR near line", token.lin - 1)
        print ("ERROR: ' (  ) ' expected")
        exit(0)


def formalparlist():
    if token.typ == IN or token.typ == INOUT or token.typ == INANDOUT:
        formalparitem()
        if token.typ == IN or token.typ == INOUT or token.typ == INANDOUT:
            print('File: ', file_to_compile )
            print ("ERROR near line", token.lin - 1)
            print ("ERROR: ' , ' missing")
            exit(0)
        while token.typ == COMMA:
            lex()
            formalparitem()
    elif not(token.typ == RIGHTPARENTH):
        print('File: ', file_to_compile )
        print ("ERROR near line", token.lin - 1)
        print ("ERROR: ' in/inout/inandout ' expected")
        exit(0)

def formalparitem():
    if token.typ == IN:
        lex()
        if token.typ == ID:
            lex()
        else:
            print('File: ', file_to_compile )
            print ("ERROR near line", token.lin - 1)
            print ("ERROR: After in, ID expected")
            exit(0)
    elif token.typ == INOUT:
        lex()
        if token.typ == ID:
            lex()
        else:
            print('File: ', file_to_compile )
            print ("ERROR near line", token.lin - 1)
            print ("ERROR: After inout, ID expected")
            exit(0)
    elif token.typ == INANDOUT:
        lex()
        if token.typ == ID:
            lex()
        else:
            print('File: ', file_to_compile )
            print ("ERROR near line", token.lin - 1)
            print ("ERROR: After inandout, ID expected")
            exit(0)
    else:
        print('File: ', file_to_compile )
        print ("ERROR near line", token.lin - 1)
        print ("ERROR: in/inout/inandout id expected")
        exit(0)

def statements():
    statement()
    if ((token.typ > 8 and token.typ < 19) or token.typ == ID ):
        print('File: ', file_to_compile )
        print ("ERROR near line", token.lin - 1)
        print ("' ; ' expected ")
        print ("<statements>::= <statement> (;<statement> )* ")
        exit(0)
    while token.typ == SEMICOL:
        lex()
        statement()

def statement():
    if token.typ == ID:
        assignmentStat()
    elif token.typ == IF:
        ifStat()
    elif token.typ == WHILE:
        whileStat()
    elif token.typ == DOWHILE:
        doWhileStat()
    elif token.typ == LOOP:
        loopStat()
    elif token.typ == EXIT:
        exitStat()
    elif token.typ == FORCASE:
        forcaseStat()
    elif token.typ == INCASE:
        incaseStat()
    elif token.typ == RETURN:
        returnStat()
    elif token.typ == INPUT:
        inputStat()
    elif token.typ == PRINT:
        printStat()
    else:
        print()

def assignmentStat():
    if token.typ == ID:
        parid = token.mylist1
        lex()
        if token.typ == ASSIGN:
            lex()
            exp = expression()
            genQuad(':=', exp, '_', parid)
        else:
            print('File: ', file_to_compile)
            print ("ERROR near line", token.lin - 1)
            print(" ' := ' expected")
            exit(0)
    else:
        print('File: ', file_to_compile)
        print ("ERROR near line", token.lin - 1)
        print(" ' ID ' expected")
        exit(0)
    return exp

def ifStat():
    if token.typ == IF:
        lex()
        if token.typ == LEFTPARENTH:
            lex()
            (Btrue, Bfalse) = condition()
            if token.typ == RIGHTPARENTH:
                lex()
                if token.typ == THEN:
                    backpatch(Btrue, nextQuad())
                    lex()
                    statements()
                    ifList = makelist(nextQuad())
                    genQuad('jump', '_', '_', '_')
                    backpatch(Bfalse, nextQuad())
                    elsepart()
                    backpatch(ifList, nextQuad())
                    if token.typ == ENDIF:
                        lex()
                    else:
                        print('File: ', file_to_compile )
                        print ("ERROR near line", token.lin - 1)
                        print(" ' endif ' expected")
                        print("if (<contition>) then <statements> <elsepart> endif")
                        exit(0)
                else:
                    print('File: ', file_to_compile )
                    print ("ERROR near line", token.lin - 1)
                    print(" ' then ' expected")
                    print("if (<contition>) then <statements> <elsepart> endif")
                    exit(0)  
            else:
                print('File: ', file_to_compile)
                print ("ERROR near line", token.lin - 1)
                print(" ' ) ' expected")
                print("\nif (<contition>) then <statements> <elsepart> endif")
                exit(0)  
        else:
            print('File: ', file_to_compile )
            print ("ERROR near line", token.lin - 1)
            print(" ' ( ' expected")
            print("\nif (<contition>) \nthen <statements> \n<elsepart> \nendif")
            exit(0)

def elsepart():
    if token.typ == ELSE:
        lex()
        statements()

def whileStat():
    if token.typ == WHILE:
        lex()
        Bquad = nextQuad()
        if token.typ == LEFTPARENTH:
            lex()
            (Btrue, Bfalse) = condition()
            if token.typ == RIGHTPARENTH:
                lex()
                backpatch(Btrue, nextQuad())
                statements()
                genQuad('jump', '_', '_', Bquad)
                backpatch(Bfalse, nextQuad())
                if token.typ == ENDWHILE:
                    lex()
                else:
                    print('File: ', file_to_compile )
                    print ("ERROR near line", token.lin - 1)
                    print(" ' endwhile ' expected")
                    exit(0)
            else:
                print('File: ', file_to_compile)
                print ("ERROR near line", token.lin - 1)
                print(" ' ) ' expected")  
                exit(0)    
        else:
            print('File: ', file_to_compile )
            print ("ERROR near line", token.lin - 1)
            print(" ' ( ' expected")
            exit(0)
    else:
        print('File: ', file_to_compile )
        print ("ERROR near line", token.lin - 1)
        print (" ' while ' expected")
        exit(0)

def doWhileStat():
    if token.typ == DOWHILE:
        lex()
        Bquad = nextQuad()
        statements()
        if token.typ == ENDDOWHILE:
            lex()
            if token.typ == LEFTPARENTH:
                lex()
                (Ctrue, Cfalse) = condition()
                backpatch(Cfalse, Bquad)
                backpatch(Ctrue, nextQuad())
                if token.typ == RIGHTPARENTH:
                    lex()
                else:
                    print('File: ', file_to_compile )
                    print ("ERROR near line", token.lin - 1)
                    print (" ' ) ' expected")
                    exit(0)
            else:
                print('File: ', file_to_compile )
                print ("ERROR near line", token.lin - 1)
                print (" ' ( ' expected")
                exit(0)
        else:
            print('File: ', file_to_compile )
            print ("ERROR near line", token.lin - 1)
            print (" ' enddowhile ' expected")
            exit(0)
    else:
        print('File: ', file_to_compile )
        print ("ERROR near line", token.lin - 1)
        print (" ' dowhile ' expected")
        exit(0)


def loopStat():
    if token.typ == LOOP:
        lex()
        statements()
        if token.typ == ENDLOOP:
            lex()
        else:
            print('File: ', file_to_compile )
            print ("ERROR near line", token.lin - 1)
            print ("ERROR: ' endloop ' expected")
            exit(0)
    else:
        print('File: ', file_to_compile )
        print ("ERROR near line", token.lin - 1)
        print ("ERROR: ' loop ' expected")
        exit(0)

def exitStat():
    if token.typ == EXIT:
        lex()
        genQuad('jump', '_', '_', '_')
    else:
        print('File: ', file_to_compile )
        print ("ERROR near line", token.lin - 1)
        print ("ERROR: ' exit ' expected")
        exit(0)

def forcaseStat():
    if token.typ == FORCASE:
        lex()
        temp = newTemp()
        exitList = emptylist()
        flagquad = nextQuad()
        genQuad(':=', '0', '_', temp)
        while token.typ == WHEN:
            lex()
            if token.typ == LEFTPARENTH:
                lex()
                (Ctrue, Cfalse) = condition()
                if token.typ == RIGHTPARENTH:
                    lex()
                    if token.typ == COLON:
                        lex()
                        backpatch(Ctrue, nextQuad())
                        genQuad(':=', '1', '_', temp)
                        statements()
                        tmp = makelist(nextQuad())
                        genQuad('jump', '_', '_', '_')
                        exitList = merge(exitList, tmp)
                        backpatch(Cfalse, nextQuad())
                    else:
                        print('File: ', file_to_compile )
                        print ("ERROR near line", token.lin - 1)
                        print ("ERROR AFTER ' when ': ' : ' expected")
                        print (" when (<condition>) : <statements>")
                        exit(0)
                else:
                    print('File: ', file_to_compile )
                    print ("ERROR near line", token.lin - 1)
                    print ("ERROR AFTER ' when ': ' ) ' expected")
                    print (" when (<condition>) : <statements>")
                    exit(0)
            else:
                print('File: ', file_to_compile )
                print ("ERROR near line", token.lin - 1)
                print ("ERROR AFTER ' when ': ' ( ' expected")
                print (" when (<condition>) : <statements>")
                exit(0)
        if token.typ == DEFAULT:
            lex()
            if token.typ == COLON:
                lex()
                statements()
                genQuad('=', '0', temp, flagquad)
                if token.typ == ENDDEFAULT:
                    lex()
                    if token.typ == ENDFORCASE:
                        backpatch(exitList, nextQuad())
                        lex()
                    else:
                        print('File: ', file_to_compile )
                        print ("ERROR near line", token.lin - 1)
                        print ("ERROR: ' endforcase ' expected")
                        exit(0)
                else:
                    print('File: ', file_to_compile )
                    print ("ERROR near line", token.lin - 1)
                    print ("ERROR: ' enddefault ' expected")   
                    exit(0)
            else:
                print('File: ', file_to_compile )
                print ("ERROR near line", token.lin - 1)
                print ("ERROR: ' : ' expected")
                exit(0)
        else:
            print('File: ', file_to_compile )
            print ("ERROR near line", token.lin - 1)
            print ("ERROR: ' default ' expected")
            exit(0)

def incaseStat():
    if token.typ == INCASE:
        lex()
        temp = newTemp()
        flagquad = nextQuad()
        genQuad(':=', '0', '_', temp)
        while token.typ == WHEN:
            lex()
        
            if token.typ == LEFTPARENTH:
                 lex()
                 (Ctrue, Cfalse) = condition()
                 if token.typ == RIGHTPARENTH:
                    lex()
                    if token.typ == COLON:
                        lex()
                        backpatch(Ctrue, nextQuad())
                        genQuad(':=', 1, '_', temp)
                        statements()
                        backpatch(Cfalse, nextQuad())
                    else:
                        print('File: ', file_to_compile )
                        print ("ERROR near line", token.lin - 1)
                        print ("ERROR AFTER ' when ': ' : ' expected")
                        print (" when (<condition>) : <statements>")
                        exit(0)
                 else:
                    print('File: ', file_to_compile )
                    print ("ERROR near line", token.lin - 1)
                    print ("ERROR AFTER ' when ': ' ) ' expected")
                    print (" when (<condition>) : <statements>")
                    exit(0)
            else:
                 print('File: ', file_to_compile )
                 print ("ERROR near line", token.lin - 1)
                 print ("ERROR AFTER ' when ': ' ( ' expected")
                 print (" when (<condition>) : <statements>")
                 exit(0)
        if token.typ == ENDINCASE:
            lex()
            genQuad('=', '1', temp, flagquad)
       	else:
            print('File: ', file_to_compile )
            print ("ERROR near line", token.lin - 1)
            print ("ERROR: ' endincase ' expected")
            exit(0)

def returnStat():   # called
    lex()           # if token == return
    exp = expression()
    genQuad('retv', '_', '_', exp,)

def printStat():    # called
    lex()           # if token == print
    exp = expression()
    genQuad('out', '_', '_', exp)

def inputStat():
    if token.typ == INPUT:
        lex()
        genQuad('inp', '_', '_', token.mylist1)
        if token.typ == ID:
        	lex()
        else:
            print('File: ', file_to_compile )
            print ("ERROR near line", token.lin - 1)
            print ("ERROR: ID expected")
            exit(0)
    else:
        print('File: ', file_to_compile )
        print ("ERROR near line", token.lin - 1)
        print ("ERROR: input expected")
        exit(0)

def actualpars():
    lex()           # mpainei an exei (
    actualparlist()
    if token.typ == RIGHTPARENTH:
    	lex()
    else:
        print ("ERROR near line", token.lin - 1)
        print ("ERROR ) expected")
        exit(0)

def actualparlist():
    if token.typ == IN or token.typ == INOUT or token.typ == INANDOUT:
        actualparitem()
        while token.typ == COMMA:
            lex()
            actualparitem()
            
def actualparitem():
    if token.typ == IN:
        lex()
        retval = expression()
        genQuad('par', retval, 'CV', '_')
    elif token.typ == INOUT:
        lex()
        retval = token.mylist1
        genQuad('par', retval, 'REF', '_')
        if token.typ == ID:
        	lex()
        else:
            print('File: ', file_to_compile )
            print ("ERROR near line", token.lin - 1)
            print ("ERROR: After inout, ID expected")
            exit(0)
    elif token.typ == INANDOUT:
        lex()
        retval = token.mylist1
        genQuad('par', retval, 'CP', '_')
        if token.typ == ID:
        	lex()
        else:
            print('File: ', file_to_compile )
            print ("ERROR near line", token.lin - 1)
            print ("ERROR: After inandout, ID expected")
            exit(0)
    else:
        print('File: ', file_to_compile )
        print ("ERROR near line", token.lin - 1)
        print ("ERROR: in/inout/inandout expected")
        exit(0)
    return retval

def condition():
    (Qtrue, Qfalse) = boolterm()
    while token.typ == OR:
        lex()
        backpatch(Qfalse, nextQuad())
        (R2true, R2false) = boolterm()
        Qtrue = merge(Qtrue, R2true)
        Qfalse = R2false
    return (Qtrue, Qfalse)

def boolterm():
    (Qtrue, Qfalse) = boolfactor()
    while token.typ == AND:
        lex()
        backpatch(Qtrue, nextQuad())
        (R2true, R2false) = boolfactor()
        Qfalse = merge(Qfalse, R2false)
        Qtrue = R2true
    return (Qtrue, Qfalse)

def boolfactor():
    retval = ""
    if token.typ == NOT:
        lex()
        if token.typ == LEFTBRACK:
            lex()
            retval = condition()
            if token.typ == RIGHTBRACK:
            	lex()
            else:
                print('File: ', file_to_compile )
                print ("ERROR near line", token.lin - 1)
                print ("ERROR: ] expected")
                exit(0)   
        else:
            print('File: ', file_to_compile )
            print ("ERROR near line", token.lin - 1)
            print ("ERROR: [ expected")
            exit(0)
    elif token.typ == LEFTBRACK:
            lex()
            retval = condition()
            if not(token.typ == RIGHTBRACK):
                print('File: ', file_to_compile )
                print ("ERROR near line", token.lin - 1)
                print ("ERROR: ] expected")
                exit(0)
            lex()
    else:
        exp1 = expression()
        op 	= relationOper()
        exp2 = expression()
        Btrue = makelist(nextQuad())
        genQuad(op, exp1, exp2, '_')
        Bfalse = makelist(nextQuad())
        genQuad('jump', '_', '_', '_')
        retval = (Btrue, Bfalse)
    return retval
       
def expression():	
    optionalSign()
    term1 = term()
    while (token.typ == PLUS) or (token.typ == MINUS):
        op         = addOper()
        term2 	= term()
        tempLab = newTemp()
        genQuad(op, term1, term2, tempLab)
        term1 	= tempLab
    return term1

def term():
    factor1 = factor()
    while (token.typ == TIMES) or (token.typ == DIV):
        op         = mulOper()
        factor2	= factor()
        tempLab	= newTemp()
        genQuad(op, factor1, factor2, tempLab)
        factor1 = tempLab
    return factor1

def factor():
    if token.typ == LEFTPARENTH:        
        lex()
        retval = expression()
        if not(token.typ == RIGHTPARENTH):
            print('File: ', file_to_compile )
            print ("ERROR near line", token.lin - 1)
            print ("ERROR: ) expected") 
            exit(0) 
        lex()   
    elif token.typ == ID:
        parid = token.mylist1
        lex()
        partail = idtail()        # EDW kati paizei 
        if (partail == ""):
            retval = parid
        else:
            genQuad('call', parid, '_', '_')
            retval = partail
    elif token.typ == NUMBER:	# na prosthesw isws arnitikous/thetikous
        retval = token.mylist1
        lex()
    else:
        print ("ERROR near line", token.lin - 1)
        print("ERROR (factor):  expected")
        exit(0)
    return retval

def idtail():
    if token.typ == LEFTPARENTH:
        return actualpars()

def relationOper():
    if not((token.typ == EQUALS) or (token.typ == LESSEQ) or (token.typ == BIGEQ) or (token.typ == BIGGER) or (token.typ == LESS) or (token.typ == DIFF)):
        print('File: ', file_to_compile )
        print ("ERROR near line", token.lin - 1)
        print("ERROR: <relational oper> expected")
        exit(0)
    op = token.mylist1
    lex()
    return op

def addOper():      # called if token + or -
    op = token.mylist1
    lex()
    return op

def mulOper():      # called if token * or /
    op = token.mylist1
    lex()
    return op

def optionalSign():
    if  (token.typ == PLUS) or (token.typ == MINUS):
        return addOper()

###  Setting the word type by checking if the word is a reserved word, a reserved symbol, number or a plain id.

def setWordType(mylist):

    if (mylist.isdigit()):
        return NUMBER

    if (mylist.isalpha()):
        if mylist == 'program':
            return PROGR
        elif mylist == 'endprogram':
            return ENDPROG
        elif mylist == 'declare':
            return DECLAR
        elif mylist == 'function':
            return FUNC 
        elif mylist == 'endfunction':
            return ENDFUNC
        elif mylist == 'in':
            return IN 
        elif mylist == 'inout':
            return INOUT
        elif mylist == 'inandout':
            return INANDOUT
        elif mylist == 'if':
            return IF
        elif mylist == 'then':
            return THEN
        elif mylist == 'endif':
            return ENDIF
        elif mylist == 'else':
            return ELSE
        elif mylist == 'while':
            return WHILE
        elif mylist == 'endwhile':
            return ENDWHILE
        elif mylist == 'dowhile':
            return DOWHILE
        elif mylist == 'enddowhile':
            return ENDDOWHILE
        elif mylist == 'loop':
            return LOOP
        elif mylist == 'endloop':
            return ENDLOOP
        elif mylist == 'exit':
            return EXIT
        elif mylist == 'forcase':
            return FORCASE
        elif mylist == 'when':
            return WHEN
        elif mylist == 'default':
            return DEFAULT
        elif mylist == 'enddefault':
            return ENDDEFAULT
        elif mylist == 'endforcase':
            return ENDFORCASE
        elif mylist == 'incase':
            return INCASE
        elif mylist == 'endincase':
            return ENDINCASE
        elif mylist == 'return':
            return RETURN
        elif mylist == 'print':
            return PRINT
        elif mylist == 'input':
            return INPUT
        elif mylist == 'or':
            return OR
        elif mylist == 'and':
            return AND
        elif mylist == 'not':
            return NOT
        else:
            return ID

    if mylist == '(':
        return LEFTPARENTH
    elif mylist == ')':
        return RIGHTPARENTH
    elif mylist == '[':
        return LEFTBRACK
    elif mylist == ']':
        return RIGHTBRACK
    elif mylist == '=':
        return EQUALS
    elif mylist == '<':
        return LESS
    elif mylist == '>':
        return BIGGER
    elif mylist == '<>':
        return DIFF
    elif mylist == '<=':
        return LESSEQ
    elif mylist == '>=':
        return BIGEQ
    elif mylist == '+':
        return PLUS
    elif mylist == '-':
        return MINUS
    elif mylist == '*':
        return TIMES
    elif mylist == '/':
        return DIV
    elif mylist == ';':
        return SEMICOL
    elif mylist == ':':
        return COLON
    elif mylist == ':=':
        return ASSIGN
    elif mylist == ',':
        return COMMA
    else:
        return ID

########################################################
#                                                      #
#                 LEXICAL ANALYSER                     #
#                                                      #                
########################################################

def lex():

    my_list = [] #List of found "word"
    state   = 0
    recog   = -1
    error   = -2
    goback  = 0

    if len(sys.argv) != 2:  #The arguments need to consist of this file (MyCompiler.py) and a file to compile.
        print ("I need a file to compile")
        exit(0)

    global endfile
    global file_to_compile
    global file
    global firsttime
    global line
    
    if firsttime==0:        	#The file needs to be opened once. 
        file_to_compile = sys.argv[1]	#This variable changes value only once, so as the file.
        file = open(file_to_compile, 'r')
        firsttime = 1

    while (state!=recog) and (state!=error): # Keep looping if the finite automaton hasn't reached it's final state or, if no errors have occured.

        symbol = file.read(1)   # Read one char per loop.

        if symbol == '\n':      # Counter for the number of lines in the .stl file.
            line = line + 1

        my_list.append(symbol) # Add char in the list of "word".
        
        ## Begining of the finite automaton, to determine if the "word" is acceptable. Stops once a word is found, or an error has occured. 

        if state == 0:         # First state of the finite automaton.
            if symbol.isalpha():
                state = 1
            elif symbol.isdigit():
                state = 2
            elif symbol == '<':
                state = 3
            elif symbol == '>':
                state = 4
            elif symbol == ':':
                state = 5
            elif symbol in ('+', '-', '=', '*', ',', ';', '(', ')', '[', ']'):
                state = recog
            elif symbol == '/':
                state = 6
            elif symbol == '':   #Checking if the EOF (end of file) has been reached.
                endfile = 1
                state = recog
            elif symbol.isspace(): #Delete unwanted spaces from the list.
                del my_list[-1]
            else:
                state = error
                print("ERROR: Invalid symbol near line: ", line)
                exit(0)
        elif state == 1:    # ID
            if not((symbol.isalpha()) or (symbol.isdigit())):   # word
                if len(my_list) > 30:
                    my_list = my_list[:31]
                state = recog
                goback = 1	# seek back
        elif state == 2:    # number
            if not (symbol.isdigit()):
                state = recog
                goback = 1	# seek back
        elif state == 3:    # <= , <> , <
            if not(symbol in ('=', '>')):
                goback = 1	# seek back
            state = recog
        elif state == 4:    # >= , >
            if not(symbol == '='):
                goback = 1;	# seek back
            state = recog
        elif state == 5:    # := , :
            if not(symbol == '='):
                goback = 1
                #back
            state = recog
        elif state == 6:    # // , /* , /
            if symbol == '/' :
                state = 7
            elif symbol == '*':
                state = 8
            else:
                state = recog
                goback = 1
        elif state == 7:    # one line comment //
            if symbol == '\n':
                state = 0
                my_list = []
        elif state == 8:    # comments /*
            if symbol == '*':
                state = 9 
            elif symbol == '':  # EOF 
                print("ERROR in comments: ' */ ' missing")
                exit(0)        
        elif state == 9:    # end comments */
            if symbol == '/':
                state = 0
                my_list = []
            else:
                state = 8

    if goback:          # Deletion of last char from my_list and unreading a char from the file, if the char was unneeded for the current word. (ex: Begining of some other word)
        del my_list[-1]
        if not(endfile):
            file.seek(file.tell() - 1)

    my_list = ''.join(my_list)  #Joining all the chars into the list.
                                
    if my_list.isdigit():   #In case a number was found, check if it's acceptable. Acceptable numbers : lesser than 32767.
        if (int(my_list) > 32767):
            print("ERROR: Invalid number near line: ", line - 1)
            print("Acceptable numbers: 0 to 32767")
            exit(0)

    typ = setWordType(my_list)  # Set the type of word found (now known as token), which is held in the list.
    if state == recog: # Set all token parameters only if the automaton has reached it's finite state (a word has been found).
        global token
        token = Token(my_list, typ, line)
 

lex()     #Call the lexical analyser to jumpstart the process. After the first word has been found,
program() #the syntax analyser is called to continue. lex() is called when needed another word in the syntax
          #analyser. The syntax analyser checks if the grammar of the language is correct.
