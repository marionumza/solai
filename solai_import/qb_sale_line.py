
import csv
#import xmlrpclib
from xmlrpc import client as xmlrpclib
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
    def __init__(self, server_ip, server_port, dbname, username, pwd):
        # Get the uid
        # sock_common = xmlrpc.client.ServerProxy('http://' + server_ip + ':' + server_port + '/common')
        url = 'http://' + server_ip + ':' + server_port
        common = xmlrpclib.ServerProxy('{}/xmlrpc/2/common'.format(url))
        models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))

        # db = dbname
        # username = username
        # password = pwd
        self.uid = common.login(dbname, username, pwd)
        self.dbname = dbname
        self.pwd = pwd
        self.models = xmlrpclib.ServerProxy('{}/xmlrpc/2/object'.format(url))


    def do_import_so(self, csv_file):
        file = csv.reader(open(csv_file), delimiter=',')
        total_lines = sum(1 for line in file)
        csvReader = csv.DictReader(open(csv_file), delimiter=',')
        sb = ProgressBar(40)
        count = 2

        for row in csvReader:
            customer_id = False
            so = self.models.execute(self.dbname, self.uid, self.pwd, 'sale.order', 'search_read',
                                    [['name', '=', row['Num'].strip()]])
            product = self.models.execute(self.dbname, self.uid, self.pwd, 'product.template', 'search_read',
                                    [['name', '=', row['Product'].strip()],['active', '=', False]])
            product_id = product and product[0] and product[0]['id']
            price_unit = 0
            if product and product[0] and product[0]['name'] == 'Discount' or product and product[0] and product[0]['name'] == 'Install':
                price_unit = float(row['Amount'].strip().replace(',', ''))

            if not product:
                product_vals = {'name': row['Product'].strip(), 'active': False}
                product_id = self.models.execute(self.dbname, self.uid, self.pwd, 'product.template', 'create', product_vals)
                print("Created new product ****************", product_id)
            if so and product_id:
                try:
                    qty = float(row['Qty'].strip().replace(',', ''))
                except ValueError:
                    qty = 1.0



                order_no = so and so[0] and so[0]['id']
                order_date = datetime.strptime(row['Date'].strip(), '%m/%d/%Y').date()
                so_line_vals = {
                    #'name': ,
                    'product_id':product_id,
                    'order_id': order_no,
                    #'journal_id': inv_journal and inv_journal[0] and inv_journal[0]['id'],
                    #'partner_id': customer_id,
                    'product_uom_qty': qty,
                    #'price_unit': float(row['Amount'].strip().replace(',', '')),

                }
                if price_unit != 0:
                    so_line_vals.update({'price_unit': price_unit})

                #print(so_line_vals, '#'*20)
                self.models.execute(self.dbname, self.uid, self.pwd, 'sale.order.line', 'create', so_line_vals)

            # #print(invoice_vals)
            # inv_id = self.models.execute(self.dbname, self.uid, self.pwd, 'account.move', 'search_read',
            #                                   [['name', '=', row['Num'].strip()]])
            # invoice_id = inv_id and inv_id[0] and inv_id[0]['id']
            # #print(invoice_id,'iiiii')
            # if inv_id:
            #     invoice_line_vals = {
            #         'name': line_name,
            #         'move_id': inv_id and inv_id[0] and inv_id[0]['id'],
            #         'price_unit': float(amount),
            #         'quantity': float(qty),
            #         'account_id':19
            #
            #     }
            #     self.models.execute(self.dbname, self.uid, self.pwd, 'account.move.line', 'create', invoice_line_vals)




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
    if len(args) < 6:
        print(__doc__)
    else:
        server_ip = args[0]
        server_port = args[1]
        database = args[2]
        username = args[3]
        password = args[4]
        csvFileName = args[5]

        ip = import_so(server_ip, server_port, database, username, password)
        ip.do_import_so(csvFileName)


if __name__ == "__main__":
    main()
