
import csv
#import xmlrpclib
import xmlrpc.client
# import time
import sys
#sys.path.append('/Users/shelton/PycharmProjects/OdooGIT/odoo')
import getopt
# import re
# import time
# from datetime import datetime
from itertools import cycle
#import re
from re import sub
from decimal import Decimal
from datetime import date, datetime
#import  fields, models


class ProgressBar(object):
    """Visualize a status bar on the console."""

    def __init__(self, max_width):
        """Prepare the visualization."""
        self.max_width = max_width
        self.spin = next(cycle(r'-\|/'))
        self.tpl = '%-' + str(max_width) + 's ] %c %5.1f%%  %d/%d'
        show(' [ ')
        self.last_output_length = 0

    def update(self, percent, count, max_count):
        """Update the visualization."""
        # Remove last state.
        show('\b' * self.last_output_length)

        # Generate new state.
        width = int(percent / 100.0 * self.max_width)

        output = self.tpl % ('-' * width, self.spin, percent, count, max_count)

        # Show the new state and store its length.
        show(output)
        self.last_output_length = len(output)


def show(string):
    """Show a string instantly on STDOUT."""
    sys.stdout.write(string)
    sys.stdout.flush()


def get_date(date_str):
    return date_str


def replace_special_char(s):
    return s.replace('\x1f', '')


class import_transaction:
    def __init__(self, server_ip, dbname, username, pwd):

        url = 'http://' + server_ip
        common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

        db = dbname
        username = username
        password = pwd
        self.uid = common.authenticate(db, username, password, {})
        self.dbname = dbname
        self.pwd = pwd
        self.models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

    def do_create_move(self):
        account_totals = {'6000 Accounting Fees': 7583,
                          '6004 Admin Expense (Secretary)': 9600.00,
                          '6010 Advertising & Marketing': 26981.64,
                          '6020 Auto & Truck Expense': 14099.31,
                          '6100 Bank & Merchant Charges': 6791.48,
                          '6120 Day Labor': 10029.76,
                          '6150 Depreciation': 8819.77,
                          '6160 Dues & Subscriptions': 3682.40,
                          '6600 Health Insurance': 18845.59,
                          '6800 Employee Benefits': 10.00,
                          '7000 Insurance': 15973.72,
                          '7010 Legal & Professional Fees': 19885.80,
                          '7020 Internet & Computer': 10643.89,
                          '7100 License, Fees & Permits': 2332.50,
                          '7150 Meals 50%': 4463.99,
                          '7160 Meals 100%': 307.34,
                          '7179 Miscellaneous': 3547.74,
                          '7200 Office Supplies': 3850.58,
                          '7210 Postage & Shipping': 2447.82,
                          '7220 Reasearch & Development': 21210.53,
                          '7230 Rent': 38241.05,
                          '7300 Repairs & Maintenance': 2022.13,
                          '7360 Small Tools': 7317.02,
                          '7400 Storage': 12583.81,
                          '7410 Shop Supplies': 803.58,
                          '7500 Sub Contractor Expense': 11012.50,
                          '7900 Travel': 1739.94,
                          '8000 Uniforms': 70.33,
                          }
        for account_name, total in account_totals.items():
            move = self.models.execute(self.dbname, self.uid, self.pwd, 'account.move', 'search_read',
                                       [['ref', '=', account_name]])
            if not move:
                move_id = self.models.execute_kw(self.dbname, self.uid, self.pwd, 'account.move', 'create',
                                       [{
                                           'ref': account_name,
                                           'journal_id': 3,
                                       }])
                account = self.models.execute(self.dbname, self.uid, self.pwd, 'account.account', 'search_read',[['code', '=', account_name[0:4]]])
                if account:
                    account_id = account and account[0] and account[0]['id']
                line_expense = self.models.execute_kw(self.dbname, self.uid, self.pwd, 'account.move.line', 'create',
                                                      [{
                                                          'move_id': move_id,
                                                          'account_id': account_id,  # Receivables
                                                          'exclude_from_invoice_tab': True,
                                                          'credit': 0,
                                                          'debit':total,
                                                      }], {'context': {'check_move_validity': False}})

    def do_import_transaction(self, csv_file):

        file = csv.reader(open(csv_file), delimiter=',')
        total_lines = sum(1 for line in file)
        csvReader = csv.DictReader(open(csv_file), delimiter=',')
        sb = ProgressBar(40)
        count = 2

        self.do_create_move()

        for row in csvReader:
            if row['Account']:
                move = self.models.execute(self.dbname, self.uid, self.pwd, 'account.move', 'search_read',
                                           [['ref', '=', row['Account']]])
                move_id = move and move[0] and move[0]['id']
                line_date = datetime.strptime(row['Date'].strip(), '%m/%d/%Y').date()
                name = row['Name']
                account_code = row['Split'][0:4]
                account = self.models.execute(self.dbname, self.uid, self.pwd, 'account.account', 'search_read',
                                           [['code', '=', account_code]])
                account_id = account and account[0] and account[0]['id']

                credit = row['Debit'].replace(',', '').strip() or 0
                debit = row['Credit'].replace(',', '').strip() or 0
                line = self.models.execute_kw(self.dbname, self.uid, self.pwd, 'account.move.line', 'create',

                                            [{
                                                'move_id': move_id,
                                                'name': row['Name']+'-'+row['Memo'],
                                                'date': line_date.isoformat(),
                                                'account_id': account_id,  # Receivables
                                                'exclude_from_invoice_tab': True,
                                                'debit': float(debit),
                                                'credit':float(credit),
                                            }], {'context': {'check_move_validity': False}})

            sb.update(count * 100.00 / total_lines, count, total_lines)
            count += 1
        print()
        '\n'
        return True


__doc__ = "Usage : python3 transaction_by_account.py localhost:8069 solai_live_nov8 admin admin 6000 · Accounting Fees.csv"


def main():
    # parse command line options
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h", ["help"])
    except getopt.error as msg:
        "for help use --help"
        sys.exit(2)
    # process options
    for o, a in opts:
        if o in ("-h", "--help"):
            print(__doc__)

            sys.exit(0)
    if len(args) < 5:
        print(__doc__)
    else:
        server_ip = args[0]
        #server_port = args[1]
        database = args[1]
        username = args[2]
        password = args[3]
        csvFileName = args[4]

        ip = import_transaction(server_ip, database, username, password)
        ip.do_import_transaction(csvFileName)


if __name__ == "__main__":
    main()
