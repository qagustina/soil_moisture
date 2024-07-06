import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import datetime
import os


def get_datadir():
    return '/mnt/ypy3_5/land/gldas/data/2015/'


def get_fn():
    start_date = '20150301' 
    num_days = 1
    data_dir = get_datadir()
    
    file_paths = []

    for i in range(num_days):
        date_str = (datetime.datetime.strptime(start_date, '%Y%m%d') + datetime.timedelta(days=i)).strftime('%Y%m%d')
        
        for hour in range(0, 24, 3):
            file_name = f'GLDAS_NOAH025_3H.A{date_str}.{hour:02d}00.021.nc4'
            file_path = os.path.join(data_dir, file_name) 
            file_paths.append(file_path)
    
    return file_paths


def read_ncfile(file_path):
    ds = nc.Dataset(file_path)
    return ds


def get_latlon():
    lon_start = -70 
    lon_end = -55   
    lat_start = -38 
    lat_end = -22    
    return lon_start, lon_end, lat_start, lat_end


def read_and_filter_nc_data(file_path, lon_start, lon_end, lat_start, lat_end):
    ds = read_ncfile(file_path)
    lon = ds.variables['lon'][:]
    lat = ds.variables['lat'][:]
    
    # recorte latlon
    lon_indices = np.where((lon >= lon_start) & (lon <= lon_end))
    lat_indices = np.where((lat >= lat_start) & (lat <= lat_end))
    
    soil_data = ds.variables['SoilMoi0_10cm_inst'][:, lat_indices[0], lon_indices[0]]

    return soil_data, lon[lon_indices], lat[lat_indices]


def plot_gif_reg():
    lon_start, lon_end, lat_start, lat_end = get_latlon()
    file_paths = get_fn()
    soil_data, lon_filtered, lat_filtered = read_and_filter_nc_data(file_paths[0], lon_start, lon_end, lat_start, lat_end)


    images = []
    hours = []


    for file_path in file_paths:
        ds = read_ncfile(file_path)
        time_var = ds.variables['time']  
        hours_data = nc.num2date(time_var[:], time_var.units)  
        
        for i, hour in enumerate(hours_data):
            soil_data, lon_filtered, lat_filtered = read_and_filter_nc_data(file_path, lon_start, lon_end, lat_start, lat_end)
            
            
            plt.figure(figsize=(10, 6))
            plt.imshow(soil_data[i, :, :], extent=[lon_filtered[0], lon_filtered[-1], lat_filtered[-1], lat_filtered[0]], cmap='gist_earth_r', aspect='equal')
            plt.colorbar(label="Soil Moisture (kg m-2) = (0,01 m3/m3)")
            plt.xlabel('Longitude',fontsize=9)
            plt.ylabel('Latitude', fontsize=9)
            t = plt.title(f'GLDAS NOAH\nSoil Moisture (0-10cm underground) - {hour.strftime("%Y-%m-%d {%H:%M:%S}")}', fontsize=9, alpha=0.8)
            t.set_fontname('monospace')
            t.set_fontweight('semibold')
            plt.grid(True)
            
            plt.gca().invert_yaxis()
            
            image_name = f'soil_temp_img_{hour.strftime("%Y%m%d%H%M%S")}.png'
            plt.savefig(image_name,  bbox_inches='tight')
            
            
            img = Image.open(image_name)
            images.append(img)
            hours.append(hour)


    images[0].save('soil_hh_day.gif', save_all=True, append_images=images[1:], duration=500, loop=0)


plot_gif_reg()
