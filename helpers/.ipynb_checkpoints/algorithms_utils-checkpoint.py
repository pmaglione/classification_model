import matplotlib.pyplot as plt
import matplotlib.cm as cm
import pandas as pd
import numpy as np
import random

#input adapters
def input_adapter(responses):
    '''
    :param responses:
    :return: Psi, N
    '''
    Psi = [[] for _ in responses.keys()]
    for obj_id, obj_responses in responses.items():
        for worker_id, worker_response in obj_responses.items():
            Psi[obj_id].append((worker_id, worker_response[0]))
    return Psi

def input_adapter_single(responses):
    '''
    :param responses:
    :return: Psi, N
    '''
    responses = {0: responses}
    Psi = [[] for _ in responses.keys()]
    for obj_id, obj_responses in responses.items():
        for worker_id, worker_response in obj_responses.items():
            Psi[obj_id].append((worker_id, worker_response[0]))
    return Psi

def invert(N, M, Psi):
    """
    Inverts the observation matrix. Need for performance reasons.
    :param N:
    :param M:
    :param Psi:
    :return:
    """
    inv_Psi = [[] for _ in range(N)]
    for obj in range(M):
        for s, val in Psi[obj]:
            inv_Psi[s].append((obj, val))
    return inv_Psi
#end

#results utils
'''
x - list of x values
y - dict of y values where key is the label of the element
xlabel - label of x
ylabel - label of y
'''
def plot_results(x, ys, xlabel, ylabel):
    colors = cm.rainbow(np.linspace(0, 1, len(ys)))

    data = {'x': x}
    for y_key, y_val in ys.items():
        data[y_key] = y_val

    df=pd.DataFrame(data)
 
    i = 0
    for y_key, y_val in ys.items():
        plt.plot(data['x'], y_key, data=df, marker='', color=colors[i], linewidth=2, label=y_key)
        i += 1

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.legend()
    plt.show()
#end
    
#workers
def simulate_workers(workers_num, cheaters_prop, fixed_acc, workers_acc):
    workers = {}
    for i in range(workers_num):
        if (fixed_acc == False):
            if np.random.binomial(1, cheaters_prop):
                # worker_type is 'rand_ch'
                worker_acc_pos = worker_acc_neg = 0.5
            else:
                # worker_type is 'worker'
                worker_acc_pos = 0.5 + (np.random.beta(1, 1) * 0.5)
                worker_acc_neg = worker_acc_pos + 0.1 if worker_acc_pos + 0.1 <= 1. else 1.
        else:
            worker_acc_pos = workers_acc
            worker_acc_neg = worker_acc_pos

        workers[i] = [worker_acc_pos, worker_acc_neg]

    return workers

def get_random_worker_accuracy(workers_accuracy, item_id, votes):
    item_votes = votes[item_id]
    worker_ids_used = item_votes.keys()
    workers_ids_range = workers_accuracy.keys()
    workers_ids_unused = [val for val in workers_ids_range if val not in worker_ids_used]
    
    selected_worker_id = np.random.choice(workers_ids_unused)
    worker_acc_pos = workers_accuracy[selected_worker_id][0]
    worker_acc_neg = workers_accuracy[selected_worker_id][1]

    return {'worker_id': selected_worker_id, 'acc_pos':worker_acc_pos, 'acc_neg': worker_acc_neg}

def get_worker_vote(workers_accuracy, i, gt, votes):
    worker_data = get_random_worker_accuracy(workers_accuracy, i, votes)
    worker_id, worker_acc_pos, worker_acc_neg = worker_data['worker_id'], worker_data['acc_pos'], worker_data['acc_neg']

    if (gt[i]):
        worker_acc = worker_acc_pos
    else:
        worker_acc = worker_acc_neg

    if np.random.binomial(1, worker_acc):
        vote = gt[i]
    else:
        vote = 1 - gt[i]

    return (worker_id, vote)
#end

#data utils
'''
    items_num - number of items
    possitive_percentage - [0,1] percentage of possitive items
'''
def generate_gold_data(items_num, possitive_percentage):
    pos_items_number = int(round(((possitive_percentage * 100) * items_num) / 100))     
    gold_data = ([1] * pos_items_number) + ([0] * (items_num - pos_items_number))
    random.shuffle(gold_data)

    return gold_data

def classify_items_smart(votes, gt, cf, th):
    items_classification = []
    for i, v in votes.items():
        prob = cf(input_adapter_single(v))
        if (prob > th):
            items_classification.append(1)
        elif (prob <= .3):
            items_classification.append(0)
        else:
            items_classification.append(gt[i]) #if .3 < prob < th get expert vote

    return items_classification

def classify_items_mv(votes, gt, cf, th):
    items_classification = []
    for i, v in votes.items():
        prob = cf(input_adapter_single(v))
        if (prob >= th):
            items_classification.append(1)
        else:
            items_classification.append(0)

    return items_classification

def get_items_predicted_classified(results):
    return {i:v for (i,v) in results.items() if v == True}

#end

#cost utils
#calculates the total cost = crowd cost(all votes) + expert cost
def get_total_cost(votes, cr, cf, th):
    total_votes_amount = sum([len(v) for i, v in votes.items()])
    unclassified_items_amount = len([i for (i, v) in votes.items() if cf(input_adapter_single(v)) <= th and cf(input_adapter_single(v)) > .3])
    
    crowd_cost = total_votes_amount * cr
    cost = crowd_cost + (unclassified_items_amount * (1 / cr))
    
    classified_items_amount = len(votes) - unclassified_items_amount
    
    return classified_items_amount, unclassified_items_amount, crowd_cost, cost

#end
    
#metrics
class Metrics:

    @staticmethod
    def compute_metrics(items_classification, gt):
        # FP == False Inclusion
        # FN == False Exclusion
        fp = fn = tp = tn = 0.
        for gt_val, cl_val in zip(gt, items_classification):
            if gt_val and not cl_val:
                fn += 1
            if not gt_val and cl_val:
                fp += 1
            if gt_val and cl_val:
                tp += 1
            if not gt_val and not cl_val:
                tn += 1
                        
        if (tp + fn > 0):
            recall = tp / (tp + fn)            
        else:
            recall = 0
            
        if (tp + fp > 0):
            precision = tp / (tp + fp)
        else:
            precision = 0
            
        loss = (fp + fn) / len(gt)
        
        return loss,  recall, precision
    
#end