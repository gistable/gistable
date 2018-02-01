import boto.ec2
import sys
import datetime
from time import gmtime, strftime, sleep
import toml

# expects ec2 instance tag: power-off
# values should be in 24hr clock from:to
# eg 2400:0400
# would result in midnight to 4am

def load_ec2_cache (f):
    try:
        with open(f) as h:
            config = toml.loads(h.read())
            print('loaded cache', config)
            return config
    except:
        return dict()

def save_ec2_cache (f,config):
    try:
        with open(f,'w') as h:
            h.write(toml.dumps(config))
            print('saved cache', config)
    except:
        print('cannot save config cache')

def main (argv):
    config_file = 'ec2.toml'
    config = load_ec2_cache(config_file)
    
    conn = boto.ec2.connect_to_region("us-east-1",
                                      aws_access_key_id='id...',
                                      aws_secret_access_key='key...')

    all_ec2 = conn.get_only_instances(filters={"tag:power-off":"*"})

    if len(all_ec2) < 1: 
        print ("no instances found with power-off tag")
        return

    i = dict()
    for n in all_ec2:
        i[n.id] = { 'power-off':list(map(lambda x:int(x), n.tags['power-off'].split(":"))),
                    'ip':n.ip_address,
                    'state': n.state,
                    'ec2':n }

    #print('found ec2 with tag', i)
    
    hh = (int(strftime("%H", gmtime())) - 4) * 100 # east coast offset
    print("current offset time (gmt-4)", hh)

    for n in i:
        # is turned on?
        if hh >= i[n]['power-off'][0] and hh <= i[n]['power-off'][1]:
            if i[n]['state'] != 'stopped':
                print("powering off!", i)
                i[n]['ec2'].stop()
            else: print('skipping',i)

        # is turned off?
        elif hh < i[n]['power-off'][0] or hh > i[n]['power-off'][1]:
            if i[n]['state'] == 'stopped':
                if i[n]['ip'] is None and config[n] is not None:
                    print('need to assoc ip', n)
                    ips = conn.get_all_addresses()
                    for ip in ips:
                        if config[n] == ip.public_ip:
                            print('found ip',config[n])
                            print('associated ip:',ip.associate(n))
                elif i[n]['ip'] != config[n]:
                    print('ec2 cache ip mismatch',n,i[n]['ip'],config[n])
                elif i[n]['ip'] is None and config[n] is None:
                    print('ec2 missing elastic associated ip!')

                sleep(2)

                print("powering on!", i)
                i[n]['ec2'].start()
                
            else: print('skipping',i)
                
                
        if i[n]['ip']: config[n] = i[n]['ip']
        elif config[n]: print('ec2 lost ip?', n, config[n])

    save_ec2_cache(config_file,config)


if __name__ == "__main__":
    main(sys.argv)
