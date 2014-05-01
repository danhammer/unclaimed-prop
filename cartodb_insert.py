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
