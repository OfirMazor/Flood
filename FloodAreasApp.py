import ee
ee.Initialize()
import geemap
import pandas as pd
import streamlit as st

headContainer = st.container()
paramsContainer = st.container()
visContainer = st.container()

with headContainer:
    st.title('Mapping Flood Areas Over Israel with SAR Data')
    st.text('Case of winter 2019')

    
israel_ee = ee.FeatureCollection('USDOS/LSIB/2017').filterMetadata('COUNTRY_NA', 'equals', 'Israel')

collection = ee.ImageCollection('COPERNICUS/S1_GRD') \
                .filterBounds(israel_ee) \
                .filter(ee.Filter.listContains('transmitterReceiverPolarisation', 'VV')) \
                .select('VV')

before = collection.filterDate('2019-02-27', '2020-03-01').mosaic().clip(israel_ee)
after = collection.filterDate('2019-02-03', '2019-03-06').mosaic().clip(israel_ee)

DIFF_UPPER_THRESHOLD = -3 

with paramsContainer:
    st.text('')
    st.text('')
    st.header('Parametrs Definition:')
    
    smoothingRadius = st.slider('Set radius (meters)', 20, 500, 100, step=10)
    st.text('')
    
    kernelType = st.selectbox('Set kernel type', ('circle', 'square', 'cross', 'plus', 'octagon', 'diamond'))
    st.text('')
    
diff_smoothed = after.focal_median(smoothingRadius, kernelType , 'meters') \
                      .subtract(before.focal_median(smoothingRadius, kernelType, 'meters'))

diff_thresholded = diff_smoothed.lt(DIFF_UPPER_THRESHOLD)



floodMap = geemap.Map(basemap='SATELLITE', center=[31.0, 34.8], zoom=7.5, add_google_map=False)
floodMap.addLayer(before, {min:-30,max:0}, 'Before Flood', shown=True)
floodMap.addLayer(after, {min:-30,max:0}, 'After Flood', shown=True)
floodMap.addLayer(diff_smoothed, {min:-10,max:10}, 'After-Before Difference (Smoothed)', shown=True)
floodMap.addLayer(diff_thresholded.updateMask(diff_thresholded),{'palette':"0000FF"},'Flooded Areas', shown=True)

with visContainer:
    st.text('')
    st.header('Flood Interactive Map')
    st.text('Blue areas indicate flood locations')
    floodMap.to_streamlit(width=750, hight=1000)
    st.text('Layers description: \n Before & After Flood images represnts unprocessed SAR data, \n Difference (Smoothed) image is the difference between the two dates of the flood event \n and Flooded Areas are selected pixels (blue) with a threshold = -3')
    st.text('')