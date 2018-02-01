# -*- encoding:utf-8 -*-
#
# CentOSをセキュアにセットアップするFabricスクリプト
#
# 前提条件 : Fabricインストール済／SSHの公開鍵作成済
# 実行方法 : fab deploy
# 検証環境 : CentOS6.6 (さくらのVPS 標準OSインストール)
#####################################################################

from fabric.api import env, run, sudo, put
from fabric.colors import green
from fabric.decorators import task

import time

########  基本設定  ########

# 作成する作業用ユーザ
USER_NAME = 'your_name'            # ← 必ず変更する！
# 作業用ユーザのパスワード
PASSWORD  = 'your_password'        # ← 必ず変更する！
# rootのメールアドレス
ROOT_MAIL_ADDLESS = 'your_address' # ← 必ず変更する！
# 設定するSSHのポート番号
SSH_PORT  = '50022'                # ← 変更推奨


########  fabric向け設定  ########

# 接続先のVPSサーバのIPアドレス
env.hosts = ["XX.XX.XX.XX"]        # ← 必ず変更する！
# 接続ユーザ名
env.user  = 'root'                 # ← 通常は変更不要


########  高度な設定  ########

# セキュリティ系ツールのインストールを行う
#  - fail2ban
#  - Clam AntiVirus
#  - Rootkit Hunter
#  - Tripwire
IS_SETUP_SECURITY_TOOLS = False    # ← Trueにするとツールをインストールする

# さくらのVPSの場合にTrueにすると、NW速度が向上する可能性がある
# 参考URL：https://help.sakura.ad.jp/app/answers/detail/a_id/1368
IS_SAKURA_VPS = False              # ← さくらのVPS以外ではFalseにしておこう


@task
def deploy():
  server_setup()


# 実行時間を計測するデコレータ
def measure_time(func):
  def _measure_time(*args, **keyword):
    start_time = time.time()
    task_name = " ".join(func.__name__.split("_"))
    print green('Start %s ...' % (task_name))
    func(*args, **keyword)
    end_time = time.time() - start_time
    print green('End %s : %s sec' % (task_name, end_time))
  return _measure_time


# サーバのセットアップ
@measure_time
def server_setup():
  optimize_sakura_vps()
  standard_server_setup()
  install_security_tools()


# 基本的なサーバのセットアップ
@measure_time
def standard_server_setup():
  print_info()
  add_new_user()
  install_etckeeper()
  setup_su()
  setup_sudo()
  setup_sshd()
  iptables()
  yum_update()
  stop_ipv6()
  stop_service()
  set_root_address()
  install_logwatch()


# セキュリティ系ツールをインストール
def install_security_tools():
  @measure_time
  def _install_security_tools():
    install_fail2ban()
    install_clamd()
    install_rkhunter()
    install_tripwire()

  if IS_SETUP_SECURITY_TOOLS:
    _install_security_tools()


# さくらのVPS向けに最適化する
def optimize_sakura_vps():
  @measure_time
  def _optimize_sakura_vps():
    run("ethtool -K eth0 tso off")
    run('echo "ACTION==\"add\", SUBSYSTEM==\"net\", KERNEL==\"eth0\", RUN+=\"/sbin/ethtool -K eth0 tso off\"" > /etc/udev/rules.d/50-eth_tso.rules')

  if IS_SAKURA_VPS:
    _optimize_sakura_vps()


@measure_time
def print_info():
  run('uname -a')
  run('cat /etc/issue')


@measure_time
def add_new_user(user_name=USER_NAME, password=PASSWORD):
  run('useradd %s -G wheel' % (user_name) )
  run("echo '%s:%s' | chpasswd" % (user_name, password) )


@measure_time
def install_etckeeper():
  run('yum -y install etckeeper')

  run('touch /etc/.gitignore')
  run('echo "shadow*"  >> /etc/.gitignore')
  run('echo "gshadow*" >> /etc/.gitignore')
  run('echo "passwd*"  >> /etc/.gitignore')
  run('echo "group*"   >> /etc/.gitignore')

  run('etckeeper init')
  run('etckeeper commit "First Commit"')


@measure_time
def setup_su():
  run("sed -i 's/^#auth\(\s\+required\)/auth\\1/' /etc/pam.d/su")


@measure_time
def setup_sudo():
  run("sed -i 's/^# %wheel\(\s\+ALL=(ALL)\s\+ALL$\)/%wheel\\1/' /etc/sudoers")


@measure_time
def setup_sshd(user_name=USER_NAME, ssh_port=SSH_PORT):
  # SSHのポート番号変更
  run("sed -i 's/^#Port\s\+22/Port %s/' /etc/ssh/sshd_config"  % (ssh_port) )
  # rootのSSHログイン禁止
  run("sed -i 's/^#PermitRootLogin\s\+yes/PermitRootLogin no/' /etc/ssh/sshd_config")
  # 公開鍵認証を有効にする
  run("sed -i 's/^#PubkeyAuthentication\s\+yes/PubkeyAuthentication yes/' /etc/ssh/sshd_config")
  # パスワードログインの禁止
  run("sed -i 's/^PasswordAuthentication\s\+yes/PasswordAuthentication no/' /etc/ssh/sshd_config")
  # SSHを許可するユーザの制限
  run('echo "AllowUsers %s" >> /etc/ssh/sshd_config' % (user_name))

  # サーバに登録する公開鍵の事前準備
  sudo('mkdir /home/%s/.ssh' % (user_name), user=user_name)
  sudo('chmod 700 /home/%s/.ssh' % (user_name), user=user_name)
  sudo('touch /home/%s/.ssh/authorized_keys' % (user_name), user=user_name)
  sudo('chmod 600 /home/%s/.ssh/authorized_keys' % (user_name), user=user_name)

  # ローカルの公開鍵をサーバに登録（公開鍵は事前に生成しておくこと）
  put('~/.ssh/id_rsa.pub', '/home/%s/.ssh/authorized_keys' % (user_name))

  # sshd再起動
  run("sshd -t")
  run("service sshd restart")


@measure_time
def iptables(ssh_port=SSH_PORT):
  run("iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT")
  run("iptables -A INPUT -i lo -j ACCEPT")
  run("iptables -A INPUT -p icmp -j ACCEPT")

  run("iptables -A INPUT -s 10.0.0.0/8     -j DROP")
  run("iptables -A INPUT -d 10.0.0.0/8     -j DROP")
  run("iptables -A INPUT -s 172.16.0.0/12  -j DROP")
  run("iptables -A INPUT -d 172.16.0.0/12  -j DROP")
  run("iptables -A INPUT -s 192.168.0.0/16 -j DROP")
  run("iptables -A INPUT -d 192.168.0.0/16 -j DROP")

  run("iptables -A INPUT -f -j DROP")
  run("iptables -A INPUT -p tcp -m state --state NEW ! --syn -j DROP")
  run("iptables -A INPUT -p tcp --dport 113 -j REJECT --reject-with tcp-reset")
  run("iptables -A INPUT -p icmp --icmp-type echo-request -m hashlimit --hashlimit 1/s --hashlimit-burst 5 --hashlimit-mode srcip --hashlimit-name input_icmp  --hashlimit-htable-expire 300000 -j DROP")

  run("iptables -A INPUT -p tcp -m tcp --dport %s -j ACCEPT"  % (ssh_port))
  run("iptables -A INPUT -p tcp -m tcp --dport 80 -j ACCEPT")

  run("iptables -P INPUT   DROP")
  run("iptables -P OUTPUT  ACCEPT")
  run("iptables -P FORWARD DROP")

  run("iptables -L --line-numbers -n")

  run("service iptables save")
  run("service iptables restart")


@measure_time
def yum_update():
  run("yum -y update")
  run("yum -y install yum-cron")
  run("service yum-cron start")
  run("chkconfig yum-cron on")


@measure_time
def stop_ipv6():
  run('echo "net.ipv6.conf.all.disable_ipv6 = 1" >> /etc/sysctl.conf')
  run('echo "net.ipv6.conf.default.disable_ipv6 = 1" >> /etc/sysctl.conf')

  run('sysctl -p', warn_only=True)
  run('ifconfig')

  run("sed -i 's/^inet_protocols\s\+=\s\+all$/inet_protocols = ipv4/' /etc/postfix/main.cf")


@measure_time
def stop_service():
  def _stop(service_name):
    run('service %s stop' % (service_name))
    run('chkconfig %s off' % (service_name))

  _stop('ip6tables')


@measure_time
def set_root_address(root_address=ROOT_MAIL_ADDLESS):
  if root_address != '':
    run('echo "root: %s" >> /etc/aliases'  % (root_address))
    run('newaliases')


@measure_time
def install_logwatch():
  run('yum -y install logwatch')
  run('logwatch --print')
  run('logwatch')

@measure_time
def install_fail2ban(ssh_port=SSH_PORT):
  run('yum -y install fail2ban')
  run("sed -i 's/port=ssh/port=%s/' /etc/fail2ban/jail.conf" % (ssh_port))
  run('service fail2ban start')
  run('chkconfig fail2ban on')


@measure_time
def install_clamd():
  run('yum -y install clamd')
  run("sed -i 's/^User\s\+clam$/#\\0/' /etc/clamd.conf")
  run('freshclam')
  run('service clamd start')
  run('chkconfig clamd on')
  #run('clamscan --infected --remove --recursive')


@measure_time
def install_rkhunter():
  run('yum -y install rkhunter')
  run('rkhunter --update', warn_only=True)
  run('rkhunter --propupd')
  #run('rkhunter --check --skip-keypress', warn_only=True)


@measure_time
def install_tripwire():
  run('yum -y install tripwire')

  # サイトキーとローカルキーの生成
  run('tripwire-setup-keyfiles')

  # 全体的な動作設定
  run("sed -i 's/^LOOSEDIRECTORYCHECKING\s\+=false$/LOOSEDIRECTORYCHECKING =true/' /etc/tripwire/twcfg.txt")
  run('twadmin -m F -c /etc/tripwire/tw.cfg -S /etc/tripwire/site.key /etc/tripwire/twcfg.txt')

  # ポリシーファイルの最適化 / 元ネタ：http://centossrv.com/tripwire.shtml
  # メンドウなので、スクリプトはgistに置いておこう。。
  twpolmake_url = 'https://gist.githubusercontent.com/tmknom/035709050cf94ea512ce/raw/d397d9c81c09176413e44da29993841cf4b3bb45/twpolmake.pl'
  run('wget %s -P /etc/tripwire' % (twpolmake_url) )
  run('perl /etc/tripwire/twpolmake.pl /etc/tripwire/twpol.txt > /etc/tripwire/twpol.txt.new')
  run('twadmin -m P -c /etc/tripwire/tw.cfg -p /etc/tripwire/tw.pol -S /etc/tripwire/site.key /etc/tripwire/twpol.txt.new')

  # テキスト版の設定ファイルの削除
  run('rm -f /etc/tripwire/twcfg.txt*')
  run('rm -f /etc/tripwire/twpol.txt*')

  # ベースラインデータベースの初期化
  run('tripwire --init')
  #run('tripwire --check', warn_only=True)
