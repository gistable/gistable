@view_config(context=Forbidden, renderer='renderer.pt')
def forbidden(context, request):
    # If unauthenticated, redirect to sign in
    if(
            Authenticated not in request.effective_principals
            and request.unauthenticated_userid is None
    ):
        raise HTTPFound('auth redirect')

    # If unverified and verification would help, redirect to verification
    principals = request.effective_principals
    denial = context.result
    if(
            Authenticated in principals
            and Verified not in principals
            and denial is not None
            and isinstance(denial, ACLPermitsResult)
    ):
        principals.append(Verified)
        policy = request.registry.queryUtility(IAuthorizationPolicy)
        if policy.permits(denial.context, principals, denial.permission):
            raise HTTPFound('verify redirect')
            
    return {
    	'title': '403 Forbidden',
    }
