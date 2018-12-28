#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 28 15:54:48 2018

@author: pmaglione
"""

import scipy
import math

def binomial_likelihood(p, n, y):
    return (math.factorial(n) / (math.factorial(y) * math.factorial(n - y))) * math.pow(p, y) * math.pow(1 - p, n - y)
    

def classification_fn(votes, prior, accuracy):
    
    n = len(votes)
    y = sum(votes)
    
    likelihood = binomial_likelihood(accuracy, n, y)
    
    #bayes theorem
    posterior = (likelihood * prior) / ((likelihood * prior) + (1 - accuracy) * (1 - prior))
    
    return posterior

'''
Function for deciding to continue or not collecting votes over a task.

votes - array of votes
classification_threshold - value between 0 and 1 for deciding if prob of data is enough or must continue
cost_ratio - ratio of crowd to expert cost, value between 0 and 1
classification_function - function to calculate how likely is to be classified
accuracy - crowd accuracy, value between 0 and 1
prior - prior believe about the item satisfies a condition, .5 is total uncertainty
'''
def decision_fn(votes, classification_threshold, cost_ratio, classification_function, accuracy, prior):
    posterior = classification_fn(votes, prior, accuracy)
    #next_prob = accuracy * posterior + (1 - accuracy) * (1 - posterior)
    
    if posterior > classification_threshold:
        return False
    elif(len(votes) >= (1 / cost_ratio)):
        return False
    else:
        return True
    
    
#test
votes = [1, 1, 1, 1, 1, 1, 1, 0, 0, 0]
ct = .9
cr = .1 #ratio 1:10
acc = .9
prior = .7

print(decision_fn(votes, ct, cr, classification_fn, acc, prior))