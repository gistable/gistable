# -*- coding: UTF-8 -*-
from flaskext.wtf import Form, TextField, PasswordField, RecaptchaField, \
                        AnyOf, NoneOf, Regexp, Email, Required, EqualTo, Recaptcha
from wtforms.validators import StopValidation
from flask import request, session
import model

# 身份證字號格式驗證
def check_ID(form, field):
    locations = dict(zip([c for c in 'ABCDEFGHJKLMNPQRSTUVXYWZIO'], range(10,36)))
    msg = u'身份證字號格式不正確'
    ID = field.data
    if len(ID) != 10: raise StopValidation(msg)
    if ID[0] in locations:
        x = locations[ID[0]]
        x1 = int(x/10)
        x2 = x%10
    else: raise StopValidation(msg)
    d = [int(digit) for digit in ID[1:]]
    y = x1 + x2*9 + \
        d[0]*8 + d[1]*7 + d[2]*6 + d[3]*5 + d[4]*4 + d[5]*3 + d[6]*2 + d[7]*1 + d[8]
    if y % 10 == 0: return True
    else: raise StopValidation(msg)

# 確認圖形驗證是否空白沒填寫
def check_recaptcha_filled(form, field):
    challenge = request.form.get('recaptcha_challenge_field', '')
    response = request.form.get('recaptcha_response_field', '')
    if not challenge or not response:
        raise StopValidation(u'請輸入圖形驗證')

# 查詢已註冊的使用者身份證字號
class ExistingUsersID(object):
    def __iter__(self):
        return iter([user.username for user in model.db.session.query(model.User.username).all()]) #@UndefinedVariable

class LoginForm(Form):
    ID = TextField(u'身份證字號')
    password = PasswordField(u'密碼', validators=[Required(u'請輸入密碼')])

class SignUpForm(Form):
    ID = TextField(u'身份證字號', validators=[check_ID, NoneOf(ExistingUsersID(), u'此身份證字號已存在，請確認是否已註冊')])
    mobile_phone = TextField(u'行動電話', validators=[Regexp(r'^09\d{8}$', message=u'行動電話號碼格式不正確')])
    email = TextField(u'電子郵件', validators=[Email(u'電子郵件位址格式不正確')])
    password = PasswordField(u'密碼', validators=[Required(u'請設定密碼')])
    chk_password = PasswordField(u'確認密碼', validators=[EqualTo('password', u'兩次輸入的密碼不相符')])
    recaptcha = RecaptchaField(u'圖形驗證', validators=[check_recaptcha_filled, Recaptcha(u'輸入錯誤，請再試一遍')])

class AddrForm(Form):
    address = TextField(u'通訊地址', validators=[Required(u'請輸入地址')])