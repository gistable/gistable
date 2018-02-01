import urllib2, re, time
from Tkinter import *


class App:
    def __init__(self, master):
        self.master = master
        frame = Frame(master)
        frame.pack()

        self.trend_string = StringVar()
        self.trend_string.set('')
        self.trend_dict = {}
        self.update_string = StringVar()
        self.update_string.set('Last Updated: ')

        Label(frame, text='Google+ Trends',
              font=('Times', '14', 'bold')).grid(row=0, column=0,
                                                 pady=10, padx=20)
        Label(frame, textvariable=self.trend_string,
              justify=LEFT).grid(row=1, column=0,pady=5, padx=20)
        self.task_bar = Label(frame, bg='white', textvariable=self.update_string,
                              height=1, width=25, anchor=W)
        self.task_bar.grid(row=2, column=0, sticky=EW)

        self.trend_loop()
        
    def trend_loop(self):
        trend_list = self.get_plus_trends()
        temp_string = ''
        dict_list = [x for x in self.trend_dict.keys()]
        for trend in trend_list:
            if not self.trend_dict.has_key(trend):
                self.trend_dict[trend] = trend_list.index(trend)
                temp_string += '%s %s\n' % (unichr(9650), trend)
            else:
                dict_list.remove(trend)
                if self.trend_dict[trend] > trend_list.index(trend):
                    temp_string += '%s %s\n' % (unichr(9650), trend)
                elif self.trend_dict[trend] < trend_list.index(trend):
                    temp_string += '%s %s\n' % (unichr(9660), trend)
                else:
                    temp_string += ' %s %s\n' % (unichr(9679), trend)
                self.trend_dict[trend] = trend_list.index(trend)
        for trend in dict_list:
            del self.trend_dict[trend]
        self.trend_string.set(temp_string)
        self.master.after(60000, self.trend_loop)
        self.update_string.set('Last Updated: %s' % time.strftime('%H:%M:%S', time.localtime()))

    
    def get_plus_trends(self):
        '''
        Returns a list of the top 10 trends on Google Plus
        '''
        site_file = urllib2.urlopen('https://plus.google.com/s/a')
        site_raw = site_file.read()

        a_list = re.findall('s/(\S*)/posts', site_raw)
        a_list = [urllib2.unquote(x) for x in a_list[:10]]

        return a_list


root = Tk()
app = App(root)

root.mainloop()
