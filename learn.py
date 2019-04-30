"""
This is the Q-Learning Portion of the code.
Here, we define Q-learning-specific functions to be implemented
further down
"""
def get_state(playerDino, cacti, pteras):
    '''
    Compiles state information needed to make computations
    Input: Dino Sprite rect, cacti sprite group, pteras sprite group
    Output: vector/list/dict (need to pick one) that holds state information
    Regardless of datatype, state has the following format:
    [is_airborne (binary),
    is_ducked (binary),
    distance to nearest cactus,
    distance to second nearest cactus,
    distance to pteradactyl]
    '''


    state = {'cact_0_dist' : 999, 'cact_1_dist' : 999, 'ptera_dist' : 999} #init state as a dictionary

    if len(cacti) != 0:
        for c, cactus in enumerate(cacti):
            state['cact_{}_dist'.format(c)] = cactus.rect.left - playerDino.rect.right
    if len(pteras) != 0:
        for d, dactyl in enumerate(pteras):
            state['ptera_dist'] = dactyl.rect.left - playerDino.rect.right

    state['is_airborne'] = 1 * playerDino.isJumping
    state['is_ducked'] = 1 * playerDino.isDucking

    return state


def get_bin(state, cacti):

#This is incomplete
    '''
    Simplified version:
    Subdivide the distance to Cactus0 into five bins (store the label in bin[0])
    Subdivide the distance to Cactus1 into five bins (store the label in bin[1])
    Don't know yet the right bounds yet (below are guesses!)
    The too far bins are to minimize the jumps if we penalize unnecessay jumps
    0  is reserved for absence of a cactus
    -1 is reserved if the dino already passed a cactus
    We can do the most simplified version instead: having only one cactus
    '''
    bin = [0 , 0]

    # Need to figure out these
    cl = 10
    r = 30
    f1 = 300
    f2 = 600

    if len(cacti) != 0:
        for c, cactus in enumerate(cacti): # not sure how 'c' works
            if (state['cact_{}_dist'.format(c)] > 0 and state['cact_{}_dist'.format(c)] < cl):
                bin[c-1] = 1
            elif  (state['cact_{}_dist'.format(c)] >= cl and state['cact_{}_dist'.format(c)] < r):
                bin[c-1] = 2
            elif  (state['cact_{}_dist'.format(c)] >= r and state['cact_{}_dist'.format(c)] < f1):
                bin[c-1] = 3
            elif  (state['cact_{}_dist'.format(c)] >= f1 and state['cact_{}_dist'.format(c)] <= f2):
                bin[c-1] = 4
            else:
                bin[c-1] = -1

    return bin
