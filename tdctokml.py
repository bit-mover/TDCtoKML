#!/usr/bin/env python3
"""Python program to convert TDC Wholesale DSL net data excel to KML."""
import argparse
from typing import Tuple

import pandas as pd
import simplekml
from pyproj import Transformer


def utm32ed50_to_wgs84(coord_x: int, coord_y: int) -> Tuple[float, float]:
    """Transform coordinates.

    TDC uses an utm32ed50 (EPSG:23032) projection and we need it in WGS84 (EPSG:4326)
    """
    # Transform from utm32ed50 (EPSG:23032) projection
    # from TDC excel sheet to WGS84 (EPSG:4326)
    transformer = Transformer.from_crs("EPSG:23032", "EPSG:4326")

    lat, lon = transformer.transform(coord_x, coord_y)
    return lon, lat


def read_spreadsheet(filename: str):
    """Read the TDC spreadsheet and parse needed sheets.

    Return the first sheet (info) and the "Adresser og koordinater" sheet
    """
    info_sheet = pd.read_excel(filename, sheet_name="INFO")
    centraloffices_sheet = pd.read_excel(filename, sheet_name="Adresser og koordinater")

    return info_sheet, centraloffices_sheet


def find_spreadsheet_date(info_sheet) -> str:
    """Overly complicated way to get date of the spreadsheet."""
    # set date to something
    # TODO: consider getting the date from the filename instead
    date: str = "00-00-0000"
    info_list: dict = info_sheet.to_dict("records")
    for row in info_list:
        if "Denne udgave viser status pr" in str(row["Oversigt over lister"]):
            excel_date: str = row["Oversigt over lister"].split(": ")
            date = excel_date[1]
    return date


# Create the parser
parser = argparse.ArgumentParser(description="Convert TDC xsls to kml files")
parser.add_argument("-i", "--input-file", action="store", type=str, required=True)
parser.add_argument("-o", "--output-file", action="store", type=str, default="tdc.kml")
parser.add_argument("-d", "--debug", action="store_true", default=False)
args = parser.parse_args()

# read the input file and out info and central offices
info, centraloffices = read_spreadsheet(args.input_file)

# use the info sheet to find the document date
document_date: str = find_spreadsheet_date(info)

# Start generating the KML file
# Create simpleKML object
kml = simplekml.Kml()
kml.document.name = f"TDC sites from {document_date}"

# Generate a dictionary from the central offices output
co_dict = centraloffices.to_dict("records")

# Generate folders for the different house types
folder_centralbygning = kml.newfolder(name="Centralbygning")
folder_teknikhus = kml.newfolder(name="Teknikhus")
folder_teknikrum = kml.newfolder(name="Teknikrum")
folder_teknikskab = kml.newfolder(name="Teknikskab")
folder_misc = kml.newfolder(name="misc")

# loop through all COs
for co in co_dict:
    # Create folders for different house types, also include a misc if soemthing new shows up
    if co["Hustype"] == "Centralbygning":
        folder = folder_centralbygning
    elif co["Hustype"] == "Teknikhus":
        folder = folder_teknikhus
    elif co["Hustype"] == "Teknikrum":
        folder = folder_teknikrum
    elif co["Hustype"] == "Teknikskab":
        folder = folder_teknikskab
    else:
        folder = folder_misc
    # If debug is set print out house name, type and CMP category
    if args.debug:
        print(
            f"Hus: {co['Hus']}, Hus type: {co['Hustype']}, CMP Kategori: {co['CMP kategori']}"
        )
    longitude, latitude = utm32ed50_to_wgs84(co["X-koordinat"], co["Y-koordinat"])
    pnt = folder.newpoint()
    pnt.name = co["Hus"]
    pnt.coords = [(longitude, latitude)]
    pnt.address = f"{co['Gadenavn']} {co['Nr']}, {co['Post nr.']} {co['Post distrikt']}"
    pnt.description = (
        f"Forkortelse: {(co['Fork'])}\n"
        f"Adresse: {co['Gadenavn']} {co['Nr']}, {co['Post nr.']} {co['Post distrikt']}\n"
        f"Hus type: {co['Hustype']}\n"
        f"CMP Kategori: {co['CMP kategori']}\n"
        f"NGA: {co['NGA']}\n"
        f"Vectoring: {co['Vectoring']}\n"
        f"dæmpning: {co['Dæmpn.']}\n"
        f"Kernepunkt: {co['Kernepunkt']}"
    )
kml.save(args.output_file)
