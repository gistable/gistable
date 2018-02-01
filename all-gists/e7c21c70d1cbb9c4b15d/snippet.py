from csv import DictWriter
from glob import glob
from ofxparse import OfxParser

DATE_FORMAT = "%m/%d/%Y"

def write_csv(statement, out_file):
    print "Writing: " + out_file
    fields = ['date', 'payee', 'debit', 'credit', 'balance']
    with open(out_file, 'w') as f:
        writer = DictWriter(f, fieldnames=fields)
        for line in statement:
            writer.writerow(line)
    
    
def get_statement_from_qfx(qfx):
    balance = qfx.account.statement.balance
    statement = []
    for transaction in qfx.account.statement.transactions:
        credit = ""
        debit = ""
        balance = balance + transaction.amount
        if transaction.type == 'credit':
            credit = transaction.amount
        elif transaction.type == 'debit':
            debit = -transaction.amount
        else:
            raise Error("Unknown transaction type")
        line = {
            'date': transaction.date.strftime(DATE_FORMAT),
            'payee': transaction.payee,
            'debit': debit,
            'credit': credit,
            'balance': balance
        }
        statement.append(line)
    return statement
    

files = glob("*.qfx")
for qfx_file in files:
    qfx = OfxParser.parse(file(qfx_file))
    statement = get_statement_from_qfx(qfx)
    out_file = "converted_" + qfx_file.replace(".qfx",".csv")
    write_csv(statement, out_file)
    