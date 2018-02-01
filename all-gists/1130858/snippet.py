import csv
import sys
from collections import namedtuple

rows = csv.reader(sys.stdin)

fields = [field.strip().lower().replace(' ', '_').replace('/', '_')
            for field in rows.next() if field.strip() != '']

PaypalRecord = namedtuple('PaypalRecord', fields)

transactions = [PaypalRecord(*row[0:len(fields)]) for row in rows]

def convert_datetime(date, time):
    day, month, year = date.split('/')
    hour, minute, second = time.split(':')
    return ''.join((year, month, day, hour, minute, second)) + '[0:GMT]'

def emit_transaction(date, amount, fit_id, name):
    print """
            <STMTTRN>
                <TRNTYPE>OTHER
                <DTPOSTED>%s
                <TRNAMT>%s
                <FITID>%s
                <NAME>%s
            </STMTTRN>
    """ % (date, amount, fit_id, name)

print """OFXHEADER:100
DATA:OFXSGML
VERSION:102
SECURITY:NONE
ENCODING:USASCII
CHARSET:1252
COMPRESSION:NONE
OLDFILEUID:NONE
NEWFILEUID:NONE

<OFX>
    <BANKMSGSRSV1>
        <STMTTRNRS>
        <TRNUID>1
        <STATUS>
            <CODE>0
            <SEVERITY>INFO
        </STATUS>
        <STMTRS>
        <CURDEF>GBP
        <BANKACCTFROM>
            <BANKID>12345
            <ACCTID>12345
            <ACCTTYPE>CHECKING
        </BANKACCTFROM>
        <BANKTRANLIST>
"""

print "<DTSTART>%s" % convert_datetime(transactions[-1].date, transactions[-1].time)
print "<DTEND>%s" % convert_datetime(transactions[0].date, transactions[0].time)

for transaction in transactions:
    if transaction.currency != "GBP" or "Currency Conversion" in transaction.type:
        sys.stderr.write("Warning: Non-GBP transaction, input manually\n")
        continue
    if float(transaction.gross) < 0 and transaction.to_email_address != '':
        name = "%s to %s" % (transaction.type, transaction.to_email_address)
    elif float(transaction.gross) > 0 and transaction.from_email_address != '':
        name = "%s from %s" % (transaction.type, transaction.from_email_address)
    else:
        name = transaction.type
    emit_transaction(convert_datetime(transaction.date, transaction.time), 
                transaction.gross, transaction.transaction_id, name)
    if float(transaction.fee) != 0:
        emit_transaction(convert_datetime(transaction.date, transaction.time), 
                transaction.fee, "%sFEE" % transaction.transaction_id, "Paypal Fee")



print """
    </BANKMSGSRSV1>
</OFX>
"""
