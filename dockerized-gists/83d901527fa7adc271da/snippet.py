def lambda_handler(event, context):

    # Get Account Id from lambda function arn
    print "lambda arn: " + context.invoked_function_arn
    
    # Get Account ID from lambda function arn in the context
    ACCOUNT_ID = context.invoked_function_arn.split(":")[4]
    print "Account ID=" + ACCOUNT_ID
    

