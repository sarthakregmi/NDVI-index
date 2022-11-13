
#This code reads the shapefiles and GeoJSON file and downloads the sentinel image of that area

import time
from datetime import date
from sentinelsat import SentinelAPI, read_geojson, geojson_to_wkt
import geopandas as gpd
from PyQt5 import QtWidgets,uic
from PyQt5.QtWidgets import QFileDialog
import rasterio
import numpy
import os
import matplotlib.pyplot as plt

def login():
    user_name = call.usernamebox.text()
    password = call.Passwordbox.text()
    global api
    api = SentinelAPI(user_name , password, 'https://scihub.copernicus.eu/dhus')
    dataimport()

def dataimport():
    #print(Data_path[0])


    #Data_path = call.filepathbox.text()
    global start_date, end_date

    start_date = call.startdatebox.text()
    end_date = call.enddatebox.text()
    global footprint
    if Data_path[0].lower().endswith(('.geojson')):
        print("its geojson")
        footprint = geojson_to_wkt(read_geojson(Data_path[0]))
        #print(footprint)
    elif Data_path[0].lower().endswith(('.shp')):
        #print("its shape file")
        myshpfile = gpd.read_file(Data_path[0])

        footprint = myshpfile.to_file("file.geojson", driver='GeoJSON')
    elif Data_path[0].lower().endswith(('.wkt')):
        footprint = read_wkt(Data_path[0])
    datadownload()
def datadownload():
    if call.sentinel2box.isChecked() == True:
        print("Downloading Sentinel 2 data.")
        products = api.query(footprint, date=(start_date, date(2022,10,21)),platformname='Sentinel-2', cloudcoverpercentage = (0, 30))
        
    if call.sentinel1box.isChecked() == True:
        print("Downloading sentinel 1 data")
        products = api.query(footprint, date =(start_date , end_date), platformname ='Sentinel-1', producttype = 'GRD')
    
    products_df = api.to_dataframe(products)
    products_to_download = products_df.head(1)
    
    api.download_all(products_to_download)


def openFileNameDialog():
    global Data_path

    Data_path = QFileDialog.getOpenFileName(None,'Open File',"","geojson files (*.geojson);;Shape Files (*.shp))")
def getImage():
    global red_path,nir_path
    file_path = QFileDialog.getExistingDirectory(None,'Open File',"")
    granule_path= file_path+"/"+os.listdir(file_path)[2]
    img_path=granule_path+"/"+os.listdir(granule_path)[0]+"/IMG_DATA"
    red_path= img_path+"/"+os.listdir(img_path)[3]
    nir_path= img_path+"/"+os.listdir(img_path)[7]
    
def get_NDVI():

    with rasterio.open(red_path) as src:
        band_red = src.read(1)
    with rasterio.open(nir_path) as src:
        band_nir = src.read(1)
    numpy.seterr(divide='ignore', invalid='ignore')
    ndvi = (band_nir.astype(float) - band_red.astype(float)) / (band_nir + band_red)
    kwargs = src.meta
    kwargs.update(
        dtype=rasterio.float32,
        count = 1)
    plt.title("NDVI Index Map")
    plt.imshow(ndvi, interpolation='nearest')
    plt.colorbar(label='NDVI Value')
    plt.axis('off')
    plt.show()
    plt.imsave("output/ndvi_cmap.png", ndvi, cmap=plt.cm.summer)

if __name__ =='__main__':

     app = QtWidgets.QApplication([])
     call = uic.loadUi('GUI1.ui')
     call.pushButton.clicked.connect(login)
     call.toolButton.clicked.connect(openFileNameDialog)
     call.ndviFolder.clicked.connect(getImage)
     call.getNDVI.clicked.connect(get_NDVI) 
     call.show()
     app.exec()
