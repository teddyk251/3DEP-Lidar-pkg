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

        self.load_pipeline_template()

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

    def get_crop_polygon(self, polygon: Polygon) -> str:
        """Calculates Polygons Cropping string used when building Pdal's crop pipeline.

        Parameters
        ----------
        polygon: Polygon
            Polygon object describing the boundary of the location required

        Returns
        -------
        str
            Cropping string used by Pdal's crop pipeline
        """
        polygon_cords = 'POLYGON(('
        for i in list(polygon.exterior.coords):
            polygon_cords += f'{i[0]} {i[1]},'

        polygon_cords = polygon_cords[:-1] + '))'

        return polygon_cords

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
        with open('../data/region_list.txt', 'r') as locations:
            locations_list = []
            for location in locations:
                locations_list.append(location.strip('\n').strip('/'))
        # print(locations_list)
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

    def load_pipeline_template(self, file_name: str = '../data/pipeline_template.json') -> None:
        """Loads Pipeline Template to constructe Pdal Pipelines from.

        Parameters
        ----------
        file_name : str, optional
            Path plus file name of the pipeline template if the template is not located in its normal locations,
            or if another template file is needed to be loaded

        Returns
        -------
        None
        """
        try:
            with open(file_name, 'r') as read_file:
                template = json.load(read_file)

            self.template_pipeline = template

            print('Pipeline Template loaded successfully')
            # logger.info('Successfully Loaded Pdal Pipeline Template')

        except Exception as e:
            print('Failed to Load Pipeline Template')
            # logger.exception('Failed to Load Pdal Pipeline Template')
            sys.exit(1)

    def build_pipeline(self) -> None:
        """Generates a generic Pdal pipeline.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        self.pipeline = []
        reader = self.template_pipeline['reader']
        reader['bounds'] = self.extraction_bounds
        reader['filename'] = self.file_path
        self.pipeline.append(reader)

        cropper = self.template_pipeline['cropping_filter']
        cropper['polygon'] = self.polygon_cropping
        self.pipeline.append(cropper)

        self.pipeline.append(self.template_pipeline['range_filter'])
        self.pipeline.append(self.template_pipeline['assign_filter'])

        reprojection = self.template_pipeline['reprojection_filter']
        reprojection['out_srs'] = f"EPSG:{self.epsg}"
        self.pipeline.append(reprojection)

        self.pipeline = pdal.Pipeline(json.dumps(self.pipeline))

    def create_cloud_points(self):
        """Creates Cloud Points from the retrieved Pipeline Arrays consisting of other unwanted data.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        try:
            cloud_points = []
            for row in self.pipeline.arrays[0]:
                lst = row.tolist()[-3:]
                cloud_points.append(lst)

            cloud_points = np.array(cloud_points)

            self.cloud_points = cloud_points

        except:
            print('Failed to create cloud points')
            sys.exit(1)

    def fetch_data(self):
        """Fetches Data from the AWS Dataset, builds the cloud points from it and 
        assignes and stores the original cloud points and original elevation geopandas dataframe.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        try:
            self.data_count = self.pipeline.execute()
            self.create_cloud_points()
            self.original_cloud_points = self.cloud_points
            self.original_elevation_geodf = self.get_elevation_geodf()
        except Exception as e:
            sys.exit(1)

    def get_elevation_geodf(self) -> gpd.GeoDataFrame:
        """Calculates and returns a geopandas elevation dataframe from the cloud points generated before.

        Parameters
        ----------
        None

        Returns
        -------
        gpd.GeoDataFrame
            Geopandas Dataframe with Elevation and coordinate points referenced as Geometry points
        """
        elevation = gpd.GeoDataFrame()
        elevations = []
        points = []
        for row in self.cloud_points:
            elevations.append(row[2])
            point = Point(row[0], row[1])
            points.append(point)

        elevation['elevation'] = elevations
        elevation['geometry'] = points
        elevation.set_crs(epsg=self.epsg, inplace=True)

        self.elevation_geodf = elevation

        return self.elevation_geodf
