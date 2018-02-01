def init_nmp():
    install_nginx()
    install_php()
    install_phpfpm()

def install_nginx():
    sudo("add-apt-repository ppa:nginx/stable")
    sudo("apt-get update")
    sudo("apt-get -y -q install nginx-full nginx-common")

def install_php():
    # More packages upon request
    sudo("apt-get -y -q --force-yes install php5-cli php5-cgi php5-mysql")
    sudo("apt-get -y -q --force-yes install php5-mcrypt libmcrypt mcrypt") 

def install_phpfpm():
    # TODO: use canonical php-fpm package when available
    sudo("add-apt-repository ppa:brianmercer/php")
    sudo("apt-get update")
    sudo("apt-get -y -q install php5-fpm")