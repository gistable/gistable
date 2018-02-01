def startcss():
    with lcd(r"%s/bin" % local_dir):  
        local("nohup ./checkCss.sh &> /dev/null < /dev/null &")

def stopcss():
    local("ps -ef | grep \"checkCss\" | grep -v \"grep\" | awk '{print $2}' | xargs kill -9")