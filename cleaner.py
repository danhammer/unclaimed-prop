import re
from pygeocoder import Geocoder, GeocoderError
from  urllib2 import urlopen
from bs4 import BeautifulSoup

def _clean_entry(soup, key_name):
    """Accepts the name of an element ID in the soup object and strips
    the extra white space or other nuisance characters.

    """
    entry = soup.find(id = key_name)
    try:
        string = entry.text.strip(' $\n\r\t')
    except AttributeError: 
        string = ' '
    cleaned = re.sub(r'\s+', ' ', string)
    return cleaned.replace("'","")


def grab_cash(soup):
    """Accepts the soup object and returns a cash float.  A common
    value is `0.00 (See " * " below)`.  Entries with this value are
    assigned `None` and are not included in the data table.

    """
    cash = _clean_entry(soup, 'ctl00_ContentPlaceHolder1_CashReportData')
    cash = cash.replace(",","")
    try:
        return float(cash)
    except ValueError:
        return None


def grab_coords(soup):
    """Accepts the soup object and returns the (latitude, longitude)
    coordinates of the address.  Returns (0,0) if there is some
    geocoding error.

    """
    address = _clean_entry(soup, 'ReportedAddressData')
    try:
        coded = Geocoder.geocode(address)
        return coded[0].coordinates
    except GeocoderError:
        return (0.0, 0.0)


def grab_name(soup):
    """Returns the reported name of the person owed"""
    name = _clean_entry(soup, 'ctl00_ContentPlaceHolder1_dlOwners')
    return "'%s'" % name 


def grab_reporter(soup):
    """Returns the name of the reporting company of the owed money"""
    reporter = _clean_entry(soup, 'ReportedByData')
    return "'%s'" % reporter


def grab_type(soup):
    """Returns the types of owed property (eg, insurance premiums)"""
    property_type = _clean_entry(soup, 'PropertyTypeData')
    return "'%s'" % property_type


def compile_data(property_id, soup):
    """returns a dictionary with the column names of a prefabricated
    CartoDB table and the values.

    """
    # extract and clean relevant information from soup string, collect
    # in a single list
    lat, lon = grab_coords(soup)
    name = grab_name(soup)
    reporter = grab_reporter(soup)
    property_type = grab_type(soup)
    value = grab_cash(soup)
    vals = [property_id, lat, lon, name, reporter, property_type, value]

    # return a dictionary with values ready for cartodb insert, as
    # long as the coordinates aren't (0,0) and the cash value is a
    # reasonable number.
    header = '(property_id,lat,lon,name,reporter,type,value)'
    if all(v == 0 for v in [lat, lon]) or value == None:
        val_str = None
    else:
        val_str = '(' + ','.join(str(x) for x in vals) + ')'

    return {'header' : header, 'values' : val_str}


def carto_entry(property_id):
    """Accepts the unique property identifier; returns a dictionary
    with the column names of a prefabricated CartoDB table and the
    values, as long as the ID exists in the online database.

    """
    # query the website, convert webpage at property ID to soup object
    base_url = 'https://ucpi.sco.ca.gov/ucp/PropertyDetails.aspx?propertyID='
    idx = str(property_id).zfill(9)
    html = urlopen(base_url + idx).read()
    soup = BeautifulSoup(html)
    
    # Return nonetypes if there is no data associated with the
    # supplied property ID.
    if soup.text.find('YOUR SESSION HAS EXPIRED') > 0:
        return {'header' : None, 'values' : None}
    else:
        return compile_data(property_id, soup)
    
