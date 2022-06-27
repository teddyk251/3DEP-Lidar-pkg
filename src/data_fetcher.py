import pdal
import json
import pandas as pd
import sys
import numpy as np
import geopandas as gpd
from shapely.geometry import Polygon, Point

BASE_DATA_URL = "https://s3-us-west-2.amazonaws.com/usgs-lidar-public/"


class DataFetcher():

    """Data Fetcher Class which handles all data fetching activites from the AWS dataset.

    Parameters
    ----------
    polygon : Polygon
        Polygon of the area which is being searched for
    epsg : str
        CRS system which the polygon is constructed based on
    region: str, optional
        Region where the specified polygon is located in from the file name folder located in the AWS dataset. If
        not provided the program will search and provide the region if it is in the AWS dataset
    """

    def __init__(self, polygon: Polygon, epsg: str, region: str) -> None:
        minx, miny, maxx, maxy = self.get_polygon_bounds(polygon, epsg)
        self.epsg = epsg
        if (region):
            self.region = self.check_region(region)
            self.file_path = BASE_DATA_URL + self.region + "/ept.json"
        else:
            self.region = self.get_region_from_bounds(minx, miny, maxx, maxy)


        

    def get_polygon_bounds(self, polygon: Polygon, epsg: str) -> tuple:
        """Extracts polygon bounds and assign polygon cropping bounds.

        Parameters
        ----------
        polygon : Polygon
            Polygon object describing the boundary of the location required
        epsg : str
            CRS system on which the polygon is constructed on

        Returns
        -------
        tuple
            Returns bounds of the polygon provided(minx, miny, maxx, maxy)
        """
        try:
            grid = gpd.GeoDataFrame([polygon], columns=["geometry"])
            grid.set_crs(epsg=epsg, inplace=True)

            grid['geometry'] = grid.geometry.to_crs(epsg=3857)

            minx, miny, maxx, maxy = grid.geometry[0].bounds
            # bounds: ([minx, maxx], [miny, maxy])
            self.extraction_bounds = f"({[minx, maxx]},{[miny,maxy]})"

            # Cropping Bounds
            self.polygon_cropping = self.get_crop_polygon(grid.geometry[0])

            grid['geometry'] = grid.geometry.to_crs(epsg=epsg)
            self.geo_df = grid

            # logger.info(
            #     'Successfully Extracted Polygon Edges and Polygon Cropping Bounds')

            return minx, miny, maxx, maxy

        except Exception as e:
            print(e)
            # logger.exception(
            #     'Failed to Extract Polygon Edges and Polygon Cropping Bounds')

    def check_region(self, region: str) -> str:
        """Checks if the given region is found in the AWS dataset.

        Parameters
        ----------
        region : str
            Proabable file name of a folder in the AWS dataset

        Returns
        -------
        str
            Returns the same regions folder file name if it was successfully located
        """
        with open('./filename.txt', 'r') as locations:
            locations_list = locations.readlines()

        if(region in locations_list):
            return region
        else:
            print("Region Not Available")
            # logger.error('Region Not Available')
            sys.exit(1)

    def get_region_from_bounds(self, minx: float, miny: float, maxx: float, maxy: float, indx: int = 1) -> str:
        """Searchs for a region which contains the polygon defined from the available boundaries in the AWS 
        dataset.

        Parameters
        ----------
        minx : float
            Minimum longitude value of the polygon
        miny : float
            Minimum latitude value of the polygon
        maxx : float
            Maximum longitude value of the polygon
        maxy : float
            Maximum latitude value of the polygon
        indx : int, optional
            Bound indexing, to select the first or other access url's of multiple values for a region
        Returns
        -------
        str
            Access url to retrieve the data from the AWS dataset
        """

        aws_dataset_info_csv = pd.read_csv('./aws_dataset.csv')
        for index, bound in enumerate(aws_dataset_info_csv['Bound/s'].to_list()):
            bound = bound.strip('][').replace(
                ']', '').replace('[', '').split(',')
            bound = list(map(float, bound))

            bminx, bminy, bmaxx, bmaxy = bound[0 * indx], bound[1 *
                                                                indx], bound[3 * indx], bound[4 * indx]

            if((minx >= bminx and maxx <= bmaxx) and (miny >= bminy and maxy <= bmaxy)):
                access_url = aws_dataset_info_csv['Access Url/s'].to_list()[
                    index][2:-2]

                region = aws_dataset_info_csv['Region/s'].to_list()[
                    index] + '_' + aws_dataset_info_csv['Year/s'].to_list()[index][2:-2]

                print(f'Region found in {region} folder')
                # logger.info(f'Region found in {region} folder')

                return access_url
        else:
            print('Region Not Available')
            # logger.error('Region Not Available')
            sys.exit()
