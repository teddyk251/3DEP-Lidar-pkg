from logging import log
from urllib.request import urlopen
from json import dump, loads
from time import sleep
import pandas as pd
import sys
from copy import copy


def get_info(url_str: str) -> tuple:
    """Retrieve ept.json information from the AWS storage using python urlopen request

    Parameters
    ----------
    url_str : str
        URL to the ept.json file.

    Returns
    -------
    tuple
        A tuple with bounds, numbers of points, reprojection and schema information extracted from the ept.json file.
    """
    try:
        # store the response of URL
        response = urlopen(url_str)
        # storing the JSON response
        # read data from response
        data_json = loads(response.read())

        return_data = data_json['bounds'], data_json['points']

        print(
            'Successfully Read and Retrieved Data Information from EPT.JSON File')

        # return extracted values
        return return_data

    except Exception as e:
        print('Failed To Read EPT.JSON File From URL')
        sys.exit(1)


def generate_dataset_metadata_json(directories_path: str = './data/region_list.txt', save: bool = False) -> dict:
    """Construct AWS Dataset Data Information. It extracts and identifies similar locations and organize them
    properly. It can also save the generated JSON file if needed.

    Parameters
    ----------
    directories_path : str, optional
        Path plus filename of the text file which contains the names of folders which are located in the AWS dataset storage.
        If filename of the directories is not given providing the file location is a must.
    save: bool, optional
        To save the generated json file in the same directory where the function was called.
    Returns
    -------
    dict
        The generated AWS Data Information in a json/dictionary format.
    """

    main_url = "https://usgs-lidar-public.s3.us-west-2.amazonaws.com/"

    dataset_json = {}

    with open('./filename.txt', 'r') as locations:
        locations_list = locations.readlines()

    for index, location in enumerate(locations_list):
        try:
            location = location.replace('\n', "")[:-1]
            folder_url = main_url + location + '/ept.json'
            bound, points, reprojection, schema = get_info(folder_url)
            location = location.split('_')
            if('LAS' in location and location[location.index('LAS') - 1].isnumeric()):
                file_name = '_'.join(location[:-3])
                year = location[-3] + '-' + location[-1]
            else:
                file_name = '_'.join(location[:-1])
                year = location[-1]

            if(file_name not in dataset_json.keys()):
                new_file = {}
                new_file['bounds'] = [bound]
                new_file['years'] = [year]
                new_file['points'] = [points]
                new_file['access_url'] = [folder_url]
                new_file['len'] = 1
                dataset_json[file_name] = new_file

            else:
                dict_value = dataset_json[file_name]
                dict_value['bounds'].append(bound)
                dict_value['years'].append(year)
                dict_value['points'] = [points]
                dict_value['access_url'].append(folder_url)
                dict_value['len'] = dict_value['len'] + 1

                dataset_json.update({file_name: dict_value})

            print(index, end=', ')
            if(index % 100 == 0):
                sleep(5)

        except Exception as e:
            print('Failed To retrieve:\n\tfile_index -> ', index)
            print("Reason:\n\t -> ", e)
            continue

    if(save):
        with open('./aws_dataset_info.json', 'w') as file_handler:
            dump(dataset_json, file_handler, sort_keys=True, indent=4)
    print('Successfully generated Data Information JSON File')

    return dataset_json





if __name__ == "__main__":
    final = generate_dataset_metadata_json()
    df = fix_bound_reptition_and_build_csv(final, save=False)
