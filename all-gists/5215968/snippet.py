#imports
# QSTK Imports
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

# Third Party Imports
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import time
from scipy.optimize import minimize

'''
' Reads data from Yahoo Finance
' @param li_startDate:  start date in list structure: [year,month,day] e.g. [2012,1,28]
' @param li_endDate:  end date in list structure: [year,month,day] e.g. [2012,12,31]
' @param ls_symbols:	list of symbols: e.g. ['GOOG','AAPL','GLD','XOM']
' @returns d_data:      dictionary structure of data mapped to keys e.g. 'open', 'close'
'''
def readData(li_startDate, li_endDate, ls_symbols):
    #Create datetime objects for Start and End dates (STL)
    dt_start = dt.datetime(li_startDate[0], li_startDate[1], li_startDate[2]);
    dt_end = dt.datetime(li_endDate[0], li_endDate[1], li_endDate[2]);

    #Initialize daily timestamp: closing prices, so timestamp should be hours=16 (STL)
    dt_timeofday = dt.timedelta(hours=16);

    #Get a list of trading days between the start and end dates (QSTK)
    ldt_timestamps = du.getNYSEdays(dt_start, dt_end, dt_timeofday);

    #Create an object of the QSTK-dataaccess class with Yahoo as the source (QSTK)
    c_dataobj = da.DataAccess('Yahoo', cachestalltime=0);

    #Keys to be read from the data
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close'];

    #Read the data and map it to ls_keys via dict() (i.e. Hash Table structure)
    ldf_data = c_dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys);
    d_data = dict(zip(ls_keys, ldf_data));

    return [d_data, dt_start, dt_end, dt_timeofday, ldt_timestamps];

'''
' Calculate Portfolio Statistics 
' @param na_normalized_price: NumPy Array for normalized prices (starts at 1)
' @param lf_allocations: allocation list
' @return list of statistics:
' (Volatility, Average Return, Sharpe, Cumulative Return)
'''
def calcStats(na_normalized_price, lf_allocations):
    #Calculate cumulative daily portfolio value
    #row-wise multiplication by weights
    na_weighted_price = na_normalized_price * lf_allocations;
    #row-wise sum
    na_portf_value = na_weighted_price.copy().sum(axis=1);

    #Calculate daily returns on portfolio
    na_portf_rets = na_portf_value.copy()
    tsu.returnize0(na_portf_rets);

    #Calculate volatility (stdev) of daily returns of portfolio
    f_portf_volatility = np.std(na_portf_rets); 

    #Calculate average daily returns of portfolio
    f_portf_avgret = np.mean(na_portf_rets);

    #Calculate portfolio sharpe ratio (avg portfolio return / portfolio stdev) * sqrt(252)
    f_portf_sharpe = (f_portf_avgret / f_portf_volatility) * np.sqrt(250);

    #Calculate cumulative daily return
    #...using recursive function
    def cumret(t, lf_returns):
        #base-case
        if t==0:
            return (1 + lf_returns[0]);
        #continuation
        return (cumret(t-1, lf_returns) * (1 + lf_returns[t]));
    f_portf_cumrets = cumret(na_portf_rets.size - 1, na_portf_rets);

    return [f_portf_volatility, f_portf_avgret, f_portf_sharpe, f_portf_cumrets, na_portf_value];

'''
' Simulate and assess performance of multi-stock portfolio
' @param li_startDate:	start date in list structure: [year,month,day] e.g. [2012,1,28]
' @param li_endDate:	end date in list structure: [year,month,day] e.g. [2012,12,31]
' @param ls_symbols:	list of symbols: e.g. ['GOOG','AAPL','GLD','XOM']
' @param lf_allocations:	list of allocations: e.g. [0.2,0.3,0.4,0.1]
' @param b_print:       print results (True/False)
'''
def simulate(li_startDate, li_endDate, ls_symbols, lf_allocations, b_print):

    start = time.time();
    
    #Check if ls_symbols and lf_allocations have same length
    if len(ls_symbols) != len(lf_allocations):
        print "ERROR: Make sure symbol and allocation lists have same number of elements.";
        return;
    #Check if lf_allocations adds up to 1
    sumAllocations = 0;
    for x in lf_allocations:
        sumAllocations += x;
    if sumAllocations != 1:
        print "ERROR: Make sure allocations add up to 1.";
        return;

    #Prepare data for statistics
    d_data = readData(li_startDate, li_endDate, ls_symbols)[0];

    #Get numpy ndarray of close prices (numPy)
    na_price = d_data['close'].values;

    #Normalize prices to start at 1 (if we do not do this, then portfolio value
    #must be calculated by weight*Budget/startPriceOfStock)
    na_normalized_price = na_price / na_price[0,:];

    lf_Stats = calcStats(na_normalized_price, lf_allocations);

    #Print results
    if b_print:
        print "Start Date: ", li_startDate;
        print "End Date: ", li_endDate;
        print "Symbols: ", ls_symbols;
        print "Volatility (stdev daily returns): " , lf_Stats[0];
        print "Average daily returns: " , lf_Stats[1];
        print "Sharpe ratio: " , lf_Stats[2];
        print "Cumulative daily return: " , lf_Stats[3];

        print "Run in: " , (time.time() - start) , " seconds.";

    #Return list: [Volatility, Average Returns, Sharpe Ratio, Cumulative Return]
    return lf_Stats[0:3]; 

'''
' Optimize portfolio allocations  to maximise Sharpe ratio
' @param li_startDate:	start date in list structure: [year,month,day] e.g. [2012,1,28]
' @param li_endDate:	end date in list structure: [year,month,day] e.g. [2012,12,31]
' @param ls_symbols:	list of symbols: e.g. ['GOOG','AAPL','GLD','XOM']
' @param s_precision:   true - precise optimization; false - 10% increments & positive weights
'''
def optimize(li_startDate, li_endDate, ls_symbols, b_precision):

    start = time.time();

    #Prepare data for statistics
    ld_alldata = readData(li_startDate, li_endDate, ls_symbols);
    d_data = ld_alldata[0];

    #Get numpy ndarray of close prices (numPy)
    na_price = d_data['close'].values;

    #Normalize prices to start at 1 (if we do not do this, then portfolio value
    #must be calculated by weight*Budget/startPriceOfStock)
    na_normalized_price = na_price / na_price[0,:];
    
    
    if b_precision:
        #Precise optimization:
        
        #Define objective function (sharpe ratio)
        def objective_sharpe(x):
            return simulate(li_startDate, li_endDate, ls_symbols, x)[2];

        #Work on this later...
        
    else:
        
        #Imprecise optimization (required in Homework 1)

        #Using backtracking and permutation
        #Permutation function
        def all_perms(elements):
            if len(elements) <=1:
                yield elements;
            else:
                for perm in all_perms(elements[1:]):
                    for i in range(len(elements)):
                        #nb elements[0:1] works in both string and list contexts
                        yield perm[:i] + elements[0:1] + perm[i:];

        #Backtracking function results in list of integers that sum to 10
        global li_sol, li_valid, i_sum, i_numEls;
        TARGET = 10;
        li_sol = [0] * len(ls_symbols);
        #li_sol = [0] * TARGET;
        li_valid = [];
        i_sum = 0;
        i_numEls = 0;
        def back(lastEl):
            global li_sol, li_valid, i_sum, i_numEls;
            #base-case
            if i_numEls >= len(ls_symbols):
                if i_sum == TARGET:
                    li_valid.extend(list(all_perms(li_sol)));
                return;
            #continuation
            for i in range(lastEl, TARGET + 1 - i_sum):
                i_sum += i;
                li_sol[i_numEls] = i;
                i_numEls += 1;
                back(i);
                #undo
                i_sum -= i;
                i_numEls -= 1;
            return;
                
        back(0);
        #Convert to float array that sum to 1
        global lf_valid;
        lf_valid = [];
        for i in li_valid:
            lf_valid.append([j/10.0 for j in i]);

        #Calculate Sharpe ratio for each valid allocation
        f_CurrMaxSharpe = 0.0;
        for allocation in lf_valid:
            t_Stats = calcStats(na_normalized_price, allocation);
            if t_Stats[2] > f_CurrMaxSharpe:
                lf_CurrStats = t_Stats
                f_CurrMaxSharpe = t_Stats[2];
                lf_CurrEffAllocation = allocation;

        #Plot portfolio daily values over time period
        #Obtain benchmark $SPX data
        d_spx = readData(li_startDate, li_endDate, ["$SPX"])[0];
        na_spxprice = d_spx['close'].values;
        na_spxnormalized_price = na_spxprice / na_spxprice[0,:];
        lf_spxStats = calcStats(na_spxnormalized_price, [1]);
        #Plot
        plt.clf();
        plt.plot(ld_alldata[4], lf_spxStats[4]);    #SPX
        plt.plot(ld_alldata[4], lf_CurrStats[4]);  #Portfolio
        plt.axhline(y=0, color='r');
        plt.legend(['$SPX', 'Portfolio']);
        plt.ylabel('Daily Value');
        plt.xlabel('Date');
        plt.savefig('chart.pdf', format='pdf');

        #Print results:
        print "Start Date: ", li_startDate;
        print "End Date: ", li_endDate;
        print "Symbols: ", ls_symbols;
        print "Optimal Allocations: ", lf_CurrEffAllocation;
        print "Volatility (stdev daily returns): " , lf_CurrStats[0];
        print "Average daily returns: " , lf_CurrStats[1];
        print "Sharpe ratio: " , lf_CurrStats[2];
        print "Cumulative daily return: " , lf_CurrStats[3];

        print "Run in: " , (time.time() - start) , " seconds.";
          


'''
Actual Implementation Starts:
'''
startDate = [2011,1,1];
endDate = [2011,12,31];
simulate(startDate,endDate,['AAPL', 'GLD', 'GOOG', 'XOM'], [0.4, 0.4, 0.0, 0.2], True);
optimize(startDate,endDate,['AAPL', 'GLD', 'GOOG', 'XOM'], False);

