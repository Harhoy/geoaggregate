#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 31 12:58:29 2017

@author: bruker


"""

'''
###################
###ALGORITME#######
###################

1 Legg alle noder i et sett S

2 Start første gruppe G_1 og legg til det første elementet og de to nærmeste, beregn polygonsentroide C(G_1)

3 Så lenge S ikke er tom:

    3a Finn nodes i S som er nærmest C(G_X) og legg denne til G_X
    
    3b Hvis G_X er full, initialiserer G_X som i 2

###################
###KOORDINATER#####
###################

Data er i UTM32. Sonebokstav er V.

Pakke for utm-konversjon:
https://pypi.python.org/pypi/utm

Pakke for polygoner
https://pypi.python.org/pypi/Shapely

'''

from shapely.geometry import Polygon
import os
from matplotlib import pyplot as plt
from os import path
import time


#####################
#KLASSER
#####################

#Nodeklasse
class Node:
    
    def __init__(self,node_id,x,y):
        self._group = node_id
        self._x = x
        self._y = y
        
    def returnCoordinates(self):
        return self._x, self._y

#Et stack/gryppe av noder
class Stack:

    def __init__(self,size,remainingNodes):
        self.items = []
        self.size = size
        self.remainingNodes = remainingNodes
        
        #Lager de første tre
        first_node = self.remainingNodes[0]
        self.items.append(first_node)
        
        #Closest no 1
        node2 = self.getNearest(first_node)
        pop_index = self.remainingNodes.index(node2)
        self.remainingNodes.pop(pop_index)
        self.items.append(node2)
        
        #Closest no 2
        node3 = self.getNearest(first_node)
        pop_index = self.remainingNodes.index(node3)
        self.remainingNodes.pop(pop_index)
        self.items.append(node3)
        
    def addNodes(self):
        
        if len(self.items) < self.size:
            nextNode = self.getNearestFromCentroid()
            pop_index = self.remainingNodes.index(nextNode)
            self.remainingNodes.pop(pop_index)
            self.items.append(nextNode)
        else:
            return -1

    def getNearestFromCentroid(self):
        
        smallest_value = 10**10
        smallest = -1
        
        [centroid_x,centroid_y] = self.getCentroid()
            
        for node in self.remainingNodes:
                
            [nodeB_x,nodeB_y] = node.returnCoordinates()
                
            test_distance = self.euclidean([nodeB_x,nodeB_y],[centroid_x,centroid_y])
                
            if test_distance < smallest_value and test_distance > 0:
                smallest = node
                smallest_value = test_distance
            
        return smallest

        
    def getNearest(self,nodeA):
        
        smallest_value = 10**10
        smallest = -1
        
        [nodeA_x,nodeA_y] = nodeA.returnCoordinates()
        
        for node in self.remainingNodes:
                
            [nodeB_x,nodeB_y] = node.returnCoordinates()
                
            test_distance = self.euclidean([nodeA_x,nodeA_y],[nodeB_x,nodeB_y])
                
            if test_distance < smallest_value and test_distance > 0:
                smallest = node
                smallest_value = test_distance
            
        return smallest
            
        
    def euclidean(self,pointA, pointB):
        return ((pointA[0]-pointB[0])**2 + (pointA[1]-pointB[1])**2)**.5
        
    def push(self,node):
        self.items.append(node)
    
    def pop(self):
        self.items.pop()
        
    def peek(self):
        return self.items[len(self.items)-1]
    
    def getList(self):
        return self.items
    
    def getLen(self):
        return len(self.items)
    
    def getSize(self):
        return self.size
    
    def passNodes(self):
        return self.remainingNodes
    
    def getCentroid(self):
        
        intuple = []
        
        for node in self.items:
            intuple.append((node.returnCoordinates()[0],node.returnCoordinates()[1]))
        
        pol = Polygon(intuple)
        
        centroid = pol.centroid.wkt
    
        centroid = centroid.split(" ")
        
        x = float(centroid[1].split("(")[1])
        y = float(centroid[2].split(")")[0])
        
        return x,y
    
    def makePoylgon(self):
        
        intuple = []
        
        for node in self.items:
            intuple.append((node.returnCoordinates()[0],node.returnCoordinates()[1]))
            
        
        return Polygon(intuple)
    

#MegaStack som holder alle undergrupper    
class MegaStack:
    
    def __init__(self,datafile):
        self._stacks = []
        self._nodes = []
        
        file = open(datafile,'r') 
        
        i = 0
        for line in file:
            x = float(line.split(';')[0].strip('\ufeff'))
            y = float(line.split(';')[1].strip('\ufeff'))
            self._nodes.append(Node(i,x,y))
            i += 1
        
    def addNode(self,stack_no,node):
        self._stacks[stack_no].push(node)
        
    def addStack(self,size):
        self._stacks.append(Stack(size,self._nodes))
        
    def returnStack(self,stack_no):
        return self._stacks[stack_no]
    
    def returnLastStack(self):
        return self._stacks[-1]
    
    def getAllCentroids(self):
        
        coord_x = []
        coord_y = []
        
        for stack in self.stacks:
            centroid_stack = stack.getCentroid()
            coord_x.append(centroid_stack[0])
            coord_y.append(centroid_stack[1])
        
        return coord_x,coord_y
    
    def getStacks(self):
        for stack in self._stacks:
            print(stack)
            
    def returnNodes(self):
        return self._nodes
    
    def updateNodes(self,remainingNodes):
        self._nodes = remainingNodes
        
    def writeResults(self,utfil_navn):
        utfil = open(utfil_navn,'w')
        i = 0
        utfil.write('G;X;Y' +  '\n')
        for stack in self._stacks:
            for node in stack.getList():
                x = node.returnCoordinates()[0]
                y = node.returnCoordinates()[1]
                line = str(i) + ';' + str(x) + ';' +str(y) + '\n'
                utfil.write(line)
            i += 1
        

#####################
#HOVEDPROGRAM
#####################

def main():
    
    print("-----------------------------")
    print("-------PREPROSSESERING-------")
    print("-----------------------------")
    print('\n')
    
    #soner = int(input("Oppgi antall soner: "))
    #filnavn = input("Filnavn: ")
    
    soner = 500
    
    start = time.time()
    
    #Henter inn data fra til mor-stacken
    MStack = MegaStack('norge_koord.csv')
    
    #HOVEDLØKKE
    i = 0
    while len(MStack.returnNodes()) > 0:
        MStack.addStack(soner)
        
        CurrentStack = MStack.returnLastStack()
            
        while CurrentStack.getLen() < CurrentStack.getSize():
            CurrentStack.addNodes()
            CurrentStack.makePoylgon()
            
        print("Steg:", i,"Antall noder igjen",len(MStack.returnNodes()))
        i += 1

    cwd = os.getcwd()
    MStack.writeResults(cwd+r'/noder.csv')
    
    end = time.time()
    
    print("Antall minutter",(end-start)/60.)
    #MStack.writeResults(path.join(cwd,filnavn +'.csv'))

main()

#Poly = CurrentStack.makePoylgon()
#x,y = Poly.exterior.xy
#plt.axis((2600000,2730000,66460000,66530000))
#plt.plot(x,y,'ro')
#plt.show()
            
