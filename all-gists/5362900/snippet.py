def p_block_if_statement(t):
  '''block_if_statement	: RULE_OPEN IF data RULE_CLOSE statements else_blocks'''
	t[0] = _AstNode(Interpreter.r_if, t[3], t[5], t[6])

def p_else_if_blocks(t):
	'''else_blocks		: else_if_block
				| else_block
				| RULE_OPEN END RULE_CLOSE'''
	t[0] = t[1]

def p_else_block(t):
	'''else_block	: RULE_OPEN ELSE RULE_CLOSE statements RULE_OPEN END RULE_CLOSE'''
	t[0] = t[4]

def p_else_if_block(t):
	'''else_if_block	: RULE_OPEN ELSE_IF data RULE_CLOSE statements else_blocks'''
	t[0] = _AstNode(Interpreter.r_if, t[3], t[5], t[6])