# Scraping ESA Online Catalogue

Python scripts to scrape the [ESA Online
Catalogue](http://esar-ds.eo.esa.int/sxcat) into a local SQLite database, in
order to perform local queries on the available `ERS-1`, `ERS-2`, or `Envisat`
Level-1 products.

The following collections are scraped:

* `ASA_IMP_1P`: Level 1 products for ENVISAT ASAR Image Mode Precision Image.
* `ASA_IMS_1P`: Level 1 products for ENVISAT ASAR Image Mode Single-Look
  Complex.
* `SAR_IMP_1P`: Level 1 products for ERS SAR Precision Image.
* `SAR_IMS_1P`: Level 1 products for ERS SAR Single-Look Complex.

However, the code can easily be adapted to scrap other available collections
such as Level-0 products.

## Data

A dump of the resulting database is available here:
[`catalog.db`](http://data.yannforget.me/asarapi/catalog.db).

Individual CSV files for each collection are also available:

* [`ASA_IMP_1P`](http://data.yannforget.me/asarapi/ASA_IMP_1P.csv)
* [`ASA_IMS_1P`](http://data.yannforget.me/asarapi/ASA_IMS_1P.csv)
* [`SAR_IMP_1P`](http://data.yannforget.me/asarapi/SAR_IMP_1P.csv)
* [`SAR_IMS_1P`](http://data.yannforget.me/asarapi/SAR_IMS_1P.csv)

## Columns in the SQLite database

* `id`: product identifier ;
* `date`: acquisition date in Unix timestamp format ;
* `polarisation`: polarisation channels (VV or VH) ;
* `orbit`: orbit direction (ascending or descending) ;
* `platform`: platform short name (ERS or Envisat) ;
* `url`: download URL.

