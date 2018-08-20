"""Retrieve ESA Online Catalogue for ERS and ENVISAT Level-1 products and
save them as CSV files.
"""

import os
from datetime import datetime, timedelta
import shutil

import requests
import pandas as pd


SEARCH_URL = 'http://esar-ds.eo.esa.int/socat/{collection}/search'


def query(search_url, start_date, stop_date, max_lat, max_lon,
          min_lat, min_lon, max_results, orbit, polarisations, swath):
    """Send query to ESA Online Catalogue."""
    params = {'request': 'search', 'service': 'SimpleOnlineCatalogue',
              'version': '1.2', 'format': 'text/tab-separated-values'}
    params['pageCount'] = max_results
    params['query.beginAcquisition.start'] = start_date
    params['query.beginAcquisition.stop'] = stop_date
    params['query.footprint.maxlat'] = max_lat
    params['query.footprint.maxlon'] = max_lon
    params['query.footprint.minlat'] = min_lat
    params['query.footprint.minlon'] = min_lon
    params['query.orbitDirection'] = orbit
    params['query.polarisationChannels'] = polarisations
    params['query.swathIdentifier'] = swath
    r = requests.post(search_url, params)
    return r


def retrieve_indexes(collection, output_dir, begin_date, end_date):
    """Retrieve full catalog in chunks corresponding to 60 days of
    data acquisition.
    """
    start_date = begin_date
    stop_date = start_date + timedelta(60)
    i = 1
    while start_date <= end_date:
        response = query(
            search_url=SEARCH_URL.format(collection=collection),
            start_date=start_date.strftime('%Y-%m-%d'),
            stop_date=stop_date.strftime('%Y-%m-%d'),
            max_lat='', max_lon='', min_lat='', min_lon='',
            max_results=50, orbit='', polarisations='', swath='')
        with open(os.path.join(output_dir, 'catalog_{}.tsv'.format(i)), 'w') as f:
            f.write(response.text)
        i += 1
        start_date += timedelta(60)
        stop_date += timedelta(60)
    return


def merge(directory, output_filepath):
    """Merge all TSV files in a directory into one CSV file."""
    files = [f for f in os.listdir(directory) if f.endswith('.tsv')]
    products = pd.read_csv(os.path.join(directory, files[0]), delimiter='\t')
    for f in files[1:]:
        chunk = pd.read_csv(os.path.join(directory, f), delimiter='\t')
        products = pd.concat([products, chunk])
    products.to_csv(output_filepath)
    for f in files:
        os.remove(f)
    return


if __name__ == '__main__':
    DATA_DIR = os.path.abspath('../data')

    # ERS-1 and 2. Multiple queries are required.
    for collection in ['SAR_IMP_1P', 'SAR_IMS_1P']:
        collection_dir = os.path.join(DATA_DIR, collection)
        os.makedirs(collection_dir, exist_ok=True)
        begin_date = datetime(1991, 1, 1)
        end_date = datetime(2011, 12, 31)
        retrieve_indexes(collection, collection_dir,
                         begin_date=begin_date, end_date=end_date)
        merge(collection_dir, os.path.join(DATA_DIR, collection + '.csv'))
        shutil.rmtree(collection_dir)

    # Envisat. Can be retrieved with a single query per collection.
    for collection in ['ASA_IMP_1P', 'ASA_IMP_1P']:
        response = query(
            search_url=SEARCH_URL.format(collection=collection),
            start_date='', stop_date='',
            max_lat='', max_lon='', min_lat='', min_lon='',
            max_results=50, orbit='', polarisations='', swath='')
        with open(os.path.join(DATA_DIR, collection + '.tsv'), 'w') as f:
            f.write(response.text)
        products = pd.read_csv(os.path.join(DATA_DIR, collection + '.tsv'), delimiter='\t')
        products.to_csv(os.path.join(DATA_DIR, collection + '.csv'))
        os.remove(os.path.join(DATA_DIR, collection + '.tsv'))
