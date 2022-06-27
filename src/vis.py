import matplotlib.pyplot as plt
from typing import Tuple

class Vis:

    def __init__(self, elevation_geodf, cloud_points) -> None:
        self.elevation_geodf = elevation_geodf
        self.cloud_points = cloud_points


    def get_terrain_map(self, markersize: int = 10, fig_size: Tuple[int, int] = (15, 20)) -> plt:
        """Constructs a Terrain Map from the cloud points.

        Parameters
        ----------
        markersize : int, optional
            Marker size used when ploting the figure
        fig_size : Tuple[int, int], optional
            Size of the figure to be returned

        Returns
        -------
        plt
            Returns a Terrain Map constructed from the cloud points
        """

        self.elevation_geodf.plot(c='elevation', scheme="quantiles", cmap='terrain', legend=True,
                                  markersize=markersize,
                                  figsize=(fig_size[0], fig_size[1]),
                                  missing_kwds={
                                    "color": "lightgrey",
                                    "edgecolor": "red",
                                    "hatch": "///",
                                    "label": "Missing values"}
                                  )

        plt.title('Terrain Elevation Map')
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')

        return plt

    def get_scatter_plot(self, factor_value: int = 1, view_angle: Tuple[int, int] = (0, 0)) -> plt:
        """Constructs a scatter plot graph of the cloud points.

        Parameters
        ----------
        factor_value : int, optional
            Factoring value if the data points are huge
        view_angle : tuple(int, int), optional
            Values to change the view angle of the 3D projection

        Returns
        -------
        plt
            Returns a scatter plot grpah of the cloud points
        """

        values = self.cloud_points[::factor_value]

        fig = plt.figure(figsize=(10, 15))

        ax = plt.axes(projection='3d')

        ax.scatter3D(values[:, 0], values[:, 1],
                     values[:, 2], c=values[:, 2], s=0.1, cmap='terrain')

        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        ax.set_zlabel('Elevation')

        ax.set_title('Elevation Scatter Plot')

        ax.view_init(view_angle[0], view_angle[1])

        return plt

