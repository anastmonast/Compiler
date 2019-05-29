#!/usr/bin/env python3

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


################        GLOBAL VARIABLES        ###############

token       = '' #we will keep the token's value here
quadList    = [] # Quad List
temps       = 0  # How many temporary variables
nextQ       = 0     # Points to next Quad
varToDec    = [] # List of variables to declare for .c file
scopeList   = []

exitList        = []    # exit from loop
startLoopQuad   = []
endLoopQuad     = []

namesOfFunction  = [] # keeps name of each function
i    = 0


###########        classes for TABLE      #############

class Scope:
    def __init__(self, entPoint, nestLev, scoPoint):
        self.entPoint     = entPoint
        self.nestLev    = nestLev
        self.scoPoint    = scoPoint
        self.currOff    = 12

    def getOffset(self):
        retval = self.currOff
        self.currOff += 4
        return retval

class Argument:
    def __init__(self, parMode, argPoint):
        self.parMode     = parMode
        self.argPoint    = argPoint

class Entity(object):
    def __init__(self, entName, entType, entPoint):
        self.entName     = entName
        self.entType    = entType
        self.entPoint    = entPoint

class Variable(Entity):
    def __init__(self, name, vOffset):
        super(Variable, self).__init__(name, 'VAR', None)
        self.name     = name
        self.vOffset     = vOffset

class Function(Entity):
    def __init__(self, name, fQuad, fArg, fFramelen):
        super(Function, self).__init__(name, 'FUNC', None)
        self.name     = name
        self.fQuad     = fQuad
        self.fArg    = fArg
        self.fFramelen = fFramelen

class Const(Entity):
    def __init__(self, val):
        super(Const, self).__init__(val, 'CON', None)
        self.val = val


class Paramet(Entity):
    def __init__(self, name, parMode, offset):
        super(Paramet, self).__init__(name, 'par', None)
        self.parMode = parMode
        self.offset = offset

class tempVariable(Entity):
    def __init__(self, name, offset):
        super(tempVariable, self).__init__(name, 'TEMP', None)
        self.offset = offset


###########################################################
#                                                          #
#                    SYMBOL TABLE                          #
#                                                          #
###########################################################

def entityInsert(newEntity):
    scopeList[-1].entPoint.append(newEntity)

def argumentIsert(mode):
    scopeList[-1].entPoint[-1].fArg.append(Argument(mode, None))

def scopeInsert():
    level = scopeList[-1].nestLev + 1
    pScope = scopeList[-1]
    newScope = Scope([], level, pScope)
    scopeList.append(newScope)

def scopeDelete():
    scopeList.pop() 
    return

def searchByType(name, enttype):
    if (len(scopeList)) != 0:
        for i in range(0, len(scopeList)):
            for entity in scopeList[-(i+1)].entPoint:
                if entity.entName == name and entity.entType == enttype:
                    return (entity, i)
def searchByName(name):
    if (len(scopeList)) != 0:
        for i in range(0, len(scopeList)):
            for entity in scopeList[-(i+1)].entPoint:
                if entity.entName == name :
                    return (entity,i)

def addVarEntity(name):
    offset = scopeList[-1].getOffset()
    retval = Variable(name, offset)
    return retval

def addFuncEntity(name, quad):
    retval = Function(name, quad, [], 0)
    return retval

def addParEntity(name, parMode):
    offset = scopeList[-1].getOffset()
    retval = Paramet(name, parMode, offset)
    return retval

def addTempEntity(name):
    offset = scopeList[-1].getOffset()
    retval = tempVariable(name, offset)
    return retval

def fillFramelength():
    if (len(scopeList)) != 0:
        for i in range(0, len(scopeList)):
            for entity in scopeList[-(i+1)].entPoint:
                if entity.entType == 'FUNC':
                    entToFill = entity
                    offset = scopeList[-1].getOffset()
                    entToFill.fFramelen = offset + 4
                    return

def printScopes():
    for scope in scopeList:
        print ("SCOPE ")
        for ent in scope.entPoint:
            print (ent.entName + ent.entType)
            if ent.entType == 'FUNC':
                for i in ent.fArg:
                    print (i.parMode + "  mode")

################################################################

def nextQuad():
    return nextQ

def genQuad(op, x, y, z):
    global nextQ
    newQuad = Quad(nextQ, op, x, y, z)
    quadList.append(newQuad)
    nextQ += 1

def newTemp():
    global temps
    newTemp = 'T_' + str(temps)
    temps += 1
    varToDec.append(newTemp)
    entityInsert(addTempEntity(newTemp))
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

def writeToInt():
    filename = file_to_compile[:-4] + '.int'
    file = open(filename,'w') 
    global quadList
    for quad in quadList:
        file.write(str(quad.label) + ': ' + str(quad.op)+' '+ str(quad.a)+' '+ str(quad.b)+' '+ str(quad.z)+'\n')

    file.close()   

def writeToC():
    cName     = file_to_compile[:-4] + '.c'
    fileForC = open(cName, 'w')
    fileForC.write('#include <stdio.h>\n\n')
    fileForC.write('int main()\n{\n')
    varSize = len(varToDec)
    if (varSize > 0):
        fileForC.write('int ' + varToDec[0] )
        for i in range(1, varSize):
            fileForC.write(', ' + varToDec[i])
    fileForC.write(';\n')
    for quad in quadList:
        fileForC.write('L_' + str(quad.label) + ': ')
        if (quad.op == ':='):
            fileForC.write(str(quad.z) + '=' + str(quad.a) + ';\n')
        elif quad.op == '+' or quad.op == '-' or quad.op == '/' or quad.op == '*':
            fileForC.write(str(quad.z) + '=' + str(quad.a) + str(quad.op) + str(quad.b) + ';\n')
        elif quad.op == '<' or quad.op == '>' or quad.op == '<=' or quad.op == '=' or quad.op == '>=' or quad.op == '<>':
            fileForC.write('if (' + str(quad.a) + str(quad.op) + str(quad.b) + ')' + ' goto ' + 'L_' + str(quad.z) + ';\n')
        elif (quad.op == 'jump'):
            fileForC.write('goto ' + 'L_' + str(quad.z) + ';\n')
        elif(quad.op == 'out'):
            fileForC.write('printf('+str(quad.z)+');\n')
        elif(quad.op == 'retv'):
            fileForC.write('return '+str(quad.z)+';\n')
        elif(quad.op == 'inp'):
            fileForC.write('scanf('+str(quad.z)+');\n')
        else:
            fileForC.write('{}\n')

    fileForC.write('}')
    fileForC.close()


########################################################
#                                                       #
#                    MIPS CODE                            #
#                                                       #
########################################################

def gnlvcode(v):
    (tEntity, entLevel) = searchByName(v)
    currLevel = scopeList[-1].nestLev
    fileForAsm.write('lw $t0, -4($sp)\n')

    for i in range(currLevel - 2, entLevel): # gia endiamesa level
        fileForAsm.write('lw $t0, -4($t0)\n')

    fileForAsm.write('add $t0,$t0-' + str(tEntity.offset) + '\n')

def loadvr(v,r):

    if str(v).isdigit():
        fileForAsm.write ('li $t' + str(r) + ',' + v  + '\n')
    else:
        try:
            entity, entLevel = searchByName(v)
        except:
            printf("Undeclared variable: ", v)
            exit(0)
        currLevel = scopeList[-1].nestLev
        if (entity.entType == 'VAR' and entLevel == 0): # main variable
            fileForAsm.write ('lw $t' + str(r) + ',-' + entity.offset + '($s0)' + '\n')
        elif (entity.entType == 'VAR' and entLevel == currLevel) \
                or (entity.entType == 'par' and entity.parMode == 'CV' and entLevel == currLevel)\
                or (entity.entType == 'TEMP'): # vf = trexon
            fileForAsm.write ('lw $t' + str(r) + ',-' + entity.offset + '($sp)'+ '\n')    
        elif (entity.entType == 'par' and entity.parMode == 'REF' and entLevel == currLevel):
            fileForAsm.write ('lw $t0' + ',-' + entity.offset + '($sp)'+ '\n')
            fileForAsm.write ('lw $t' + str(r) + ',($t0)' + '\n')
        elif (entity.entType == 'VAR' and entLevel < currLevel) \
                or (entity.entType == 'par' and entity.parMode == 'CV' and entLevel < currLevel):
            gnlvcode(v)
            fileForAsm.write ('lw $t' + str(r) + ',($t0)'+ '\n')
        elif (entity.entType == 'par' and entity.parMode == 'REF' and entLevel < currLevel):
            gnlvcode(v)
            fileForAsm.write ('lw $t0,($t0)' + '\n')
            fileForAsm.write ('lw $t' + str(r) +',($t0)\n')
        else:
            print("ERROR 359 kati paizei")
            exit(0)

def storerv(r,v):
    (vEntity, entLevel) = searchByName(v)
    currLev = scopeList[-1].nestLev 

    if vEntity.entType == 'VAR' and entLevel == 0:
        fileForAsm.write('sw $t'+str(r)+',-'+str(vEntity.offset)+'($s0)\n')
    elif (vEntity.entType == 'VAR' and entLevel == currLev) or (vEntity.entType == 'TEMP') or (vEntity.entType == 'par' and vEntity.parMode == 'CV' and entLev==currLev):
        fileForAsm.write('sw $t'+str(r)+',-'+str(vEntity.offset)+'($sp)\n')
    elif vEntity.entType == 'PAR' and vEntity.parMode == 'REF' and entLevel ==currLev:
        fileForAsm.write('lw $t0,-'+str(vEntity.offset)+'($sp)\n')
        fileForAsm.write('sw $t'+str(r)+',($t0)\n')
    elif (v.Entity == 'VAR' or (vEntity.entType == 'par' and vEntity.parMode == 'CV') ) and entLevel<currLev:
        gnlvcode(v)
        fileForAsm.write('sw $t'+str(r)+',($t0)\n')
    elif v.Entity == 'par' and vEntity.parMode == 'REF' and entLevel <currLev:
        gnlvcode(v)
        fileForAsm.write('lw $t0,($t0)\n')
        fileForAsm.write('sw $t'+str(r)+',($t0)\n')
    else:
        printf("error 380")

def mips_code(quad, block_name):
    print("POSES FORES\n")
    global fileForAsm
    cName     = file_to_compile[:-4] + '.asm'
    fileForAsm = open(cName, 'w')

    fileForAsm.write('L_' + str(quad.label) + '\n')
    if (quad.op == 'jump'):
        fileForAsm.write('j L_' + quad.z + '\n')
    elif (quad.op == '==' or quad.op == '<' or quad.op == '>' or quad.op == '<>' or quad.op == '<=' or quad.op == '>='): # == < > <> <= >=
        loadvr(quad.a, 1)
        loadvr(quad.b, 2)
        if quad.op == EQUALS:
            fileForAsm.write('beq,$t1,$t2,' + quad.z + '\n')
        elif quad.op == DIFF:
            fileForAsm.write('bne,$t1,$t2,' + quad.z + '\n')
        elif quad.op == BIGGER:
            fileForAsm.write('bgt,$t1,$t2,' + quad.z + '\n')
        elif quad.op == LESS:
            fileForAsm.write('blt,$t1,$t2,' + quad.z + '\n')
        elif quad.op == BIGEQ:
            fileForAsm.write('bge,$t1,$t2,' + quad.z + '\n')
        elif quad.op == LESSEQ:
            fileForAsm.write('ble,$t1,$t2,' + quad.z + '\n')
        else:
            None
    elif (quad.op == ASSIGN):
        loadvr(quad.a, 1)
        storerv(1, quad.z)
    elif (quad.op == '+' or quad.op == '-' or quad.op == '*' or quad.op == '/'): # + - * /
        loadvr(quad.a, 1)
        loadvr(quad.b, 2)
        if quad.op == PLUS:
            fileForAsm.write('add $t1,$t1,$t2\n')
        elif quad.op == MINUS:
            fileForAsm.write('sub,$t1,$t1,$t2\n')
        elif quad.op == TIMES:
            fileForAsm.write('mul,$t1,$t1,$t2\n')
        elif quad.op == DIV:
            fileForAsm.write('div,$t1,$t1,$t2\n')
        else:
            None
    elif (quad.op == 'out'):
        fileForAsm.write('li $v0,1\n')
        fileForAsm.write('li $a0,' + quad.z + '\n')
        fileForAsm.write('syscall\n')
    elif (quad.op == 'in'):
        fileForAsm.write('li $v0,5\n')
        fileForAsm.write('syscall\n')
    elif (quad.op == 'retv'):
        loadvr(quad.z, 1)
        fileForAsm.write('lw $t0,-8($sp)\n')
        fileForAsm.write('sw $t1,($t0)\n')
    elif (quad.op == 'halt'):
        print()
    elif (quad.op == 'par'):
        if block_name in namesOfFunction:
            i += 1
        else:
           	namesOfFunction.append(block_name)
           	i = 0
        (fentity, fLevel) = searchByName(block_name)
        fileForAsm.write('add $fp,$sp,' + str(fentity.fFramelen)  + '\n')

        if quad.b == 'CV':
            loadvr(quad.a, 0)
            fileForAsm.write('sw $t0,-(12+4'+ str(i) +')($fp)\n' )	
        elif quad.b == 'REF':
        	try:
	        	(tEntity, entLevel) = searchByType(quad.a, 'PAR')
	        	if entLevel == fLevel:
	        		if tEntity.parMode == 'REF': # me anafora stin F
	        			fileForAsm.write('lw $t0,-'+ tEntity.offset +'($sp)\n')
	        			fileForAsm.write('sw $t0,-(12+4'+ str(i) +')($fp)\n' )
	        		else: # ola ta alla(topiki, me timi, proswrini)
	        			fileForAsm.write('add $t0,$sp,-'+ tEntity.offset +'\n')
	        			fileForAsm.write('sw $t0,-(12+4'+ str(i) +')($fp)\n' )
	        	elif entLevel < fLevel:
	        		if tEntity.parMode == 'REF': # me anafora stin F
	        			gnlvcode(quad.a)
	        			fileForAsm.write('lw $t0,($t0)\n')
	        			fileForAsm.write('sw $t0,-(12+4'+ str(i) +')($fp)\n' )
	        		else: # ola ta alla(topiki, me timi, proswrini)
	        			gnlvcode(quad.a)
	        			fileForAsm.write('sw $t0,-(12+4'+ str(i) +')($fp)\n' )
	       	except:
	       		print("ERROR: Can't find parameter: " + quad.a)      	
        elif quad.b == 'RET':
        	fileForAsm.write('add $t0,$sp'+ tEntity.offset +'\n')
        	fileForAsm.write('sw $t0,-8($fp)\n' )
        elif quad.b == 'CP':
        	print()
        else:
        	print()
    elif (quad.op == 'call'):
        (fentity, fLevel) = searchByName(block_name)
        (toCallentity, toCallLevel) = searchByName(quad.a)
        if fLevel == toCallLevel:
            fileForAsm.write('lw $t0,-4($sp)\n')
            fileForAsm.write('sw $t0,-4($fp)\n' )
        elif fLevel < toCallLevel:
            fileForAsm.write('sw $sp,-4($fp)\n' )
        else:
            print()
        fileForAsm.write('add $sp,$sp'+ fentity.fFramelen +'\n')
        fileForAsm.write('jal ' + quad.a + '\n')
        fileForAsm.write('add $sp,$sp-'+ fentity.fFramelen +'\n')
    elif (quad.op == 'begin_block'):
        fileForAsm.write('sw $ra,($sp)\n' )
        if block_name == file_to_compile[:-4]: # main
            None

    elif (quad.op == 'end_block'):
        if block_name == file_to_compile[:-4]:
            None
    else:
        print()


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
            scopeList.append(Scope([], 0, None))
            block()
            if token.typ == ENDPROG:
                genQuad('halt', '_', '_', '_')
                genQuad('end_block', program_name, "_", "_")
                writeToC()
                writeToInt()
                print("\n*********** Congratulations ***********\n\nYour code has been compiled without errors. ")
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
        varToDec.append(token.mylist1)    # add variables to declare to list
        entityInsert(addVarEntity(token.mylist1))
        lex()                            
        while token.typ == COMMA:
            lex()
            if token.typ == ID:
                varToDec.append(token.mylist1)
                entityInsert(addVarEntity(token.mylist1))
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
        spname = token.mylist1
        quad = genQuad('begin_block', spname, '_', '_')
        entityInsert(addFuncEntity(token.mylist1, quad))
        scopeInsert()
        if token.typ == ID:
            lex()
            funcbody(spname)
            if token.typ == ENDFUNC:
                genQuad('end_block', spname, '_', '_')
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
    for quad in quadList:
    	mips_code(quad, spname)
        
def funcbody(name):
    formalpars(name)
    block()

def formalpars(name):
    if token.typ == LEFTPARENTH:
        lex()
        formalparlist(name)
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

def formalparlist(name):
    if token.typ == IN or token.typ == INOUT or token.typ == INANDOUT:
        formalparitem(name)
        if token.typ == IN or token.typ == INOUT or token.typ == INANDOUT:
            print('File: ', file_to_compile )
            print ("ERROR near line", token.lin - 1)
            print ("ERROR: ' , ' missing")
            exit(0)
        while token.typ == COMMA:
            lex()
            formalparitem(name)
    elif not(token.typ == RIGHTPARENTH):
        print('File: ', file_to_compile )
        print ("ERROR near line", token.lin - 1)
        print ("ERROR: ' in/inout/inandout ' expected")
        exit(0)

def formalparitem(name):
    global parCounter
    if token.typ == IN:
        lex()
        (tmpent, useless) = searchByType(name, 'FUNC')
        tmpent.fArg.append(Argument('CV', token.mylist1))
        entityInsert(addParEntity(token.mylist1, 'CV'))
        if token.typ == ID:
            genQuad('par', token.mylist1, 'CV', '_')
            lex()
        else:
            print('File: ', file_to_compile )
            print ("ERROR near line", token.lin - 1)
            print ("ERROR: After in, ID expected")
            exit(0)
    elif token.typ == INOUT:
        lex()
        (tmpent, useless) = searchByType(name, 'FUNC')
        tmpent.fArg.append(Argument('REF', token.mylist1))
        entityInsert(addParEntity(token.mylist1,'REF'))
        if token.typ == ID:
            genQuad('par', token.mylist1, 'REF', '_')
            lex()
        else:
            print('File: ', file_to_compile )
            print ("ERROR near line", token.lin - 1)
            print ("ERROR: After inout, ID expected")
            exit(0)
    elif token.typ == INANDOUT:
        lex()
        (tmpent, useless) = searchByType(name)
        tmpent.fArg.append(Argument('CP', token.mylist1))
        entityInsert(addParEntity(token.mylist1, 'CP'))
        if token.typ == ID:
            genQuad('par', token.mylist1, 'REF', '_')
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
        None

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
    global exitList, startLoopQuad, endLoopQuad
    exitList.append(None)
    if token.typ == LOOP:
        lex()
        startLoopQuad.append(nextQuad())
        statements()
        endLoopQuad.append(nextQuad())
        if token.typ == ENDLOOP:
            if exitList[-1] != None:
                backpatch(exitList[-1], endLoopQuad.pop())
            else:
                genQuad('jump', '_', '_', startLoopQuad.pop())
            exitList.pop()
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

def exitStat():    # enters if token = EXIT, no need for checking
    lex()
    tmp = makelist(nextQuad())
    genQuad('jump', '_', '_', '_')
    exitList[-1] = tmp
    
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
    genQuad('retv', '_', '_', exp)
    entityInsert(addTempEntity(exp))
    #printScopes()
    fillFramelength()
    scopeDelete()

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
    retval = ""
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
        exp1   = expression()
        op     = relationOper()
        exp2   = expression()
        Btrue  = makelist(nextQuad())
        genQuad(op, exp1, exp2, '_')
        Bfalse = makelist(nextQuad())
        genQuad('jump', '_', '_', '_')
        retval = (Btrue, Bfalse)
    return retval
       
def expression():    
    optionalSign()
    term1 = term()
    while (token.typ == PLUS) or (token.typ == MINUS):
        op      = addOper()
        term2   = term()
        tempLab = newTemp()
        genQuad(op, term1, term2, tempLab)
        term1   = tempLab
    return term1

def term():
    factor1 = factor()
    while (token.typ == TIMES) or (token.typ == DIV):
        op         = mulOper()
        factor2    = factor()
        tempLab    = newTemp()
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
        partail = idtail()
        if partail:
            retf = newTemp()
            genQuad('par', retf, 'RET', '_')
            genQuad('call', parid, '_', '_')
            retval = retf
        else:
        	retval = parid
    elif token.typ == NUMBER:    # na prosthesw isws arnitikous/thetikous
        entityInsert(Const(token.mylist1))
        retval = token.mylist1
        lex()
    else:
        print ("ERROR near line", token.lin - 1)
        print("ERROR (factor):  expected")
        exit(0)
    return retval

def idtail():
    if token.typ == LEFTPARENTH:
        actualpars()
        return True
    else:
    	return False

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
    
    if firsttime==0:            #The file needs to be opened once. 
        file_to_compile = sys.argv[1]    #This variable changes value only once, so as the file.
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
                goback = 1    # seek back
        elif state == 2:    # number
            if not (symbol.isdigit()):
                state = recog
                goback = 1    # seek back
        elif state == 3:    # <= , <> , <
            if not(symbol in ('=', '>')):
                goback = 1    # seek back
            state = recog
        elif state == 4:    # >= , >
            if not(symbol == '='):
                goback = 1;    # seek back
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
