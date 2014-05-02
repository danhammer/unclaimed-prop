import os
import cleaner
from cartodb import CartoDBAPIKey, CartoDBException

API_KEY = os.environ['CARTODB_API_KEY']
DOMAIN = 'danhammer'
TABLE  = 'claims'


def upload(property_id):
    """Uploads the data for the supplied integer ID"""
    cl = CartoDBAPIKey(API_KEY, DOMAIN)
    x = cleaner.carto_entry(property_id)

    if x['values'] is not None:
        query = 'INSERT INTO %s %s VALUES %s' %(TABLE, x['header'], x['values'])    
        try:
            print "uploading %s" % property_id
            cl.sql(query)
        except CartoDBException as e:
            print ("some error ocurred", e)
            print query


def processed_ids():
    """Returns a list of property IDs that have already been pushed to
    CartoDB

    """
    cl = CartoDBAPIKey(API_KEY, DOMAIN)
    query = 'SELECT property_id FROM %s' % TABLE
    try:
        data = cl.sql(query)
    except CartoDBException as e:
        print ("some error ocurred", e)

    return [x['property_id'] for x in data['rows']]

def total_value():
    """Returns the total value of the unclaimed property that had
    already been uploaded to CartoDB

    """
    cl = CartoDBAPIKey(API_KEY, DOMAIN)
    query = 'SELECT value FROM %s' % TABLE
    try:
        data = cl.sql(query)
    except CartoDBException as e:
        print ("some error ocurred", e)

    cash = sum([x['value'] for x in data['rows']])
    return '{:10,.2f}'.format(cash)
    


def plot_ids():
    import matplotlib.pyplot as plt

    x = processed_ids()
    cash = total_value()
    num_bins = 100
    # the histogram of the data
    n, bins, patches = plt.hist(x, num_bins, facecolor='green', alpha=0.5)
    plt.xlabel('Property ID')
    plt.ylabel('Frequency')
    plt.title(r'Number of IDs: %s, Total value: \$%s' %(len(x), cash))


    # Tweak spacing to prevent clipping of ylabel
    plt.subplots_adjust(left=0.1)
    plt.show()
