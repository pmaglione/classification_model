import numpy as np
import

action_stop = 0
action_continue = 1


def majority_voting(votes):
    pos = sum(votes)
    neg = len(votes) - pos
    if pos >= neg:
        return 1
    else:
        return 0

consensus_rule_hyperparameter = majority_voting
cost_hyperparameter = 0.1
utility_hyperparameter = 1

class TaskState:
    votes: []
    N: []
    N_num: 0
    V: 0
    V_neg: 0

def calculate_voi():
    pass

def crowd_explorer_decision(tasks, horizon):
    prm = [] #models
    actions = []
    for task in tasks:
        task_state = TaskState()
        t = 0
        voi = 1 #initialization
        while(voi > 0 or t != horizon):
            voi = calculate_voi(task_state, prm, horizon, t)
            if voi > 0:
                vote = get_next_worker_vote() #"real" vote
                #add_label(prm, vote)
                task_state.votes.append(vote)
                t += 1 #number of real votes
        #end while
        action = 
        actions.append(action)
    
def calculate_voi(task_state, prm, horizon):
    for _ in range(100): #until timeout?
        models = sample_models(prm)
        task_state = sample_execution_path(task_state, models, horizon)
        
    return task_state.V - task_state.V_neg
        
            
def sample_execution_path(task_state, models, horizon, t):
    label = None
    if t = horizon:
        label = consensus_rule_hyperparameter(task_state.votes) #consensus rule is hyperparameter
    else:
        next_vote = sample_next_vote(task_votes, models)
        task_votes.append(next_vote)
        label = sample_next_vote(task_votes, models)
    #endif
    task_state.N[label] = task_state.N[label] + 1
    task_state.N_num = task_state.N_num + 1
    task_state.V_neg = ((max(task_state.N) / task_state.N_num) * utility_hyperparameter) - (t - cost_hyperparameter)
    
    if t < horizon:
        st.V = 
    