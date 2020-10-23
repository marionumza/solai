
import csv
import xmlrpc.client
import sys
import getopt
from itertools import cycle

from datetime import date, datetime


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
                    'product_id':product_id,
                    'order_id': order_no,
                    'product_uom_qty': qty,

                }
                if price_unit != 0:
                    so_line_vals.update({'price_unit': price_unit})

                #print(so_line_vals, '#'*20)
                self.models.execute(self.dbname, self.uid, self.pwd, 'sale.order.line', 'create', so_line_vals)

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
        # server_port = args[1]
        database = args[1]
        username = args[2]
        password = args[3]
        csvFileName = args[4]

        ip = import_so(server_ip, database, username, password)
        ip.do_import_so(csvFileName)


if __name__ == "__main__":
    main()
