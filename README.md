# 3DEP-Lidar-pkg

> A Python package for retrieving 3DEP's geospatial data and enable users to easily manipulate, transform, subsample and visualize the data. It supports geographic elevation data at the moment and will support more in the future.
<hr>

# Table of Contents
* [Documentation](#documentation)
* [Description](#description)
* [How to Install](#install)

# <a name='documentaion'></a>Code Documentation
https://teddyk251.github.io/3DEP-Lidar-pkg/

# <a name='description'></a>Problem Description

How much maize a field produces is very spatially variable. Even if the same farming practices, seeds and fertilizer are applied exactly the same by machinery over a field, there can be a very large harvest at one corner and a low harvest at another corner. We would like to be able to better understand which parts of the farm are likely to produce more or less maize, so that if we try a new fertilizer on part of this farm, we have more confidence that any differences in the maize harvest 9are due mostly to the new fertilizer changes, and not just random effects due to other environmental factors.

Water is very important for crop growth and health. We can better predict maize harvest if we better understand how water flows through a field, and which parts are likely to be flooded or too dry. One important ingredient to understanding water flow in a field is by measuring the elevation of the field at many points. The USGS recently released high resolution elevation data as a lidar point cloud called USGS 3DEP in a public dataset on Amazon. This dataset is essential to build models of water flow and predict plant health and maize harvest.  


<hr>   



# <a name='install'></a>Installation  



```
git clone https://github.com/teddyk251/3DEP-Lidar-pkg.git
cd 3DEP-Lidar-pkg/
pip install .
