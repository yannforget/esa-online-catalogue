"""Insert all CSV into a single sqlite database."""


import os
import sqlite3
from datetime import datetime
import dateutil.parser

from shapely.geometry import Polygon
from shapely import wkt
import pandas as pd


# Subset of columns to keep
COLUMNS = [
    'productId',
    'beginAcquisition',
    'platformShortName',
    'swathIdentifier',
    'orbitDirection',
    'footprint',
    'productURI',
    'polarisationChannels',
]


def polygon_from_footprint(footprint):
    """Convert geometry string provided in the ESA catalogue to WKT."""
    coords = [float(coord) for coord in footprint.split(' ')]
    points = []
    for i in range(0, len(coords), 2):
        points.append((coords[i], coords[i+1]))
    polygon = Polygon(points)
    return wkt.dumps(polygon, rounding_precision=6)


def timestamp_from_string(datestring):
    """ISO 8601 datestring to UNIX timestamp integer."""
    date = dateutil.parser.parse(datestring)
    return int(date.timestamp())


DATA_DIR = os.path.abspath('.')

conn = sqlite3.connect(os.path.join(DATA_DIR, 'catalog.db'))
conn.enable_load_extension(True)
conn.execute('SELECT load_extension("mod_spatialite");')
conn.execute('SELECT InitSpatialMetadata(1);')
conn.commit()
c = conn.cursor()
c.execute("CREATE TABLE products(id CHARACTER(59) PRIMARY KEY, date INTEGER, platform TEXT, swath TEXT, orbit TEXT, url TEXT, polarisation TEXT)")
c.execute("SELECT AddGeometryColumn('products', 'geom', 4326, 'POLYGON', 'XY');")
conn.commit()

for collection in ['SAR_IMP_1P', 'SAR_IMS_1P', 'ASA_IMP_1P', 'ASA_IMS_1P']:
    products = pd.read_csv(os.path.join(DATA_DIR, collection + '.csv'), usecols=COLUMNS)
    products.drop_duplicates('productId', inplace=True)
    data = zip(
        products.productId, products.beginAcquisition.map(timestamp_from_string),
        products.platformShortName, products.swathIdentifier,
        products.orbitDirection, products.productURI,
        products.polarisationChannels, products.footprint.map(polygon_from_footprint))
    c.executemany("INSERT INTO products (id, date, platform, swath, orbit, url, polarisation, geom) VALUES (?, ?, ?, ?, ?, ?, ?, GeomFromText(?, 4326));", data)
    conn.commit()
    print(collection + ' sucessfully imported.')

c.execute("SELECT CreateSpatialIndex('products', 'geom');")
conn.commit()
conn.close()
