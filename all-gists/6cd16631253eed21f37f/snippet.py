#!/usr/bin/env python


#_______________________________________________________________________
#
# C C C P   i s  C o n t r o l    C h a r t s    i n   P y t h o n
#_______________________________________________________________________
#


license_str = """
  This program is free software; you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation; either version 2 of the License, or
  (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program; if not, write to the Free Software
  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
  MA 02110-1301, USA.
 """


from pylab import *
from math import *
import time as py_time
import datetime as py_datetime
#from control_chart_data_parser import *
from cccp_const import *
from cccp_ex import *
from cccp_types import *

def xtend( x ):
    ar = []
    for t in r.sample_times:
        ar.append(x)
    return ar

def rside_txt( xmax, val, txt, loc=None ):
    if loc == None:
        loc = val
    text( xmax*1.02, loc, txt%val )

version = 1.0
script_name = sys.argv[0]
valid_machines = [ "qranky_1", "qranky_2", "igor_1", "example" ]


help_str = """
About:
  CCCP is Control Charts in Python
  %s, Version %3.1f
  Quarq Technology / SRAM LLC
  Jonathan Huft
  Licensed under GPL V2

Example: %s -f=qranky_1

Options:
  --help      ( -? )        Prints this message.
  --machine=  ( -m= )       Specify test machine from following:
              %s
  --file      ( -f= )       Specify CSV file to import from.
  --verbose   ( -v )        More verbose output.
  --license   ( -l )        Prints GPL license notification.

""" % ( script_name, version, script_name, valid_machines )



class Control_Chart:

    def __init__( self ):
        self.verbose = False
        self.outpath = "outputs/"
        self.time_ran = py_time.localtime()
        self.infile = None
        self.tol = 0.05     # Sets axis on mean plot



    # Given a data set, determine which samples are in violation
    # of the common Western Electric  control chart rules
    def western_electric_rules( self, r ):

        # Points outside the +/- 3 sigma control limits
        def get_3s_violators( r ):
            ss = len(r.samples[0].measurements)
            A2r = const_A2[ ss ]*r.range
            ucl = r.mean + A2r
            lcl = r.mean - A2r
            return get_m_of_n_runs( r.sample_means, 1, 1, lcl, ucl )


        ## Two out of three consecutive points outside
        ## the +/- 2 sigma limits
        def get_2s_runs( r ):
            ss = len(r.samples[0].measurements)
            A2r = const_A2[ ss ]*r.range
            ucl = r.mean + A2r*2.0/3.0
            lcl = r.mean - A2r*2.0/3.0
            return get_m_of_n_runs( r.sample_means, 2, 3, lcl, ucl )


        ## Four out of five consecutive points outside
        ## the +/- 1 sigma limits
        def get_1s_runs( r ):
            ss = len(r.samples[0].measurements)
            A2r = const_A2[ ss ]*r.range
            ucl = r.mean + A2r/3.0
            lcl = r.mean - A2r/3.0
            return get_m_of_n_runs( r.sample_means, 4, 5, lcl, ucl )


        ## Eight consecutive points on the same side
        ## of the center line.
        def get_mean_runs( r ):
            ucl = r.mean
            lcl = r.mean
            return get_m_of_n_runs( r.sample_means, 8, 8, lcl, ucl )


        def get_m_of_n_runs( data, m, n, lcl, ucl ):

            t, s = [], []
            for i in range(n,len(data)+1,1):
                set = data[i-n:i]
                if n_of_set( set, m, 'gt', ucl ) or \
                    n_of_set( set, m, 'lt', lcl ):
                    t.append( r.sample_times[i-n:i] )
                    s.append( data[i-n:i] )
            return t, s


        # Checks if 'n' items in a set are greater than 'lim', etc.
        # 'expr' parameter specifies conditional relation of 'set items
        # to 'lim'
        def n_of_set( set, n, expr = 'gt', lim = 0.0 ):
            ct = 0
            for i in set:
                if expr == 'gt':
                    if i > lim:
                        ct += 1
                elif expr == 'lt':
                    if i < lim:
                        ct += 1
                elif expr == 'gte':
                    if i <= lim:
                        ct += 1
                elif expr == 'lte':
                    if i <= lim:
                        ct += 1
            if ct >= n:
                return True
            else:
                return False


        if False:   # Test for WE rules function
            data = [ 0.0, 0.0, 2.0, 3.0, 3.0, 2.0, 2.0, 3.0, \
                     3.0, 2.0, 2.0, 2.0, 3.0, 7.0 ]

            m = 3
            for i in range(m,len(data)+1,1):
                set = data[i-m:i]
                print set,
                if n_of_set( set, n=2, expr='gt', lim=2.5 ):
                    print "!"
                else:
                    print


        ## Get all of the violating series..
        out_of_ctrl_samples = []
        out_of_ctrl_times = []

        if True:
            for f in [ get_3s_violators, get_mean_runs, \
                get_2s_runs, get_1s_runs ]:
                t, s = f( r )
                out_of_ctrl_times.append(t)
                out_of_ctrl_samples.append(s)
                print "Out of control points detected:"
                print f
                print s, "@", t
                print


        return out_of_ctrl_times, out_of_ctrl_samples



    def plot_means( self, r ):

        r.update_all()

        # Use mean of sample ranges
        ss = len(r.samples[0].measurements)
        A2r = const_A2[ ss ]*r.range
        ucl = r.mean + A2r
        lcl = r.mean - A2r

        plot( r.sample_times, xtend(ucl), linewidth=4.0, c='r', alpha=0.5  )
        plot( r.sample_times, xtend(lcl), linewidth=4.0, c='r', alpha=0.5  )
        if True:
            plot( r.sample_times, xtend(r.mean + A2r/3.0), linewidth=1.0, c='b', alpha=0.25  )
            plot( r.sample_times, xtend(r.mean - A2r/3.0), linewidth=1.0, c='b', alpha=0.25  )
            plot( r.sample_times, xtend(r.mean + A2r*2.0/3.0), linewidth=1.0, c='y', alpha=0.25  )
            plot( r.sample_times, xtend(r.mean - A2r*2.0/3.0), linewidth=1.0, c='y', alpha=0.25  )
        plot( r.sample_times, xtend(r.mean), linewidth=2.0, c='b'  )
        plot( r.sample_times, r.sample_means, marker='^', c='k')

        tmin = min(r.sample_times)
        tmax = max(r.sample_times)

        #axis([tmin, tmax, lcl*(1-self.tol),ucl*(1+self.tol)])
        rside_txt(tmax, ucl, "UCL=%5.3f")
        rside_txt(tmax, lcl, "LCL=%5.3f")
        rside_txt( tmax, r.mean, "Nominal=%5.3f" )

        span = ((ucl-lcl)/r.mean )*100.0
        rside_txt( tmax, span, "Span=%5.3f%%", lcl*(1-self.tol))


        #xlabel('Time')
        ylabel('Means', fontsize=18)
        grid(False)


    def plot_western_electric_overlay( self ):
        # Find points that are out of control based on rules and
        # overlay these points with big red blobs
        out_of_ctrl_times, out_of_ctrl_samples = \
            self.western_electric_rules( r )

        if self.verbose and len(out_of_ctrl_samples) :
            print "Overlaying out-of-control points.."

        for rule in range(0, len(out_of_ctrl_samples)):
            t, s = out_of_ctrl_times[rule], out_of_ctrl_samples[rule]

            if len(s) > 0:
                scatter(t, s, s=250, c='r', alpha=0.5)


    def plot_ranges( self, r ):
        r.update_all()

        ss = len(r.samples[0].measurements)
        ucl =  r.range * const_D4[ss]
        lcl =  r.range * const_D3[ss]

        plot( r.sample_times, xtend(ucl), linewidth=4.0, c='r', alpha=0.5  )
        plot( r.sample_times, xtend(lcl), linewidth=4.0, c='r', alpha=0.5  )
        plot( r.sample_times, xtend(r.range), linewidth=2.0, c='b' )
        plot( r.sample_times, r.sample_ranges, marker='^', c='k')

        tmin = min(r.sample_times)
        tmax = max(r.sample_times)

        #axis([tmin, tmax, lcl*0.66, ucl*1.25])
        rside_txt( tmax, ucl, "UCL=%5.3f" )
        rside_txt( tmax, lcl, "LCL=%5.3f" )
        rside_txt( tmax, r.range, "Nominal=%5.3f" )

        #xlabel('Time')
        ylabel('Ranges', fontsize=18)
        grid(True)


    # Achtung:  Need to figure out how to properly compute stdevs
    #           and what factors to use and what they do...
    def plot_stdevs( self, r ):
        r.update_all()
        ss = len(r.samples[0].measurements)
        ucl =  r.stdev * const_B4[ss]
        lcl =  r.stdev * const_B3[ss]

        plot( r.sample_times, xtend(ucl), linewidth=4.0, c='r', alpha=0.5  )
        plot( r.sample_times, xtend(lcl), linewidth=4.0, c='r', alpha=0.5  )
        plot( r.sample_times, xtend(r.stdev), linewidth=2.0, c='b' )
        plot( r.sample_times, r.sample_stdevs, marker='^', c='k')

        tmin = min(r.sample_times)
        tmax = max(r.sample_times)

        #axis([tmin, tmax, lcl*0.666, ucl*1.25])
        rside_txt( tmax, ucl, "UCL=%5.3f" )
        rside_txt( tmax, lcl, "LCL=%5.3f")
        rside_txt( tmax, r.stdev, "Nominal=%5.3f" )

        grid(True)


    def plot_cusum( self, r, target_mean, k=0.5, h=4 ):
        r.update_all()

        # Control limits
        ss = len(r.samples[0].measurements)
        # Adjust sample stdev to estimated population stdev
        sigma = r.stdev * const_A3[ss] / 3.0
        ucl = h*sigma
        lcl = -1.0 * ucl

        # Compute cumulative sums
        su, sl = [0], [0]
        for x in r.sample_means:
            su.append( max( 0, x - target_mean - k*sigma  + su[-1] ) )
            sl.append( min( 0, x - target_mean + k*sigma  + sl [-1]) )
        # Trim the first zeros off..
        su = su[1:]
        sl = sl[1:]


        plot( r.sample_times, xtend(ucl), linewidth=4.0, c='r', alpha=0.5  )
        plot( r.sample_times, xtend(lcl), linewidth=4.0, c='r', alpha=0.5  )
        plot( r.sample_times, su, marker='^', c='k'  )
        plot( r.sample_times, sl, marker='^', c='k' )

        tmin = min(r.sample_times)
        tmax = max(r.sample_times)

        #axis([tmin, tmax, lcl*1.1, ucl*1.1])
        rside_txt( tmax, ucl, "UCL=%5.3f" )
        rside_txt( tmax, lcl, "LCL=%5.3f" )
        rside_txt( tmax, target_mean, "Target=%5.3f")

        grid(True)


    def plot_p_attr( self, r ):
        r.update_all()
        #r.pretty_print(True,False)

        # Control limits
        ss = len(r.samples[0].measurements)

        mean_p = r.get_mean_proportion_defective()
        #print "--> mean_p:", mean_p

        # Compute upper and lower control lims
        ucl, lcl = [], []
        for s in r.samples:
            s.update_all()
            n = len( s.measurements )   #Sample size
            q = 3*sqrt( mean_p*(1-mean_p)/n )

            ucl.append( mean_p + q )
            lcl.append( max( 0, mean_p - q ) )


        plot( r.sample_times, ucl, linewidth=4.0, c='r', alpha=0.5  )
        plot( r.sample_times, lcl, linewidth=4.0, c='r', alpha=0.5  )
        plot( r.sample_times, xtend(mean_p), linewidth=2.0, c='b' )
        plot( r.sample_times, r.defect_proportions, marker='^', c='k',
            linewidth=2.0)


        tmin = min(r.sample_times)
        tmax = max(r.sample_times)

        #ymin =  min(lcl)*0.8
        ymin = 0
        #([tmin, tmax, ymin, max(ucl)*1.2])
        rside_txt( tmax, mean_p, "Mean=%5.3f")
        text( tmax*1.02, ucl[-1], "UCL" )
        text( tmax*1.02,lcl[-1], "LCL" )
        grid(True)



    def save_plots( self, stitle ):

        savefig("%s%s_%s.png"% (self.outpath, stitle, \
            py_time.strftime("%Y-%m-%d_%H-%M-%S", self.time_ran)  ) )
        savefig("%scurrent_%s.png"% (self.outpath, stitle) )




    def make_xbar_plot( self, r, stitle, p2='range', cusum=False ):

        figure(1, figsize=(18, 8), dpi=80, facecolor='w', edgecolor='k')
        suptitle(stitle, fontsize=20)

        #years    = YearLocator()   # every year
        #months   = MonthLocator()  # every month
        #yearsFmt = DateFormatter('%Y')


        if cusum:
            subplot(311)
        else:
            subplot(211)
        title('Generated %s' % py_time.strftime("%Y/%m/%d, %H:%M", \
            self.time_ran) )
        self.plot_means(r)
        #self.plot_western_electric_overlay()


        if cusum:
            subplot(312)
        else:
            subplot(212)
        if p2 in ('r', 'range'):
            self.plot_ranges(r)
            ylabel('Std. Devs.', fontsize=18)
        elif p2 in ('s', 'stdev'):
            self.plot_stdevs(r)
            ylabel('Std. Devs.', fontsize=18)

        if cusum:
            subplot(313)
            self.plot_cusum(r, 10.0, k=0.5, h=4 )
            ylabel('CUSUM', fontsize=18)

        xlabel('Time', fontsize=18)
        self.save_plots(stitle)



        if self.verbose:
            show()



    def make_attr_chart( self, r, stitle ):

        figure(1, figsize=(18, 8), dpi=80, facecolor='w', edgecolor='k')
        suptitle(stitle, fontsize=20)


        subplot(111)
        title('Generated %s' % py_time.strftime("%Y/%m/%d, %H:%M", \
            self.time_ran) )
        self.plot_p_attr(r)
        xlabel('Time', fontsize=18)
        ylabel('Proportion', fontsize=18)


        self.save_plots(stitle)
        if self.verbose:
            show()




#_______________________ M A I N __ P R O G R A M _____________________#

if __name__=="__main__":

    cc = Control_Chart()

    # Parse command-line arguements
    for arg in sys.argv:

        if arg in ['-?', '-h', '-help',  '--help']:
            print help_str
            exit(0)

        if arg in [ "-l", "--license"]:
            print license_str
            exit(0)

        if arg in ["-v", "--verbose"]:
            cc.verbose = True

        if arg.startswith("-m=") or arg.startswith("--machine="):
            cc.machine_name = arg.rsplit( "=", 1 )[1]
            if not cc.machine_name in valid_machines:
                print "Please specify one of the following:", \
                valid_machines
                exit(-1)

        if arg.startswith("-f=") or arg.startswith("--file="):
            cc.infile = arg.rsplit( "=", 1 )[1]


    # x-bar/R chart example from Foster Text
    if False:
        r = import_time_value_arrays( times=[], \
            values=example_data_foster_18_11, sample_size=4 )
        r.pretty_print(True, True)
        t = 'Figure 11-8 from Foster Text'
        cc.make_xbar_plot(r, t, p2='range')


    # p chart example from Foster Text
    elif False:
        r = get_example_data_foster_12_1()
        t = 'Example 12-1 from Foster Text'
        cc.make_attr_chart( r, stitle=t )


    # Example of calibration drift and CUSUM chart
    elif True:
        d = get_calibration_example_data()
        r = import_time_value_arrays( times=[], \
            values=d, sample_size=4 )
        t = 'Calibration Control Chart'
        cc.make_xbar_plot(r, t, p2='range', cusum=True )


    else:
        if cc.infile == None:
            print "Please specify a data file."
            exit(0)
        else:
            t, m = import_csv_to_arrays( cc.infile )
            r = import_time_value_arrays( t, m, sample_size=4 )
            t =  ('Control Chart')
            cc.make_attr_chart( r, stitle=t )