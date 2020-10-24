
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


class import_invoice:
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


    def do_import_invoice(self, csv_file):
        file = csv.reader(open(csv_file), delimiter=',')
        total_lines = sum(1 for line in file)
        csvReader = csv.DictReader(open(csv_file), delimiter=',')
        sb = ProgressBar(40)
        count = 2

        for row in csvReader:
            print(row)
            customer_id = False
            customer = self.models.execute(self.dbname, self.uid, self.pwd, 'res.partner', 'search_read',
                                    [['name', '=', row['Name']]])
            if customer:
                customer_id = customer and customer[0] and customer[0]['id']
            else:
                print("Invalid Customer")

            inv_journal = self.models.execute(self.dbname, self.uid, self.pwd, 'account.journal', 'search_read',
                                           [['code', '=', 'INV']])
            invoice_date = row['Date'].strip()
            line_name = row['Memo'].strip()
            invoice_no = row['Num'].strip()
            invoice_date = datetime.strptime(row['Date'].strip(), '%m/%d/%Y').date()
            amount = row['Amount'].strip()
            qty = row['Qty'].strip()
            invoice_vals = {
                'name': invoice_no,
                'invoice_date': invoice_date.isoformat(),
                'type': 'out_invoice',

                'journal_id': inv_journal and inv_journal[0] and inv_journal[0]['id'],
                'partner_id': customer_id

            }
            #print(invoice_vals)
            inv_id = self.models.execute(self.dbname, self.uid, self.pwd, 'account.move', 'search_read',
                                              [['name', '=', row['Num'].strip()]])
            invoice_id = inv_id and inv_id[0] and inv_id[0]['id']
            #print(invoice_id,'iiiii')
            if inv_id:
                invoice_line_vals = {
                    'name': line_name,
                    'move_id': inv_id and inv_id[0] and inv_id[0]['id'],
                    'price_unit': float(amount),
                    'quantity': float(qty),
                    'account_id':19

                }
                self.models.execute(self.dbname, self.uid, self.pwd, 'account.move.line', 'create', invoice_line_vals)
            # if not inv_id:
            #     print(invoice_vals,"vvvvvvvvvv")
            #     invoice_id = self.models.execute(self.dbname, self.uid, self.pwd, 'account.move', 'create', invoice_vals)

            #print(invoice_id)
            # sdjkfh
            # if main_categ and main_categ[0] and sub_categ and sub_categ[0]:
            #     material_cost_vals = {
            #         'name': final_categ,
            #         'material_type': main_categ[0]['id'],
            #         'sub_category': sub_categ[0]['id'],
            #         'specifications': specifications,
            #         'lead_time': lead_time,
            #         'supplier_item_no': item_no,
            #         'size': size,
            #         'length': length,
            #         'width': width,
            #         'thickness': thickness,
            #         'product_category':r_s_b,
            #         'sq_inch_cost': sq_inch_cost,
            #         'shipping_fixed': shipping_cost,
            #         'final_category': True,
            #         'default_supplier_id': supplier_id,
            #         'taxes_id': [],
            #         'cost': cost,
            #         'tracking': 'serial',
            #         'type': 'product'
            #
            #     }
            #     product = self.models.execute(self.dbname, self.uid, self.pwd, 'product.template', 'search_read',
            #                         [['name', '=', final_categ]])
            #     #print(material_cost_vals)
            #     if product:
            #         print("product exists --->", final_categ)
            #         pass
            #     else:
            #         print("product create --->", final_categ)
            #         material_cost = self.models.execute(self.dbname, self.uid, self.pwd, 'product.template', 'create', material_cost_vals)



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

        ip = import_invoice(server_ip, server_port, database, username, password)
        ip.do_import_invoice(csvFileName)


if __name__ == "__main__":
    main()
