import matplotlib.pyplot as plt
import matplotlib.cm as cm
import pandas as pd
import numpy as np
import random
import itertools
import math
from matplotlib.ticker import NullFormatter 
import warnings
warnings.filterwarnings("ignore")

#input adapters
def input_adapter(responses):
    '''
    :param responses:
    :return: Psi
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
    #recreate array
    responses_aux = {}
    i = 0
    for key, response in responses.items():
        responses_aux[i] = response
        i += 1
    responses = responses_aux
    
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
def plot_results(x, xlabel, results, print_columns):
    colors = cm.rainbow(np.linspace(0, 1, len(results)))
    marker = itertools.cycle((',', '+', '.', 'o', '*')) 
    linestyles = itertools.cycle(('-', '--', '-.', ':'))
    data = {'x': x}
    
    if (len(print_columns) > 3):
        rows = math.ceil(len(print_columns)/3)
    else:
        rows = 3
        
    k = int(f'{rows}31')
    plt.figure(num=None, figsize=(18, 10), dpi=80, facecolor='w', edgecolor='k')
    plt.tight_layout()
    for column in print_columns:
        ylabel = column
        
        ys = {}
        for d_key, d_val in results.items():
            ys[d_key] = d_val[column]
        
        for y_key, y_val in ys.items():
            data[y_key] = y_val

        df=pd.DataFrame(data)

        i = 0
        for y_key, y_val in ys.items():
            plt.subplot(k)
            plt.plot(data['x'], y_key, data=df, linestyle=next(linestyles), color=colors[i], linewidth=2, label=y_key)
            plt.xticks(data['x'])
            i += 1

        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.legend()
        
        k += 1
    #end for
    
    plt.gca().yaxis.set_minor_formatter(NullFormatter())
    plt.subplots_adjust(left  = 0.125,  # the left side of the subplots of the figure,
                        right = 0.9,    # the right side of the subplots of the figure,
                        bottom = 0.1,   # the bottom of the subplots of the figure,
                        top = 0.9,      # the top of the subplots of the figure,
                        wspace = 0.4,   # the amount of width reserved for blank space between subplots,
                        hspace = 0.2)
    plt.show()
    
def print_hyperparameters(cf, cr,base_votes_per_item, drawing_simulations_amount, expert_cost_increment, workers_num, z, 
                          fixed_acc, base_workers_acc, fixed_workers_acc, items_num, data_true_percentage,
                          iterations_per_ct, cts, k):
    print(f"""
        Hyparparameters:
            - Classification
                * Classification function: {cf.__name__}
                * Cost ratio: {cr}
            - Classification thresholds:
                * {cts}
            - Items
                * Amount: {items_num} 
                * Ground true percentage: {data_true_percentage}
            - MV votes:
                * Base votes per item: {base_votes_per_item}
            - Workers
                * Amount of workers: {workers_num}
                * Cheaters percentage: {z}
                * If not fixed, workers accuracy > {base_workers_acc} 
                * Workers fixed accuracy? {fixed_acc}
                * Fixed number: {fixed_workers_acc}
            - Cost estimator fn
                * Cost estimator drawing number: {drawing_simulations_amount}
                * Expert cost increment: {expert_cost_increment}
            - Experiments convergence:
                * # iterations per classification threshold: {iterations_per_ct}
            - Penalization in false negatives
                * k: {k}
    """)
#end
    
#workers
def simulate_workers(workers_num, cheaters_prop, fixed_acc, workers_acc, base_acc = .5):
    workers = {}
    for i in range(workers_num):
        if (fixed_acc == False):
            if np.random.binomial(1, cheaters_prop):
                # worker_type is 'rand_ch'
                worker_acc_pos = worker_acc_neg = 0.5
            else:
                # worker_type is 'worker'
                worker_acc_pos = base_acc + (np.random.beta(1, 1) * (1 - base_acc))
                #worker_acc_neg = worker_acc_pos + 0.1 if worker_acc_pos + 0.1 <= 1. else 1.
                worker_acc_neg = worker_acc_pos
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
    
    if (len(worker_ids_used) > 1000):
        used = len(worker_ids_used)
        ranges = len(workers_ids_range)
        unu = len(workers_ids_unused)
        print(f'u: {used} - r: {ranges} - un: {unu}')
    
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

def classify_items_with_expert(votes, gt, cf, th):
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
        p_in = cf(input_adapter_single(v))
        p_out = 1 - p_in
        if (p_out > th):
            items_classification.append(0)
        else:
            items_classification.append(1)

    return items_classification

def get_items_predicted_classified(results):
    return {i:v for (i,v) in results.items() if v == True}

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i + n]
#end

#cost utils
#calculates the total cost = crowd cost(all votes) + expert cost
def get_total_cost(votes, cr, cf, th, use_expert):
    total_votes_amount = sum([len(v) for i, v in votes.items()]) 
    
    crowd_cost = total_votes_amount * cr
    total_cost = crowd_cost
    
    if (use_expert): #use some criteria for identifying items sent to expert
        unclassified_items_amount = len([i for (i, v) in votes.items() if cf(input_adapter_single(v)) <= th and cf(input_adapter_single(v)) > .3])
        total_cost = crowd_cost + (unclassified_items_amount * (1 / cr))
    else:
        unclassified_items_amount = len([i for (i, v) in votes.items() if cf(input_adapter_single(v)) <= th])
    
    classified_items_amount = len(votes) - unclassified_items_amount
    
    return classified_items_amount, unclassified_items_amount, crowd_cost, total_cost

def get_crowd_cost(item_votes, cr):
    return len(item_votes) * cr
#end
    
#metrics
class Metrics:

    @staticmethod
    #k penalization for false negatives
    def compute_metrics(items_classification, gt, k = 1):
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
                        

        recall = tp / (tp + fn)          
        precision = tp / (tp + fp)
        loss = (fp + (fn * k)) / len(gt)
        
        return loss, recall, precision
    
#end

#data utils
def load_data(path, predicates):
    data = pd.read_csv(path)
    y_predicate = {}  # gt labels per predicate
    for pr in predicates:
        y_predicate[pr] = data[pr].values

    return y_predicate