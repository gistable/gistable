# -*- coding: utf-8 -*-

from datetime import datetime
import urllib2


def kb_balance(account, password, resident, username):
    """
    국민은행 계좌 잔액 빠른조회. 빠른조회 서비스에 등록이 되어있어야 사용 가능.
    빠른조회 서비스: https://obank.kbstar.com/quics?page=C018920

    account  -- 계좌번호 ('-' 제외)
    password -- 계좌 비밀번호 (숫자 4자리)
    resident -- 주민등록번호 끝 7자리
    username -- 인터넷 뱅킹 ID (대문자)
    """

    if len(password) != 4 or not password.isdigit():
        raise ValueError("password: 비밀번호는 숫자 4자리여야 합니다.")

    if len(resident) != 7 or not resident.isdigit():
        raise ValueError("resident: 주민등록번호 끝 7자리를 입력해주세요.")

    url = 'https://obank.kbstar.com/quics?asfilecode=524517'
    params = {
        '다음거래년월일키': '',
        '다음거래일련번호키': '',
        '계좌번호': account,
        '비밀번호': password,
        '조회시작일': datetime.now().strftime('%Y%m%d'),
        '조회종료일': datetime.now().strftime('%Y%m%d'),
        '주민사업자번호': '000000' + resident,
        '고객식별번호': username.upper(),
        '응답방법': '2',
        '조회구분': '2',
        'USER_TYPE': '02',
        '_FILE_NAME': 'KB_거래내역빠른조회.html',
        '_LANG_TYPE': 'KOR'
    }

    for k, v in params.iteritems():
        url += '&' + k + '=' + v

    r = urllib2.urlopen(url)
    data = r.read()

    balance_str = data.split("<td class='td' colspan='3'>")[2].split("<")[0]
    balance = int(balance_str.replace(',', ''))
    return balance
