
''' expressionString = IF Variable_3 > 1000 RETURN VARIABLE_3* VARIABLE_1 END IF Variable_3 < 1000 RETURN VARIABLE_3* VARIABLE_2 END '''
def parse_expression(expressionString):
    expressionStringArray = filter(None,expressionString.split("END"))
    
    ''' expressionStringArray[0] = IF Variable_3 > 1000 RETURN VARIABLE_3* VARIABLE_1
    expressionStringArray[1] = IF Variable_3 < 1000 RETURN VARIABLE_3* VARIABLE_2 '''

    for expression in expressionStringArray:
        expConditionResult = expression.strip().split("RETURN")

        '''
        expConditionResult[0] = IF Variable_3 > 1000 or IF Variable_3 < 1000
        expConditionResult[1] = VARIABLE_3* VARIABLE_1 or VARIABLE_3* VARIABLE_2

        And next remove the IF to feed the remaining string to eval '''

        expCondition = expConditionResult[0].replace("IF","").strip()

       ''' Replace the VARIABLE_1 & VARIABLE_2 with the real Values  using string.replace() python function
        # Split whole string based on spaces for now and planning to check every item in array after striping . Kind of brute force
        # also removing and trailing blanks by filter none
        expCondition = 300 > 1000 or 300 < 1000 '''

        retval = eval(expCondition)
        if retval == True:
            '''
            Process & return the string after the return which will be 
            expConditionResult[1] =  300*100 or 300*200
            '''
            return eval(expConditionResult[1])
            
