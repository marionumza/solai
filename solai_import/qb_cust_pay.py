
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

# class OdooMarshaller(xmlrpclib.Marshaller):
#
#     """
#     XMLRPC Marshaller that converts date(time) objects to strings in iso8061 format.
#     """
#
#     dispatch = dict(xmlrpclib.Marshaller.dispatch)
#
#     def dump_datetime(self, value, write):
#         # override to marshall as a string for backwards compatibility
#         value = Datetime.to_string(value)
#         self.dump_unicode(value, write)
#     dispatch[datetime] = dump_datetime
#
#     def dump_date(self, value, write):
#         value = Date.to_string(value)
#         self.dump_unicode(value, write)
#     dispatch[date] = dump_date
#
#     def dump_lazy(self, value, write):
#         v = value._value
#         return self.dispatch[type(v)](self, v, write)
#     dispatch[lazy] = dump_lazy
#
#
# # monkey-patch xmlrpc.client's marshaller
# xmlrpclib.Marshaller = OdooMarshaller

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


class import_so:
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


    def do_import_so(self, csv_file):
        file = csv.reader(open(csv_file), delimiter=',')
        total_lines = sum(1 for line in file)
        csvReader = csv.DictReader(open(csv_file), delimiter=',')
        sb = ProgressBar(40)
        count = 2

        for row in csvReader:
            print(row)
            customer_id = False
            customer = self.models.execute(self.dbname, self.uid, self.pwd, 'res.partner', 'search_read',
                                    [['name', '=ilike', row['Customer']]])
            if customer:
                customer_id = customer and customer[0] and customer[0]['id']
            else:
                #cust_vals = {'name': row['Customer']}
                #customer_id = self.models.execute(self.dbname, self.uid, self.pwd, 'sale.order', 'create', cust_vals)
                print("Invalid Customer.........................................", row['Customer'])

            pay_no = row['Num'].strip()
            pay_date = datetime.strptime(row['Date'].strip(), '%m/%d/%Y').date()
            amount = row['Amount'].strip()
            journal = row['Pay Meth'].strip()
            if journal == 'Cash':
                journal = 7
            else:
                journal = 8
            pay_vals = {
                'name': pay_no,
                'payment_date': pay_date.isoformat(),
                #'note': amount,
                'partner_id': customer_id,
                'amount': amount,
                'journal_id': journal,
                'partner_type': 'customer',
                'payment_type': 'inbound',
                'payment_method_id': 1,
            }
            if customer_id:
                self.models.execute(self.dbname, self.uid, self.pwd, 'account.payment', 'create', pay_vals)




            sb.update(count * 100.00 / total_lines, count, total_lines)
            count += 1
        print()
        '\n'
        return True


__doc__ = "Usage : python qb_import.py server port database username password csvFileName"


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

        ip = import_so(server_ip, database, username, password)
        ip.do_import_so(csvFileName)


if __name__ == "__main__":
    main()
