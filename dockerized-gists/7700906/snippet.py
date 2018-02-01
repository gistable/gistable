import numpy as np
maxl = 19*19
enemy_cell = maxl+1
friendly_cell = maxl+2

#we need this to retrace our steps
def argmax(x):
    i = np.nanargmax(x)
    while len(x)>0 and x[i] in [enemy_cell,friendly_cell,np.inf]:
        x[i] = -np.inf
        i = np.nanargmax(x)
    
    return i

class timer:
    def __init__(self):
        self.time=time.clock()
    def g(self):
        thetime = time.clock()
        diff = thetime-self.time
        self.time=thetime
        return round(diff*10**6) #microseconds

#This only needs to be run on the start of the turn, generates a grid copy of the game board
def generate_grid(self):
    #update the game board

    #at first, we don't know the length to anywhere (NaN)
    self.grid = np.ones(boardsize)*np.nan
    
    #we can never access invalid tiles (inf)
    for loc in np.ndindex(np.shape(self.grid)):
        if "invalid" in rg.loc_types(loc) or "obstacle" in rg.loc_types(loc):
            self.grid[loc] = np.inf
    
    #enemy cells and friendly cells are marked with their respective id
    for loc in self:
        bot = self[loc]
        if bot['player_id'] != self.player_id: #ENEMY
            self.grid[loc] = enemy_cell
        else:
            self.grid[loc] = friendly_cell

def opt_bfs_find_path(self,loc_from,loc_to):
    #print "OPTBFS: Attempting to find path from",loc_from,"to",loc_to
    #t = timer()
    if rg.wdist(loc_from,loc_to)==1:
        return [loc_from,loc_to]
    k=0
    grid = deepcopy(self.grid)
    
    grid[loc_to] = maxl
    grid[loc_from] = 0
    
    path_found = False
    
    next_from_sites = [loc_from]
    next_to_sites = [loc_to]
    join_loc = None        
    
    while (not path_found) and len(next_from_sites)!=0 and len(next_to_sites)!=0:
        new_next_to_sites = []
        new_next_from_sites = []
        k+=1
        for site in next_from_sites:
            for loc in locs_around(site):
                if np.isnan(grid[loc]):
                    grid[loc]=k
                    new_next_from_sites.append(loc)
                elif grid[loc]>k and grid[loc]<enemy_cell:
                    path_found=True
                    join_loc = loc
                    break
                
            if path_found: break
        if path_found: break
            
        for site in next_to_sites:
            for loc in locs_around(site):
                if np.isnan(grid[loc]):
                    grid[loc]=maxl-k
                    new_next_to_sites.append(loc)
                elif grid[loc]<(maxl-k):
                    path_found=True
                    join_loc = loc
                    break
            if path_found: break
                
        next_from_sites = new_next_from_sites
        next_to_sites = new_next_to_sites
    
    #print grid
    if path_found and join_loc is not None:
        path = [join_loc]
        #print "Found path in",k,"iterations and",t.g(),"us"

        #trace back to source:
        l_from=path[0]
        l_to   = path[-1]
        while path[0]!=loc_from:
            nbs_from = [tuple(l_from+d) for d in directions]
            l_from = nbs_from[np.nanargmin([grid[nb] for nb in nbs_from])]
            path.insert(0,l_from)
        
        #trace to target
        while path[-1]!=loc_to:
            nbs_to   = [tuple(l_to+d) for d in directions]
            l_to   =   nbs_to[argmax([grid[nb] for nb in nbs_to])]
            path.append(l_to)
            k += -1

        #print path
        return path
            
    else:
        #print "Could not find path and took",t.g(),"us"
        return None