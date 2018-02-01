import libscrc
def text_qr(account,one_time=True,country="TH",money="",currency="THB"):
    """
    text_qr(account,one_time=True,country="TH",money="",currency="THB")
    account is phone number or  identification number.
    one_time : if you use once than it's True.
    country : TH
    money : money (if have)
    currency : THB
    """
    Version = "0002"+"01" # เวชั่นของ  PromptPay
    if one_time==True: # one_time คือ ต้องการให้โค้ดนี้ครั้งเดียวหรือไม่
        one_time="010212" # 12 ใช้ครั้งเดียว
    else:
        one_time="010211" # 11 ใช้ได้้หลายครั้ง
    merchant_account_information="2937" # ข้อมูลผู้ขาย
    merchant_account_information+="0016"+"A000000677010111" # หมายเลขแอปพลิเคชั่น PromptPay
    if len(account)!=13: # ใช้บัญชีใช้เป็นเบอร์มือถือหรือไม่ ถ้าใช่ จำนวนจะไม่เท่ากับ 13
        account=list(account)
        merchant_account_information+="011300" # 01 หมายเลขโทรศัพท์ ความยาว 13 ขึ้นต้น 00
        if country=="TH":
            merchant_account_information+="66" # รหัสประเทศ 66 คือประเทศไทย
        del account[0] # ตัดเลข 0 หน้าเบอร์ออก
        merchant_account_information+=''.join(account)
    else:
        merchant_account_information+="02"+account.replace('-','') # กรณีที่ไม่รับมือถือ แสดงว่าเป็นเลขบัตรประชาชน
    country="5802"+country # ประเทศ
    if currency=="THB":
        currency="5303"+"764" # "764"  คือเงินบาทไทย ตาม https://en.wikipedia.org/wiki/ISO_4217
    if money!="": # กรณีกำหนดเงิน
        check_money=money.split('.') # แยกจาก .
        if len(check_money)==1 or len(check_money[1])==1: # กรณีที่ไม่มี . หรือ มีทศนิยมแค่หลักเดียว
            money="54"+"0"+str(len(str(float(money)))+1)+str(float(money))+"0"
        else:
            money="54"+"0"+str(len(str(float(money))))+str(float(money)) # กรณีที่มีทศนิยมครบ
    check_sum=Version+one_time+merchant_account_information+country+currency+money+"6304" # เช็คค่า check sum
    check_sum1=hex(libscrc.ccitt(check_sum.encode("ascii"),0xffff)).replace('0x','')
    if len(check_sum1)<4: # # แก้ไขข้อมูล check_sum ไม่ครบ 4 หลัก
        check_sum1=("0"*(4-len(check_sum1)))+check_sum1
    check_sum+=check_sum1
    return check_sum.upper() # upper ใช้คืนค่าสตริงเป็นตัวพิมพ์ใหญ่