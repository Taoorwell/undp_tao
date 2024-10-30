# load used python packages
import os 
import subprocess
from glob import glob
import numpy as np
from osgeo import gdal, ogr
import geopandas as gpd

# define some variables used after
image_files_dir = r'Monthly/'
output_file = r'mean_no2_moldova.tif'
moldova_shape = r'moldova.shp'

# a. a function for finding the files in the directory 
def find_files(directory):
    # using glob to get all tif files downloaded in Monthly folder 
    images_path = sorted(glob(directory + r'*.tif'))
    return images_path

# b. calculate the mean values of 12 months and write out the image for resample and clip later
def calculate_mean_and_write_out(images_path, output_file):
    # reading 12 image using gdal and caculate mean image using numpy
    image_array_list = []
    for image_path in images_path:
        dataset = gdal.Open(image_path)
        image_array_list.append(dataset.ReadAsArray())
    mean_image_array = np.mean(np.array(image_array_list), axis=0)
    
    # writing out mean image using gdal package and geotransformation and projection of download images
    (y_size, x_size) = mean_image_array.shape
    print(f'mean image shape: {(y_size, x_size)}')
    driver = gdal.GetDriverByName('GTiff')
    output_image = driver.Create(output_file, x_size, y_size, 1, gdal.GDT_Float32)
    
    output_image.SetGeoTransform(dataset.GetGeoTransform())
    output_image.SetProjection(dataset.GetProjection())
    
    output_image.GetRasterBand(1).WriteArray(mean_image_array)
    output_image.GetRasterBand(1).SetNoDataValue(-9999)
    output_image.FlushCache()
    

if __name__ == "__main__":
    # a finding images
    print('Finding downloaded files:')
    images_path = find_files(image_files_dir)
    print(images_path)
    
    # b calculating mean 
    print('Calculating mean and write out')
    calculate_mean_and_write_out(images_path=images_path, output_file=output_file)
    print('mean no2 moldova file saved!')
    
    # c using gdal_translate for resample
    print('Using gdal_translate and gdalwarp for resampling and clipping')
    subprocess.run(r'gdal_translate -of GTiff -tr 2000 2000 mean_no2_moldova.tif mean_no2_moldova_2000.tif')
    print('mean no2 moldova 2000 saved!')
    
    # d using gdal_warp for clip 
    subprocess.run(r'gdalwarp -cutline moldova.shp -crop_to_cutline mean_no2_moldova_2000.tif mean_no2_moldova_2000_clip.tif')
    print('mean no2 moldova 2000 clip saved!')

    print('Finish!')