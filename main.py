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
import collections

#utils
def binomial_likelihood(p, n, y):
    return (math.factorial(n) / (math.factorial(y) * math.factorial(n - y))) * math.pow(p, y) * math.pow(1 - p, n - y)
    

def get_workers_accuracy(acc):
    return sum(acc) / len(acc)

class Evaluator:
    '''
    Function for deciding to continue or not collecting votes over a task.

    Input:
        votes - dictionary of dictionaries, containing the votes over each item where keys corresponds to workers ID
            {
                item_i: {worker_i:vote...worker_n:vote},
                ...
                item_n: {worker_i:vote...worker_n:vote},
            }
        classification_threshold - value between 0 and 1 for deciding if prob of data is enough or must continue
        cost_ratio - ratio of crowd to expert cost, value between 0 and 1
        classification_function - function to calculate how likely is to be classified
        
    Output:
        Dictionary with the decision for each item (True/False), indexed by item_id
            {
                item_id: Boolean
                ...
                item_n: Boolean
            }
    '''
    def decision_fn(votes, classification_threshold, cost_ratio, classification_function):
        print(votes)
        
        prior = .5
        accuracy = .75 #must be computed using the votes, EM or DawidSkene
        
        results = dict.fromkeys(range(items_num), True)
        
        for item_id, item_votes in votes.items():
            posterior = classification_function(item_votes, prior, accuracy)
            #next_prob = accuracy * posterior + (1 - accuracy) * (1 - posterior)
    
            if posterior > classification_threshold:
                results[item_id] = True
            elif(len(votes) >= (1 / cost_ratio)):
                results[item_id] = False
            else:
                results[item_id] = True
                
        return results
        
    
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
    
class Classificator:
    def classification_fn_posterior(votes, prior, accuracy):    
        n = len(votes)
        y = sum(votes.values())

        likelihood = binomial_likelihood(prior, n, y)

        #bayes theorem
        posterior = (likelihood * prior) / ((likelihood * prior) + (1 - accuracy) * (1 - prior))

        return posterior
    
    def classification_fn_beta_pdf(votes, th, accuracy):    
        n = len(votes)
        y = sum(votes.values())

        posterior = beta.sf(th, 1 + y, 1 + (n - y))

        return posterior

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
    
    def get_random_worker_accuracy(self, item, items_num):       
        '''
        #TO-DO: add logic to avoid worker vote on same task
        worker_found = False
        
        while (worker_found == False):
            index = np.random.randn(0, self.workers_num - 1)

            if (index not in self.index_workers_voted_on_item[item]):
                self.index_workers_voted_on_item[item].append(index)
                worker_found = True
        ''' 
        worker_id = random.randint(0, self.workers_num - 1)
        return (worker_id, self.workers_accuracy[worker_id])
    
    def generate_votes_gt(self, items_num):
        #workers_accuracy = self.workers_accuracy
        total_votes = collections.defaultdict(dict)
        #workers_num = len(self.workers_accuracy)
        #accuracy_media = get_workers_accuracy(workers_accuracy)
        results = dict.fromkeys(range(items_num), True) #Must collect votes for all items
        
        #Every iteration check all items, performance can be improved
        for i in range(items_num):
            get_more_votes = True
            while(get_more_votes):
                if (results[i]): #check if must continue collecting votes for this item
                    worker_id, worker_acc = self.get_random_worker_accuracy(i, items_num)
                   
                    if np.random.binomial(1, worker_acc):
                        vote = 1
                    else:
                        vote = 0
                        
                    total_votes[i][worker_id] = vote
                    
                    #Ask if must continue or not
                    results = Evaluator.decision_fn(total_votes, self.classification_threshold, self.cost_ratio, 
                                                               Classificator.classification_fn_posterior)
                    #Stop when decided stop for all items, all items = False
                    get_more_votes = sum([x for x in results if x == False]) == items_num
            #end while
         #end for     
            
        return total_votes



#Assumptions
#1 condition
#difficulty of tasks are all equal
#there are no test questions
#there are a percent of cheaters
        
z = 0.1 #% cheaters
items_num = 5
ct = .9
cr = .01 #ratio 1:100
iter_num = 1
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
#end for
'''
print("#items classified: {}".format(len([a for a in votes if len(a) < (1/cr)])))
print("Workers general acc: %{:1.2f}".format(get_workers_accuracy(workers_accuracy) * 100))
print("# ground truth IN items: {}".format(len([a for a in ground_truth if a == 1])))
'''
#print(sum([sum(a) for a in votes])/len(votes))
