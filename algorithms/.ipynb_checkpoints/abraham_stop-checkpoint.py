import math

#inverted case for use the same decision logic
#returns false if must stop and true if must continue
'''
Implementation of the stopping algorithm.

References:
I.   Abraham,   O.   Alonso,   V.   Kandylas,   R.   Patel,   S.   Shelford,   andA. Slivkins. Using worker quality scores to improve stopping rules.CoRR,abs/1411.0149, 2014

Va = amount of votes for class = 1
Vb = amount of votes for class = 0
'''
def abraham_stop_binary(v_a, v_b, c, e):
    t = v_a + v_b
    return math.fabs(v_a - v_b) < (c * math.sqrt(t)) - (e * t)