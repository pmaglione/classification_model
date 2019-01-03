#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 28 15:54:48 2018

@author: pmaglione
"""

import math
import numpy as np
import random
from scipy.stats import beta

def binomial_likelihood(p, n, y):
    return (math.factorial(n) / (math.factorial(y) * math.factorial(n - y))) * math.pow(p, y) * math.pow(1 - p, n - y)
    

def get_workers_accuracy(acc):
    return sum(acc) / len(acc)

class Classificator:
    '''
    Function for deciding to continue or not collecting votes over a task.

    votes - array of votes
    classification_threshold - value between 0 and 1 for deciding if prob of data is enough or must continue
    cost_ratio - ratio of crowd to expert cost, value between 0 and 1
    classification_function - function to calculate how likely is to be classified
    accuracy - crowd accuracy, value between 0 and 1
    prior - prior believe about the item satisfies a condition, .5 is total uncertainty
    '''
    def decision_fn(votes, classification_threshold, cost_ratio, classification_function, accuracy):
        prior = .5
        posterior = classification_function(votes, prior, accuracy)
        #next_prob = accuracy * posterior + (1 - accuracy) * (1 - posterior)

        if posterior > classification_threshold:
            return False
        elif(len(votes) >= (1 / cost_ratio)):
            return False
        else:
            return True
    
    
class Workers:

    def __init__(self, workers_num, cheaters_prop):
        self.workers_num = workers_num
        self.cheaters_prop = cheaters_prop
        self.acc_passed = []

    # simulate workers
    def simulate_workers(self):
        for _ in range(self.workers_num):
            if np.random.binomial(1, self.cheaters_prop):
                # worker_type is 'rand_ch'
                worker_acc_pos = 0.5
            else:
                # worker_type is 'worker'
                worker_acc_pos = 0.8 + (np.random.beta(1, 1) * 0.2)
            
            self.acc_passed.append(worker_acc_pos)
        #end for
            
        return self.acc_passed

class Generator:

    def __init__(self, params):
        self.workers_accuracy = params['workers_accuracy']
        self.workers_num = params['workers_num']      
        self.items_num = params['items_num']      
        self.cost_ratio = params.get('cost_ratio')
        self.classification_threshold = params.get('classification_threshold')
        self.index_workers_voted_on_item = {}
    
    def generate_gold_data(self, items_num):
        gold_data = []
        for item_index in range(items_num):
            if np.random.binomial(1, .9):
                val = 1
            else:
                val = 0
            gold_data.append(val)
        #end for
        return gold_data
    
    def classification_fn_posterior(self, votes, prior, accuracy):    
        n = len(votes)
        y = sum(votes)

        likelihood = binomial_likelihood(accuracy, n, y)

        #bayes theorem
        posterior = (likelihood * prior) / ((likelihood * prior) + (1 - accuracy) * (1 - prior))

        return posterior
    
    def classification_fn_sf(self, votes, prior, accuracy):    
        n = len(votes) + 2
        y = sum(votes) + 1

        likelihood = beta.sf(.5, n, y)

        #bayes theorem
        posterior = (likelihood * prior) / ((likelihood * prior) + (1 - accuracy) * (1 - prior))

        return posterior
    
    def get_random_worker_accuracy(self, item, items_num):       
        worker_found = False
        '''
        while (worker_found == False):
            index = np.random.randn(0, self.workers_num - 1)

            if (index not in self.index_workers_voted_on_item[item]):
                self.index_workers_voted_on_item[item].append(index)
                worker_found = True
        ''' 
                
        return self.workers_accuracy[random.randint(0, self.workers_num - 1)]
    
    def generate_votes_gt(self, items_num):
        workers_accuracy = self.workers_accuracy
        total_votes = []
        workers_num = len(self.workers_accuracy)
        accuracy_media = get_workers_accuracy(workers_accuracy)

        for i in range(items_num):
            item_votes = []
            get_more_votes = True
            while(get_more_votes):
                worker_acc = self.get_random_worker_accuracy(i, items_num)
               
                if np.random.binomial(1, worker_acc):
                    vote = 1
                else:
                    vote = 0
                item_votes.append(vote)
                
                #Ask if must continue or not
                get_more_votes = Classificator.decision_fn(item_votes, self.classification_threshold, self.cost_ratio, 
                                                           self.classification_fn_posterior, accuracy_media)
            #end while
                
            total_votes.append(item_votes)
         #end for     
            
        return total_votes
    
z = 0.1 #% cheaters
items_num = 100
ct = .9
cr = .01 #ratio 1:100
iter_num = 1
data = []
workers_num = 1000

for _ in range(iter_num):
    workers_accuracy = Workers(workers_num, z).simulate_workers()

    params = {
        'workers_accuracy': workers_accuracy,
        'workers_num': workers_num,
        'items_num': items_num,
        'cost_ratio': cr,
        'classification_threshold': ct
    }

ground_truth = Generator(params).generate_gold_data(items_num)

votes = Generator(params).generate_votes_gt(items_num)

print(len([a for a in votes if len(a) < (1/cr)]))
print("Workers general acc: %{:1.2f}".format(get_workers_accuracy(workers_accuracy) * 100))

