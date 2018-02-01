import types
import tensorflow as tf 
import numpy as np

# Expressions are represented as lists of lists,
# in lisp style -- the symbol name is the head (first element)
# of the list, and the arguments follow.

# add an expression to an expression list, recursively if necessary.
def add_expr_to_list(exprlist, expr):
	# if expr is a atomic type
	if isinstance(expr, types.ListType):
		# Now for rest of expression
		for e in expr[1:]:
			# Add to list if necessary
			if not (e in exprlist):
				add_expr_to_list(exprlist, e)
	# Add index in list.
	exprlist.append(expr)

def expand_subexprs(exprlist):
	new_exprlist = []
	orig_indices = []
	for e in exprlist:
		add_expr_to_list(new_exprlist, e)
		orig_indices.append(len(new_exprlist)-1)
	return new_exprlist, orig_indices

def compile_expr(exprlist, expr):
	# start new list starting with head
	new_expr = [expr[0]]
	for e in expr[1:]:
		new_expr.append(exprlist.index(e))
	return new_expr

def compile_expr_list(exprlist):
	new_exprlist = []
	for e in exprlist:
		if isinstance(e, types.ListType):
			new_expr = compile_expr(exprlist, e)
		else:
			new_expr = e
		new_exprlist.append(new_expr)
	return new_exprlist

def expand_and_compile(exprlist):
	l, orig_indices = expand_subexprs(exprlist)
	return compile_expr_list(l), orig_indices

def new_weight(N1,N2):
	return tf.Variable(tf.random_normal([N1,N2]))
def new_bias(N_hidden):
	return tf.Variable(tf.random_normal([N_hidden]))

def build_weights(exprlist,N_hidden,inp_vec_len,out_vec_len):
	W = dict()  # dict of weights corresponding to each operation
	b = dict()  # dict of biases corresponding to each operation
	W['input']  = new_weight(inp_vec_len, N_hidden)
	W['output'] = new_weight(N_hidden, out_vec_len)
	for expr in exprlist:
		if isinstance(expr, types.ListType):
			idx = expr[0]
			if not W.has_key(idx):
				W[idx] = [new_weight(N_hidden,N_hidden) for i in expr[1:]]
				b[idx] = new_bias(N_hidden)
	return (W,b)

def build_rnn_graph(exprlist,W,b,inp_vec_len):
	# with W built up, create list of variables
	# intermediate variables
	in_vars = [e for e in exprlist if not isinstance(e,types.ListType)]
	N_input = len(in_vars)
	inp_tensor = tf.placeholder(tf.float32, (N_input,  inp_vec_len), name='input1')
	V = []      # list of variables corresponding to each expr in exprlist
	for expr in exprlist:
		if isinstance(expr, types.ListType):
			# intermediate variables
			idx = expr[0]
			# add bias
			new_var = b[idx]
			# add input variables * weights
			for i in range(1,len(expr)):
				new_var = tf.add(new_var, tf.matmul(V[expr[i]], W[idx][i-1]))
			new_var = tf.nn.relu(new_var)
		else:
			# base (input) variables
			# TODO : variable or placeholder?
			i = in_vars.index(expr)
			i_v = tf.slice(inp_tensor, [i,0], [1,-1])
			new_var = tf.nn.relu(tf.matmul(i_v,W['input']))
		V.append(new_var)
	return (inp_tensor,V)

# take a compiled expression list and build its RNN graph
def complete_rnn_graph(W,V,orig_indices,out_vec_len):
	# we store our matrices in a dict;
	# the dict format is as follows:
	# 'op':[mat_arg1,mat_arg2,...]
	# e.g. unary operations:  '-':[mat_arg1]
	#      binary operations: '+':[mat_arg1,mat_arg2]
	# create a list of our base variables
	N_output = len(orig_indices)
	out_tensor = tf.placeholder(tf.float32, (N_output, out_vec_len), name='output1')

	# output variables
	ce = tf.reduce_sum(tf.zeros((1,1)))
	for idx in orig_indices:
		o = tf.nn.softmax(tf.matmul(V[idx], W['output']))
		t = tf.slice(out_tensor, [idx,0], [1,-1])
		ce = tf.add(ce, -tf.reduce_sum(t * tf.log(o)), name='loss')
	# TODO: output variables
	# return weights and variables and final loss
	return (out_tensor, ce)


# from subexpr_lists import *
a = [ 1, ['+',1,1], ['*',1,1], ['*',['+',1,1],['+',1,1]], ['+',['+',1,1],['+',1,1]], ['+',['+',1,1],1 ], ['+',1,['+',1,1]]]
# generate training graph
l,o=expand_and_compile(a)
W,b = build_weights(l,10,1,2)
i_t,V = build_rnn_graph(l,W,b,1)
o_t,ce = complete_rnn_graph(W,V,o,2)
# generate testing graph
a = [ ['+',['+',['+',1,1],['+',['+',1,1],['+',1,1]]],1] ]  # 7
l_tst,o_tst=expand_and_compile(a)
i_t_tst,V_tst = build_rnn_graph(l_tst,W,b,1)

out_batch = np.transpose(np.array([[1,0,1,0,0,1,1],[0,1,0,1,1,0,0]]))
print ce
train_step = tf.train.GradientDescentOptimizer(0.001).minimize(ce)
init = tf.initialize_all_variables()
sess = tf.Session()
sess.run(init)
for i in range(5000):
	sess.run(train_step, feed_dict={i_t:np.array([[1]]),o_t:out_batch})
print l
print l_tst
print sess.run(tf.nn.softmax(tf.matmul(V[1], W['output'])), feed_dict={i_t:np.array([[1]])})
print sess.run(tf.nn.softmax(tf.matmul(V[-1], W['output'])), feed_dict={i_t:np.array([[1]])})
print sess.run(tf.nn.softmax(tf.matmul(V_tst[-2], W['output'])), feed_dict={i_t_tst:np.array([[1]])})
print sess.run(tf.nn.softmax(tf.matmul(V_tst[-1], W['output'])), feed_dict={i_t_tst:np.array([[1]])})
