# I was following the Udacity Programming Languages course and this one was actually challenging and fun to figure out.
# Roberto S. 1/20/2013

edges = { (1,'h'):[3,2],
          (3,'h'):[3],
          (2,'h'):[3],
          (2,'t'):[4],
          (4,'m'):[5],
          (5,'l'):[6] }
accepting = [6]
"""accept a NFSM and returns only one (the shortest) string possible. Returns a string if the fsm is not ambiguos or None if it is.
  :param current: current state - integer 
  :param edges: edges in fsm machine - dictionary - {(integer,string):[integer]}
  :param accepting: Final state in a FSM
  :param visited: States already visited, to avoid infinite loops."""
  
def nfsmacceptor(current, edges, accepting, visited): 
    # write your code here
    if current in accepting:
        return ""
    else:
        if current in visited:
            return None
        else:
            for edge in edges:
                if current in edge:
                    for state in edges[edge]:    
                        temp= nfsmacceptor(state, edges, accepting, (visited + [current]))
                        if temp is None:
                            continue
                        else:
                            return edge[1] + temp
                    

        
print "Test Expected Output:\"html\": " + str(nfsmacceptor(1, edges, accepting, [])) 
print "Test Expected Output:\"htm\": " + str(nfsmacceptor(1, edges, [5,6], [])) 




