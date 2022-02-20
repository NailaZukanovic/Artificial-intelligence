from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic.edit import CreateView
from django.db import models
import math
from random import shuffle
import secrets

class GameState():
    def __init__(self):
        self.scoreX=0
        self.scoreY=0
        self.gameEnd=False
        self.numberX = 0
        self.numberY = 0

class Game():
    def __init__(self):
        for num in range(self.width*self.width):
            self.fields.append(0)
        self.TipIgre = 'laki'
    fields = []
    width = 10
    lastMove = 0
    turn = True
    char = ''
    root = None
    inProgress = False
    def VictoryCheck(self, board = None):
        if (board == None):
            board = self.fields
        state = GameState()
        for player in ['X', 'O']:
            other = 'X' if player == 'O' else 'O'
            for index in range(len(board)):
                if (board[index] == other):
                    for dir in [1, self.width+1, self.width, self.width-1]:
                        found = 0
                        temp = index
                        while(temp+dir in GetSquare(temp) and board[temp+dir] == player):
                            temp += dir
                            found += 1
                            if(found == 3):
                                if(player == 'X'):
                                    state.numberX += 10
                                else:
                                    state.numberY += 10
                            if(found == 4):
                                if(player == 'X'):
                                    state.numberX += 20
                                else:
                                    state.numberY += 20
                            if (found == 4 and temp+dir in GetSquare(temp) and board[temp+dir] == other):
                                if (player=='X'):   
                                    state.scoreX += 1
                                    state.numberX += 80
                                else:
                                    state.scoreY += 1
                                    state.numberY += 80
        state.gameEnd = False if 0 in board else True
        return state

class Node():
    def __init__(self, p, nm):
        self.nodeMove = nm
        self.depth=0
        self.parent=None
        self.score=None
        self.children=[]

def Ai(request):
    Model.game.TipIgre = request.GET.get('param')
    Model.game.inProgress = True
    return HttpResponse('OK')

def TestCall(request):
    if (not Model.game.inProgress):
        state = Model.game.VictoryCheck()
        print("Score:")
        print("=============")
        print("X: " + str(state.scoreX))
        print("Y: " + str(state.scoreY))
        print("=============")
        return HttpResponse(Model.game.fields)
    if (Model.game.TipIgre != "kompjuter"):
        polje = int(request.GET.get('param'))
        if (ProveraPozicije(polje)):
            Model.game.lastMove = polje
            if (Model.game.turn):
                char = 'X'
            else: 
                char = 'O'
            Model.game.turn = not Model.game.turn
            Model.game.fields[polje] = char

            state = Model.game.VictoryCheck()
            if (state.gameEnd):
                Model.game.inProgress = False
                return HttpResponse(Model.game.fields)
            if (Model.game.TipIgre == 'igraci'):
                return HttpResponse(Model.game.fields)
            Model.game.inProgress = False

            lst=[]

            root = Node(None, Model.game.lastMove) 

            match Model.game.TipIgre:
                case 'laki':
                    levels =  3
                case 'srednji':
                    levels = 5
                case 'teski':
                    level = 5 
                case _:        
                    levels = 3

            TreeCreate(levels,root,lst)

            mm = MinMax()
            bestScore = mm.MinMaxAB(root, True)

            filter(lambda n: len(n.children) == 0, lst)
            print("Number of leafs: " + str(len(lst)))

            if (len(root.children) == 1):
                bestNode = root.children[0]
            else:
                bestNode = next(filter(lambda n: n.score == bestScore, root.children))
            
            
            if (Model.game.turn):
                char = 'X'
            else: 
                char = 'O'
            Model.game.fields[bestNode.nodeMove] = char
            Model.game.lastMove = bestNode.nodeMove
            Model.game.turn = not Model.game.turn
            print("Possible moves:")
            for chld in root.children:
                print(chld.score)
            print("selecting: " + str(bestNode.score))

            del root
            del lst

            Model.game.inProgress = True
        

            state = Model.game.VictoryCheck()
            if (state.gameEnd):
                Model.game.inProgress = False
                return HttpResponse(Model.game.fields)
        
            print("X: " + str(state.scoreX))
            print("Y: " + str(state.scoreY))
        else:
            print("Potez nije validan!")
    else:
        Model.game.inProgress = False
        if 'X' not in Model.game.fields:
            move = secrets.randbelow(len(Model.game.fields))
            Model.game.fields[move] = 'X'
            Model.game.turn = not Model.game.turn
            Model.game.inProgress = True
            Model.game.lastMove = move
        else:
            if (Model.game.turn):
                char = 'X'
            else: 
                char = 'O'
            lst=[]
            root = Node(None, Model.game.lastMove) 
            levels =  3
            TreeCreate(levels,root,lst)
            mm = MinMax()
            bestScore = mm.MinMaxAB(root, True)

            filter(lambda n: len(n.children) == 0, lst)
            print("Number of leafs: " + str(len(lst)))

            if (len(root.children) == 1):
                bestNode = root.children[0]
            else:
                bestNode = next(filter(lambda n: n.score == bestScore, root.children))
            Model.game.fields[bestNode.nodeMove] = char
            Model.game.lastMove = bestNode.nodeMove
            
            print("Possible moves:")
            for chld in root.children:
                print(chld.score)
            print("selecting: " + str(bestNode.score))

            del root
            del lst
            state = Model.game.VictoryCheck()
            if (state.gameEnd):
                return HttpResponse(Model.game.fields)
            else:
                Model.game.inProgress = True
            Model.game.turn = not Model.game.turn
    return HttpResponse(Model.game.fields)

class MinMax():
    def __init__(self):
        self.alfa = float('-inf')
        self.beta = float('inf')
    def MinMaxAB(self,node, maxPlayer):
        if len(node.children) == 0:
            return CalcScore(node)
        if maxPlayer:
            node.score = float('-inf')
            for child in node.children:
                node.score = max(node.score, self.MinMaxAB(child, False))
                if node.score >= self.beta:
                    break 
                self.alfa = max(self.alfa, node.score)
            return node.score
        else:
            node.score = float('inf')
            for child in node.children:
                node.score = min(node.score, self.MinMaxAB(child, True))
                if node.score <= self.alfa:
                    break 
                self.beta = min(self.beta, node.score)
            return node.score


def CalcScore(node):
    board = Model.game.fields[:]
    currentNode = node
    if (Model.game.turn):
        char = 'X'
        op = 'O'
    else: 
        char = 'O'
        op = 'X'

    while(currentNode.depth > 0):
        board[currentNode.nodeMove] = char if currentNode.depth%2==0 else op
        currentNode = currentNode.parent
    state = Model.game.VictoryCheck(board)
    if(Model.game.TipIgre == "srednji"):
        score = (state.scoreY*2 - state.scoreX*3)
    elif(Model.game.TipIgre == "teski"):
        score = (state.scoreY - state.scoreX*10)*50
    else:
        score = state.scoreY*1.5 - state.scoreX*2
    if (state.gameEnd):
        score = float('inf') if state.scoreY > state.scoreX else float('-inf')
    if (char == 'O'):
        return -score
    return score

def TreeCreate(depth, pNode, allNodes): 
    pozicije = list(ListaPozicija(pNode.nodeMove))
    parent = pNode
    while(parent != None):
        if parent.nodeMove in pozicije:
            pozicije.remove(parent.nodeMove)
        parent = parent.parent
    for pos in pozicije:
        n = Node(pNode, pos)
        n.depth = pNode.depth+1
        n.parent = pNode
        pNode.children.append(n)
        allNodes.append(n)
        if (n.depth < depth):
            TreeCreate(depth, n, allNodes)
    shuffle(pNode.children)


def ListaPozicija(move):
    if ('X' not in Model.game.fields):
        return range(len(Model.game.fields))
    if (0 not in Model.game.fields):
        return []
    sq = GetSquare(move)
    if (len(list(filter(lambda n: Model.game.fields[n] == 0, sq)))==0):
        return filter(lambda n: Model.game.fields[n] == 0, range(len(Model.game.fields)))
    else:
        return filter(lambda n: Model.game.fields[n] == 0, sq)


def ProveraPozicije(polje):
    if ('X' not in Model.game.fields):
        return True 
    if (Model.game.fields[polje] != 0):
        return False
    sq = GetSquare(Model.game.lastMove)
    if (polje in sq or len(list(filter(lambda n: Model.game.fields[n] == 0, sq)))==0):
        return True
    return False

def GetSquare(polje):
    square = []
    top = polje//Model.game.width == 0
    bottom = polje//Model.game.width == Model.game.width-1
    left = (polje+1) % Model.game.width == 1
    right = (polje+1) % Model.game.width == 0
    if (not left):
        square.append(polje-1)
        if (not top):
            square.append(polje-Model.game.width-1)
        if (not bottom):
            square.append(polje+Model.game.width-1)
    if (not right):
        square.append(polje+1)
        if (not top):
            square.append(polje-Model.game.width+1)
        if (not bottom):
            square.append(polje+Model.game.width+1)
    if (not top):
        square.append(polje-Model.game.width)
    if (not bottom):
        square.append(polje+Model.game.width)
    return square



class Model(models.Model):
    app_label = "Test"
    game = Game()

class HtmlView(CreateView):
    model = Model
    fields = []
    template_name = "index.html"

def Scores(request):
    board = Model.game.fields[:]
    state = Model.game.VictoryCheck(board)
    return HttpResponse(str(state.scoreX) + " " + str(state.scoreY))
