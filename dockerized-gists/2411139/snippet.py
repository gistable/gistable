#!/usr/bin/env python                                                                                                                                                         
                                                                                                                                                                              
# Trivial GARCH implementation in python                                                                                                                                      
#                                                                                                                                                                             
# From Peter Tessin's http://www.petertessin.com/TimeSeries.pdf                                                                                                               
#                                                                                                                                                                             
                                                                                                                                                                              
import numpy                                                                                                                                                                  
import math                                                                                                                                                                   
                                                                                                                                                                              
def garch(n=1000, mu=0, sig=1):                                                                                                                                               
    errors = numpy.random.normal(mu, sig, n)                                                                                                                                  
                                                                                                                                                                              
    n_a = 2                                                                                                                                                                   
    alpha = numpy.random.uniform(0,1,n_a)                                                                                                                                     
                                                                                                                                                                              
    n_b = 2                                                                                                                                                                   
    beta = numpy.random.uniform(0,1,n_b)                                                                                                                                      
    values = numpy.zeros(n)                                                                                                                                                   
    sigma2 = numpy.zeros(n)                                                                                                                                                   
                                                                                                                                                                              
    for i in range(len(values)):                                                                                                                                              
        sig2 = alpha[0]                                                                                                                                                       
                                                                                                                                                                              
        n1 = len(alpha)-1 if len(alpha)-1<=i else i                                                                                                                           
        for j in range(n1):                                                                                                                                                   
            sig2 = sig2 + alpha[j+1] * math.pow(values[i-j-1], 2)                                                                                                             
                                                                                                                                                                              
        value = 0                                                                                                                                                             
        n2 = len(beta) if len(beta)<=i else i                                                                                                                                 
        for j in range(n2):                                                                                                                                                   
            value = value + beta[j] * sigma2[i-j-1]                                                                                                                           
            sigma2[i] = value + sig2                                                                                                                                          
            values[i] = (math.sqrt(sigma2[i])) * errors[i]                                                                                                                    
                                                                                                                                                                              
    return values, errors                                                                                                                                                     
                                                                                                                                                                              
                                                                                                                                                                              
def historical_bootstrap(log_returns):                                                                                                                                        
    mean = sum(log_returns) / float(len(log_returns))                                                                                                                         
    udd = []                                                                                                                                                                  
    returns_ignored, sigma_hat = garch(len(log_returns))                                                                                                                      
    for r_d, sigma_hat_d in zip(log_returns, sigma_hat):                                                                                                                      
        udd_d = (r_d - mean) / sigma_hat_d                                                                                                                                    
        udd.append(udd_d)                                                                                                                                                     
    return udd                                                                                                                                                                
                                                                                                                                                                              
                                                                                                                                                                              
if __name__ == "__main__":                                                                                                                                                    
    print garch(10)                                                                                                                                                           
    print historical_bootstrap([0.1, 0.2, 0.1, 0.3])                                                                                                                          
                                                                                                                                                                              
                                                                                                                                                                              
                                                                                                                                                                              
                                                                                       