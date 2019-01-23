from .truth_finder import expectation_maximization as truth_finder_multiple

def truth_finder_single(Psi):
    '''
        Input: Psi
        Output: Pi = 1
    '''
    N = len(Psi[0])
    M = 1

    _, p = truth_finder_multiple(N, M, Psi)
    
    return p[0][1]