import subprocess


def get_user_and_password() -> dict:
    return {'PASS_WORD': '*****', 'USER_NAME': '************'}


def login(user_name: str, password: str):
    import time
    import os
    time.sleep(0.3)
    os.environ['NO_PROXY'] = 'net.zju.edu.cn'
    import requests
    url = 'https://net.zju.edu.cn/include/auth_action.php'
    data_content = {'action': 'login',
                    'username': user_name,
                    'password': password,
                    'ac_id': 3,
                    'save_me': 1,
                    'ajax': 1}
    response = requests.post(url, data=data_content)
    print(response.content.decode('utf-8'))


def already_connected_to_wifi() -> bool:
    try:
        result = subprocess.check_output(["netsh", "wlan", "show", "interface"])
        return "ZJUWLAN" in result.decode('utf-8')
    except subprocess.CalledProcessError as e:
        print(e)
        return False


def pre_login_issues():
    if not already_connected_to_wifi():
        subprocess.call(["netsh", "wlan", "connect", "name=ZJUWLAN"])
    user_and_pass = get_user_and_password()
    login(user_name=user_and_pass['USER_NAME'], password=user_and_pass['PASS_WORD'])


if __name__ == "__main__":
    pre_login_issues()
