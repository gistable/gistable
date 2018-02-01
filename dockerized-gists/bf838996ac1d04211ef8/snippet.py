import numpy as np
import hashlib

def create_block(parent_block, value, hashfunc):
    """ ------------------------------------------------
        String -> Block -> (Block -> String) -> Block
        ------------------------------------------------
        Produce a new block from a string value and a hash 
        of its parent block. In this case, a block is also a string. 
    """ 
    return value + ': ' + hashfunc(parent_block)
    
def create_blockchain(parent_block, values, hashfunc):
    """ -------------------------------------------------------
        List String -> Block -> (Block -> String) -> List Block
        -------------------------------------------------------
        Return block chain given list, parent_block, and hash function.
    """
    block = create_block(parent_block, values[0], hashfunc)
    
    if len(values) == 1:
        return [block]
    else:
        return [block] + create_blockchain(block, values[1:], hashfunc)

def sha256(string):
    return hashlib.sha256(string).hexdigest()[:10]

def parens(string):
    return '(' + string + ')'

values = ['Oprah', 'loves', 'haggis']    

start_block = 'Genesis'
new_blocks = create_blockchain(start_block, values, sha256)
blocks = [start_block] + new_blocks

print sha256(start_block) #  81ddc8d248
print new_blocks # ['Oprah:  81ddc8d248',
                 #  'loves:  7ce8a984d9',
                 #  'haggis: 4e94771d64']
                 
new_blocks = create_blockchain(start_block, values, parens)
blocks = [start_block] + new_blocks

print parens(start_block) #  (Genesis)
print new_blocks # ['Oprah:  (Genesis)',
                 #  'loves:  (Oprah: (Genesis))',
                 #  'haggis: (loves: (Oprah: (Genesis)))']
                 
def change_random_character(string):
    """ ----------------
        String -> String
        ----------------
        Return string with one of its characters
        (potentially) changed to another alphanumeric character. 
    """
    chars = list('0123456789abcdefghijklmnopqrstuvwxyz')
    i = np.random.choice(range(len(string))) # index of character to changen
    new_char = np.random.choice(chars)
    return string[:i] + new_char + string[i+1:]

print [change_random_character("aaaa") for _ in range(3)] # ['ataa', 'aaam', 'aaa4']

def mutate_blocks(blocks, n):
    """ -------------------------------
        List Block -> Int -> List Block
        -------------------------------
        Given a list of blocks, return a list 
        containing n random mutations of each. 
    """
    mutated_blocks = []
    for block in blocks:
        for _ in range(n):
            mutated_blocks.append(change_random_character(block))
    return mutated_blocks

mutate_blocks(blocks, 2)
# ['Genksis',
#  'Genasis',
#  'Oprah: 81rdc8d248',
#  'Oprah: 81ddc8ds48',
#  'loves: 7ce8ae84d9',
#  'laves: 7ce8a984d9',
#  'haggis: 4e94771dg4',
#  'haggis: 4e94771n64']
        
def get_reference(block):
    """ ---------------
        Block -> String
        ---------------
        Given a block, return the reference to its parent. 
    """
    if ': ' not in block: # invalid block
        return 'no parent reference'
    else: 
        return block.split(': ')[1]
    
def map_to_keys(f, xs):
    """ ------------------------------
        (a -> b) -> List a -> Dict b a
        ------------------------------
        Return dictionary where each value 
        is an element x in xs, and each key is f(x). 
        """
    return {f(x): x for x in xs}    
    
def reconstruct_blockchain(parent_block, blocks, hashfunc):
    """ ------------------------------------------------------
        Block -> List Block -> (Block -> String) -> List Block
        ------------------------------------------------------
        Reconstruct valid blockchain from a parent block 
        and list of other blocks which may be part of blockchain. 
    """
    reference_dict = map_to_keys(get_reference, blocks)
    blockchain = [parent_block]
    while True:
        reference = hashfunc(blockchain[-1])
        if reference in reference_dict.keys():
            blockchain.append(reference_dict[reference])
        else:
            return blockchain

candidate_blocks = mutate_blocks(blocks, 2) + blocks
reconstruct_blockchain(start_block, candidate_blocks, sha256)
    



