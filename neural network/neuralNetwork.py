# -*- coding: utf-8 -*-
"""
Created on Wed Dec 19 17:56:43 2018

@author: Nainesh
"""

"""
 A object of class optimize is used for training . It takes X_train and y_train. -normalise- func mean normalise and -shuffle- shuffles.the data.
 -encode- detects different classes and set their classes as 0,1,2,3,4,....
-parameter- func takes two value - (list of number of units in hidden layer in order,number of class)
-getheta- func takes - (alpha, number of iterations , regularisation parameter , batch size for mini-batch gradient descent{default=0})
-getheta- calls -gradDescent- which first intialise theta using -random_intialise- and -random_theta-. -gradDescent calls -grad- for gradients 
as per number of iteration and batch size. -grad- calls -forprop-. -gradDescent- returns Theta to -gettheta-.
-predict- predicts the output and -decode- help to convert back into classes
"""
 
import numpy as np
from math import sqrt as root
import pandas as pd
import matplotlib.pyplot as plt


def shuffle(a, b):
  assert len(a)== len(b) 
  p = np.random.permutation(len(a))
  return a[p], b[p]



class optimize(object):

    
  def __init__(self,X_f,y):                                  #x_f is matrix of n features, y has elements in range(0,nofcls)

    X_f,y = shuffle(X_f,y)
    self.X = self.normalise(X_f)
    self.y = self.encode(y)

    
  def encode(self,z):
    b = list(set(z.flatten()))
    self.b = b
    encode = pd.Series(range(0,len(b)),index = b)
    Y = (encode[z.flatten()]).values
    y = np.reshape(Y,(-1,1))
    return y


  def normalise(self,x):
      
    mean= np.mean(x,0)
    self.mean = mean
    return (x - mean)


  def sigmoid(self,x):
    dr = 1 + np.exp(-x)
    sig  = np.true_divide(1,dr)
    return sig


  def parameter(self,units,nout):                              # units is a list- [no of unit in hidden layers]
      
    nlayer = len(units) + 2
    units.insert(0,int(np.shape(self.X)[1]))
    units.insert(0,int(0))
    units.append(nout)
    self.nlayer = nlayer
    self.units = units                                         # now, unit is a list- [int(0), net_units in layer 1, net_units in layer 2,]

    
  def gettheta(self,alpha,iterations=100,lambda_=0,batsize = 0, v =0):
      
    self.alpha = alpha
    self.iterations = iterations
    self.lambda_ = lambda_
    self.v = v
    m = np.shape(self.X)[0]
    
    if batsize==0:
      self.batsize = m
    else:
      if int(m)%batsize is 0:
        self.batsize = batsize
      else:
        print ('Batch size is invalid. Running Batch Gradient Descent')
        self.batsize = m
    
    self.gradDescent()
    
    return self.Theta


  def random_theta(self,i):
    
    units = self.units
    einit = root(6) / ( root( units[i]) + root(units[i+1]) )
    theta = np.random.random(( units[i+1],units[i]+1) )*2*einit - einit
    return theta
    

  def random_intialize(self):
    
                                                                #for sake of convention of notation, Theta[0] will contain garbage value
    Theta = [0]
    Theta.extend ( map(lambda i: self.random_theta(i), range(1,self.nlayer)))
    return Theta


  def forprop(self,x,Theta):
    
    A = [0]                                                     # for sake of convention of notation, A[0],Z[0] will contain garbage value
    Z = [0]
    m = np.shape(x)[1]

    Z.append(x)
    k = np.vstack([np.ones((1,m)),Z[1]])
    A.append(k)
    
    for i in range(2,self.nlayer):
      
      Z.append( np.dot(Theta[i-1],A[i-1]) )                        # Z[i] is formed
      A.append( np.vstack([np.ones((1,m)),self.sigmoid(Z[i])]) )   # A[i] is formed

    Z.append( np.dot(Theta[self.nlayer-1],A[self.nlayer-1]) )
    A.append( self.sigmoid(Z[self.nlayer]) )
    
    return [A,Z]
 
    
  def grad(self,Theta,X,y):
    
    nlayer = self.nlayer
    m=np.shape(self.X)[0]
    
    #forprop
    x=X.T
    [A,Z] = self.forprop(x,Theta)
    
    Y = np.zeros(np.shape(A[nlayer]))
    for k in range(0,self.batsize):
      Y[int(y[k,0]),k] = 1

    #backprop
    Del = []
    Del.append( A[nlayer] - Y )
    map ( lambda i: Del.append(self.actgrad(Theta,Del,Z,i)) , range(nlayer-1,1,-1) )  
    Del.extend([0,0])
    Del = list(reversed(Del))
    
    Grad = [0]
    for i in range(1,nlayer):
      temp = Theta[i]
      temp = np.hstack([np.zeros((self.units[i+1],1)),temp[:,1:]])
      regular = ((1.0*self.lambda_)/m)*temp
      k = (1.0/m)*np.dot(Del[i+1],A[i]) + regular
      Grad.append(k)
    
    self.Grad = Grad
 

  def actgrad(self,Theta,Del,Z,i):
    
    k = np.dot( Theta[i][:,1:].T , Del[self.nlayer-1-i] )
    return k * self.sigmoid(Z[i]) * ( 1-self.sigmoid(Z[i]) )


  def gradDescent(self):
    
    Theta = self.random_intialize()
    alpha = self.alpha
    m = np.shape(self.X)[0]
    batsize = self.batsize
    pltdata = []
    
    for k in range(0,self.iterations):
        
      for j in range(0,m,batsize):
        
        X = self.X[ j : j + batsize ,:]
        y = self.y[ j : j + batsize ,:]
        self.grad(Theta,X,y)
        Theta = map( lambda x,y: x - alpha*y , Theta , self.Grad )
        
      if self.v == 1: pltdata.append(self.costfunc(self.X,self.y,Theta))
    self.pltdata = pltdata
    self.Theta = Theta
  

  def predict(self,x):
      
    nlayer = self.nlayer
    x = x - self.mean
    x = x.T
    [A,Z] = self.forprop(x,self.Theta)
      
      
    y = A[nlayer].argmax(0)
    y = y.reshape((np.shape(y)[0],1))
      
    return self.decode(y)


  def decode(self,z):
      
    decode = pd.Series( self.b ,index = range(0,len(self.b)))
    y = (decode[z.flatten()]).values
    y = np.reshape(y,(-1,1))
    return y
  
    
  def accuracy (self,X,y):
      
    X = X - self.mean
    y_predict = self.predict(X)
    k = (y_predict==y)
    k = k.astype(int)

    return  np.sum(k)*100/np.shape(y)[0]


  def costfunc(self,X,y,Theta):        # for more efficiency output of forprop can be passed directly.

    nlayer = self.nlayer
    m = np.shape(X)[0]
    x = X.T
    [A,Z] = self.forprop(x,Theta)
    
    Y = np.zeros( np.shape( A[nlayer] ) )
    for k in range(0,np.shape(A[nlayer])[1]):
      Y[int(y[k,0]),k] = 1
    
    J = (-1/m)*(np.sum( Y*np.log(A[nlayer]) + (1-Y)*np.log(1-A[nlayer]) ))
    regular = 0.0
    for i in range(1,len(Theta)):
      regular = regular + np.sum(Theta[i][:,1:])
    J = J + (self.lambda_*regular)/(2.0*m)
    
    return J


  def plotJvsno(self,alpha,iterations=100,lambda_=0,batsize = 0,v=1):
      
    self.gettheta(alpha,iterations,lambda_,batsize,v)
    plt.plot(range(0,iterations),self.pltdata,'g-')
    plt.xlabel('Iterations')
    plt.ylabel('Cost')
    plt.title('Cost vs Iterations')
    plt.show()
    
    
    
    
