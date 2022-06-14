#!/usr/bin/env python3
"""Python program to convert TDC Wholesale DSL net data excel to KML."""
import argparse
from typing import Any, Dict, List, Tuple

import pandas as pd  # type: ignore
import simplekml  # type: ignore
from pyproj import Transformer


def utm32ed50_to_wgs84(coord_x: int, coord_y: int) -> Tuple[float, float]:
    """Transform coordinates.

    TDC uses an utm32ed50 (EPSG:23032) projection and KML uses WGS84 (EPSG:4326)
    """
    transformer = Transformer.from_crs("EPSG:23032", "EPSG:4326")

    coords = transformer.transform(coord_x, coord_y)
    if coords is None:
        return (0.0, 0.0)
    return coords


def read_spreadsheet(filename: str) -> Tuple[Dict[str, str], Dict[str, str]]:
    """Read the TDC spreadsheet and parse needed sheets.

    Return the first sheet (info) and the "Adresser og koordinater" sheet
    """
    info_sheet = pd.read_excel(filename, sheet_name="INFO")
    centraloffices_sheet = pd.read_excel(filename, sheet_name="Adresser og koordinater")

    return info_sheet.to_dict("records"), centraloffices_sheet.to_dict("records")


def find_spreadsheet_date(info_sheet_dict: Dict[Any, str]) -> str:
    """Overly complicated way to get date of the spreadsheet."""
    # set date to something
    date: str = "00-00-0000"
    for row in info_sheet_dict:
        if "Denne udgave viser status pr" in str(row["Oversigt over lister"]):
            excel_date: List[str] = row["Oversigt over lister"].split(": ")
            date = excel_date[1]
    return date


def generate_filename(document_date: str, args: Any) -> str:
    """Generate a filename depending on CLI arguments."""
    if args.output_file:
        return str(args.output_file)
    return f"tdc-{document_date}"


def parse_args() -> Any:
    """Use argparse to parse commandline arguments."""
    # Create the parser
    parser = argparse.ArgumentParser(description="Convert TDC xsls to kml files")
    parser.add_argument(
        "-i",
        "--input-file",
        action="store",
        type=str,
        required=True,
        help="Input file name, usually 0214_Wholesale_DSL_net_data_$date.xsls",
    )
    parser.add_argument(
        "-o",
        "--output-file",
        action="store",
        type=str,
        help="Outfile file name, without the file suffix (default: tdc-$document_date)",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="Add verbose output while running",
    )
    parser.add_argument(
        "-k",
        "--kml",
        action="store_true",
        default=False,
        help="Output kml format, uncompressed (default: kmz)",
    )

    return parser.parse_args()


def generate_kml(
    document_date: str, central_offices_dict: Any, filename: str, args: Any
) -> None:
    """Generate KML file."""
    # Start generating the KML file
    # Create simpleKML object
    kml = simplekml.Kml()
    kml.document.name = f"TDC sites from {document_date}"

    # Generate folders for the different house types
    folder_dict = {
        "Centralbygning": kml.newfolder(name="Centralbygning"),
        "Teknikhus": kml.newfolder(name="Teknikhus"),
        "Teknikrum": kml.newfolder(name="Teknikrum"),
        "Teknikskab": kml.newfolder(name="Teknikskab"),
        "Misc": kml.newfolder(name="Misc"),
    }

    # loop through all COs
    for central_office in central_offices_dict:
        # Create folders for different house types, also include a misc if soemthing new shows up
        if central_office["Hustype"] == "Centralbygning":
            folder = folder_dict["Centralbygning"]
        elif central_office["Hustype"] == "Teknikhus":
            folder = folder_dict["Teknikhus"]
        elif central_office["Hustype"] == "Teknikrum":
            folder = folder_dict["Teknikrum"]
        elif central_office["Hustype"] == "Teknikskab":
            folder = folder_dict["Teknikskab"]
        else:
            folder = folder_dict["Misc"]
        # get coordinates
        (latitude, longitude) = utm32ed50_to_wgs84(
            central_office["X-koordinat"], central_office["Y-koordinat"]
        )
        # If debug is set print out house name, type and CMP category
        if args.verbose:
            print(
                f"Hus: {central_office['Hus']}, "
                f"Hus type: {central_office['Hustype']}, "
                f"CMP Kategori: {central_office['CMP kategori']}, "
                f"Coords: {latitude}, {longitude}"
            )
        # Create an address variable because we are using it twice
        address: str = (
            f"{central_office['Gadenavn']} {central_office['Nr']}, "
            f"{central_office['Post nr.']} {central_office['Post distrikt']}"
        )
        pnt = folder.newpoint()
        pnt.name = central_office["Hus"]
        # pnt.coords needs the coordinates in the order longitude then latitude
        pnt.coords = [(longitude, latitude)]
        pnt.address = address
        pnt.description = (
            f"Forkortelse: {(central_office['Fork'])}\n"
            f"Adresse: {address}\n"
            f"Hus type: {central_office['Hustype']}\n"
            f"CMP Kategori: {central_office['CMP kategori']}\n"
            f"NGA: {central_office['NGA']}\n"
            f"Vectoring: {central_office['Vectoring']}\n"
            f"Dæmpning: {central_office['Dæmpn.']}\n"
            f"Kernepunkt: {central_office['Kernepunkt']}"
        )

    if args.kml:
        if args.verbose:
            print(f"Saving KML file, {filename}.kml")
        kml.save(filename + ".kml")
    else:
        if args.verbose:
            print(f"Saving KMZ file, {filename}.kmz")
        kml.savekmz(filename + ".kmz")


def main() -> None:
    """Main function to collect all data and write the final KML file."""
    # parse command line arguments
    args = parse_args()
    # read the input file and out info and central offices
    info, centraloffices = read_spreadsheet(args.input_file)
    # use the info sheet to find the document date
    document_date: str = find_spreadsheet_date(info)
    #
    filename: str = generate_filename(document_date, args)
    # Generate KML file
    generate_kml(document_date, centraloffices, filename, args)


if __name__ == "__main__":
    main()
