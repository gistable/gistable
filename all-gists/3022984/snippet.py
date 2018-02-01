class ZhihuDev(Developer) : 
    @property
    def characteristics(self):
        return set(["Teamwork", "Devoted", "Creative"])

    @property
    def skills(self) :
        return {
            "Language"  : ["Python","Erlang", "Golang", "C/C++"],
            "OS"        : ["Linux", "Mac OS X", "BSD UNIX"] , 
            "Tool"      : ["Vim", "Emacs", "Git"], 
            "Framework" : ["Tornado", "Gevent", "Flask"], 
            "Network"   : ["TCP/IP", "ZeroMQ"]}
    
    @property
    def is_geek(self): 
        return True