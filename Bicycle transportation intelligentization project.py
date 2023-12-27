import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point, Polygon
import cx_Oracle
import os
import streamlit as st
from sklearn.preprocessing import MinMaxScaler

import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point, Polygon, LineString, shape
import cx_Oracle
import os
import re
import math
import datetime as dt
from datetime import datetime, timedelta
city_lat1=29.493391
city_lat2=29.837785
city_long1=52.389580
city_long2=52.6834
city_id='F9CA365EAC7147778517031A42238005'

border=gpd.read_file('cycling_allowed_area.gpkg')
#border=border.drop([''], axis=1)
border=border.dropna()
#Buffering 
#scale: 1 decimal degree= 95271 m
border1 = border.buffer(0.001) #= 28.5813
border1 = gpd.GeoDataFrame().set_geometry(border1)
bgdf=gpd.GeoDataFrame().set_geometry(border1['geometry'])
crs = {'init': 'epsg:4326'}
bgdf.crs=crs

def oracle_connect():
    try:
        os.environ["ORACLE_HOME"] = "C:\instantclient_19_3"
        db = cx_Oracle.connect(user=os.environ["ORACLE_USER"], password=os.environ["ORACLE_PASSWORD"], dsn=os.environ["ORACLE_DSN"],encoding='UTF-8')
        return db

    except cx_Oracle.DatabaseError as ora_exception:
        error, = ora_exception.args
        print("Oracle Error Code: ", error.code)
        print("Oracle Error Message: ", error.message)

db=oracle_connect()


# In[33]:

def sugg_set(cc,sugg):
    if cc<sugg:
        return sugg-cc
   
    else:
        return 0
    
def alarm_set(cc,low,high):
    if cc<low:
        return 1
    elif cc>high:
        return 1
    else:
        return 0


# In[34]:


def diff_set(cc,low,high):
    if cc<low:
        return cc-low
    elif cc>high:
        return cc-high
    else:
        return 0


# In[70]:


def diff_percent(minus_sum,extra_sum,diff):
    if diff>0:
        return (diff/extra_sum)*100
    elif diff<0:
        return (-diff/minus_sum)*100
    else:
        return 0

tab = st.selectbox("Choose a service", ["آلارم پارکینگ","پیشنهاد چیدمان","تعداد دوچرخه خارج از محدوده","پیشنهاد جمع آوری"],key=1)



sql2="""select lock_serial,latitude,longitude from NODOOD.b_lock where lock_status='C'  and latitude between %s and %s and longitude between %s and %s"""%(city_lat1,city_lat2,city_long1,city_long2)
b_lock=pd.read_sql(sql2,db)
sql2="""select bp.latitude , bp.longitude , bp.title from REMOVED.b_parking bp where  city_id ='%s'"""%(city_id)
parking=pd.read_sql(sql2,db)
#parking=pd.read_csv('parking.csv')
parking['index']=parking.index

crs = {'init': 'epsg:4326'}
parking_geo = [Point(xy) for xy in zip(parking.LONGITUDE, parking.LATITUDE)] 
parking_gdf = gpd.GeoDataFrame(parking , crs = crs , geometry = parking_geo) 
parking_buffer = parking_gdf.buffer(0.0008)

lock_geo = [Point(xy) for xy in zip(b_lock.LONGITUDE, b_lock.LATITUDE)] 
lock_gdf = gpd.GeoDataFrame(b_lock , crs = crs , geometry = lock_geo)
parking_buffer_gdf = gpd.GeoDataFrame(gpd.GeoSeries(parking_buffer))
parking_buffer_gdf = parking_buffer_gdf.rename(columns={0:'geometry'}).set_geometry('geometry')
parking_buffer_gdf.crs = crs
parking_buffer_gdf['TITLE']=parking['TITLE']
parking_buffer_gdf['index']=parking.index
parking_status = gpd.sjoin(lock_gdf, parking_buffer_gdf , how = 'right', op = 'within')


# In[72]:


parking_status=parking_status.groupby('index')['index_left'].count().reset_index(name='CC')



analysis=pd.read_excel('shiraz_input.xlsx')




bike_count=400
bike_dispatch=350

result=pd.DataFrame()
result['suggestion12H']=analysis['suggestion12H']
result['TITLE']=analysis['TITLE']
#result['parking capcity']=analysis['CAPACITY']
result['real time']=parking_status['CC']
result['alarm(low)']=analysis['alarm(low)6H']
result['alarm(high)']=analysis['alarm(high)6H']
result=result.round({'alarm(low)':0,'diff':0})
result=result.fillna(0)

result= result.round(0)
result=result.fillna(0)
# In[78]:


result['diff']=result.apply(lambda x: diff_set(x['real time'],x['alarm(low)'],x['alarm(high)']),axis=1)


result_sorted=result.sort_values('diff')
result_sorted=result_sorted.round({'diff':0})

if (tab=="آلارم پارکینگ"):
    st.title('<آلارم پارکینگ>')
    result_sorted.drop(['suggestion12H'],axis = 1,inplace=True)
    result_sorted.drop([29],inplace=True)
    result1=result_sorted.style.hide_index().bar(color=['#d65f5f', '#5fba7d'], subset=['diff'], align='mid')
    # if st.checkbox('Show full Data'): 
    st.table(result1)
# selection = st.multiselect('which Parking?', result_sorted['TITLE'].unique())
# filtered_res=result_sorted[result_sorted['TITLE'].isin(selection)]
# filtered_res=filtered_res.style.hide_index().bar(color=['#d65f5f', '#5fba7d'], subset=['diff'], align='mid')
# #st.title(result_sorted['alarm(low)'].sum())

# # In[83]:


# st.table(filtered_res)

# In[84]:
suggest=pd.DataFrame()
result['dispatch_suggestion']=0
result['dispatch_suggestion']=result.apply(lambda x: sugg_set(x['real time'],x['suggestion12H']),axis=1)
suggest=result[(result['dispatch_suggestion']>0)]
suggest=suggest[['TITLE','dispatch_suggestion']]
suggest=suggest.sort_values('dispatch_suggestion',ascending=False)
suggest=suggest.style.hide_index().bar(color=['#d65f5f'], subset=['dispatch_suggestion'], align='mid')
if (tab=="پیشنهاد چیدمان"):
    st.title('<پیشنهاد چیدمان>')
    st.table(suggest)



sql2="""select bl.sys_time,(CURRENT_TIMESTAMP-bt.end_time) as last_trip,bl.lock_serial,bl.lock_status,bl.longitude ,bl.latitude
from REMOVED.b_lock bl,NODOOD.b_trip bt
where bl.lock_serial in (select rml.lock_serial from NODOOD.rep_monitor_lock rml where  rml.state in ('O'))
and bt.id=bl.last_trip_id
and bt.status in ('P','R')
and bl.sys_time is not null and bl.latitude between 29.5721 and 29.837 and bl.longitude between 52.38 and 52.68 
and bl.lock_status in ('C') order by last_trip desc """
lock_status=pd.read_sql(sql2,db)
lock_geo=[Point(xy) for xy in zip(lock_status.LONGITUDE, lock_status.LATITUDE) ] 
lock_status_gdf=gpd.GeoDataFrame(lock_status,crs=crs,geometry=lock_geo)

# sjoin:
result2=gpd.sjoin(lock_status_gdf,bgdf,how='left',op='within')
result2=result2[result2['index_right']!=1]
result2['LAST_TRIP']=result2['LAST_TRIP']+ dt.timedelta(hours=3,minutes=30)
result2=result2[['SYS_TIME','LAST_TRIP','LOCK_SERIAL']]
result2.rename(columns={'SYS_TIME':'آخرین بروزرسانی وضعیت','LAST_TRIP':'مدت زمان گذشته از اخرین سفر','LOCK_SERIAL':'پلاک دوچرخه'},inplace=True)
if (tab=="تعداد دوچرخه خارج از محدوده"):
    st.title('<تعداد دوچرخه خارج از محدوده>')
    st.title(len(result2.index))
    st.table(result2)
 
 
 
 

#########################################################################################
import pandas as pd
import numpy as np
import cx_Oracle
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
figure(num=None, figsize=(24, 12), dpi=80, facecolor='w', edgecolor='k')
from IPython.display import display, HTML
from folium.plugins import HeatMap
import folium
import osmnx
from h3 import h3


# In[4]:


from folium import Map, Marker, GeoJson
from folium.plugins import MarkerCluster
import branca.colormap as cm
import folium

import matplotlib.pyplot as plt
from IPython.display import Image, display
from IPython.utils.text import columnize
import warnings
warnings.filterwarnings('ignore')


# In[5]:


import json
import pandas as pd
from pandas.io.json import json_normalize
import numpy as np
import datetime as dt
import statistics

from geojson.feature import *
# from area import area

import copy
import streamlit as st


# In[6]:


import cx_Oracle
import os
import numpy as np
import pandas as pd



def oracle_connect():
    try:
        os.environ["ORACLE_HOME"] = "C:/instantclient_19_3"
        db = cx_Oracle.connect(user=os.environ["ORACLE_USER"], password=os.environ["ORACLE_PASSWORD"], dsn=os.environ["ORACLE_DSN"],encoding='UTF-8')
        return db

    except cx_Oracle.DatabaseError as ora_exception:
        error, = ora_exception.args
        print("Oracle Error Code: ", error.code)
        print("Oracle Error Message: ", error.message)
        
db=oracle_connect()


# In[7]:


def df_to_hex_df(df,resolution):
#     df = df[["LATITUDE","LONGITUDE","LOCK_SERIAL"]]
#     if('LOCK_SERIAL' in df.columns):
#         df
        
    df["hex_id"] = df.apply(lambda row: h3.geo_to_h3(row["LATITUDE"], row["LONGITUDE"], resolution), axis = 1)
    df["geometry"] =  df.hex_id.apply(lambda x: 
                                                           {    "type" : "Polygon",
                                                                 "coordinates": 
                                                                [h3.h3_to_geo_boundary(h3_address=x,geo_json=True)]
                                                            }
                                                        )
    return df


# In[8]:


def counts_by_hexagon(df, resolution):
    
    '''Use h3.geo_to_h3 to index each data point into the spatial index of the specified resolution.
      Use h3.h3_to_geo_boundary to obtain the geometries of these hexagons'''

    df = df[["LATITUDE","LONGITUDE"]]
    
    df["hex_id"] = df.apply(lambda row: h3.geo_to_h3(row["LATITUDE"], row["LONGITUDE"], resolution), axis = 1)
    
    df_aggreg = df.groupby(by = "hex_id").size().reset_index()
    df_aggreg.columns = ["hex_id", "value"]
    
    df_aggreg["geometry"] =  df_aggreg.hex_id.apply(lambda x: 
                                                           {    "type" : "Polygon",
                                                                 "coordinates": 
                                                                [h3.h3_to_geo_boundary(h3_address=x,geo_json=True)]
                                                            }
                                                        )
    
    return df_aggreg


# In[9]:


def hexagons_dataframe_to_geojson(df_hex, file_output = None):
    
    '''Produce the GeoJSON for a dataframe that has a geometry column in geojson format already, along with the columns hex_id and value '''
    
    list_features = []
    
    for i,row in df_hex.iterrows():
        feature = Feature(geometry = row["geometry"] , id=row["hex_id"], properties = {"value" : row["value"]})
        list_features.append(feature)
        
    feat_collection = FeatureCollection(list_features)
    
    geojson_result = json.dumps(feat_collection)
    
    #optionally write to file
    if file_output is not None:
        with open(file_output,"w") as f:
            json.dump(feat_collection,f)
    
    return geojson_result


# In[10]:


def choropleth_map(df_aggreg, border_color = 'black', fill_opacity = 0.5, initial_map = None, with_legend = False,
                   kind = "linear"):
    #colormap
    min_value = df_aggreg["value"].min()
    max_value = df_aggreg["value"].max()
    m = round ((min_value + max_value ) / 2 , 0)
    
    #take resolution from the first row
    res = h3.h3_get_resolution(df_aggreg.hex_id.iloc[0])
#     res=9
    
    if initial_map is None:
        initial_map = Map(location= [29.609942, 52.529768], zoom_start=13, 
                attr= '© <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors © <a href="http://cartodb.com/attributions#basemaps">CartoDB</a>' 
            )
        

    #the colormap 
    #color names accepted https://github.com/python-visualization/branca/blob/master/branca/_cnames.json
    if kind == "linear":
        custom_cm = cm.LinearColormap(['green','yellow','red'], vmin=min_value, vmax=max_value)
    elif kind == "outlier":
        #for outliers, values would be -11,0,1
        custom_cm = cm.LinearColormap(['blue','white','red'], vmin=min_value, vmax=max_value)
    elif kind == "filled_nulls":
        custom_cm = cm.LinearColormap(['sienna','green','yellow','red'], 
                                      index=[0,min_value,m,max_value],vmin=min_value,vmax=max_value)
   

    #create geojson data from dataframe
    geojson_data = hexagons_dataframe_to_geojson(df_hex = df_aggreg)
    
    #plot on map
    name_layer = "Choropleth " + str(res)
    if kind != "linear":
        name_layer = name_layer + kind
        
    GeoJson(
        geojson_data,
        style_function=lambda feature: {
            'fillColor': custom_cm(feature['properties']['value']),
            'color': border_color,
            'weight': 1,
            'fillOpacity': fill_opacity 
        }, 
        name = name_layer
    ).add_to(initial_map)

    #add legend (not recommended if multiple layers)
    if with_legend == True:
        custom_cm.add_to(initial_map)
    
    
    
    return initial_map

    


# In[11]:


def basic_local_outliers(df):
    
    '''For each hexagon, compute its value deviation from the mean of its neighbors on its k-rings for k=2 
    (only neighbors with non-null value). 
    Decision rule: local outlier if its value deviates with more than 2 stddev from the mean of the first ring 
            or its value deviates with more than 2 stddev from the mean of the 1st and 2nd k-rings together'''
        
    #create dictionary where key is hex_id and value is number of stops in that hexagon
    dict_hex_value = dict(zip(df_aggreg["hex_id"],df_aggreg["value"]))
    df["is_isolated"] = 0
    df["is_outlier"] = 0
    df["avg_ring_1"] = None
    df["avg_rings_1_2"] = None
    df["stddev_ring_1"] = None
    df["stddev_rings_1_2"] = None
    
    for i,row in df.iterrows():
        
        is_decided = False
        
        current_hex_value = row["value"]
        list_hex_on_rings_levels = h3.k_ring_distances(h3_address = row["hex_id"], ring_size = 2)
        
        #on ring 0 it's the current hexagon under analysis
        #on ring 1 
        ring_1 = list(list_hex_on_rings_levels[1])
        values_ring_1 = [dict_hex_value[x] for x in ring_1  if x in dict_hex_value.keys()] 
        
        if len(values_ring_1) >= 1:
            # mean requires at least one data point
            avg_ring_1 = statistics.mean(values_ring_1)
            df.loc[i,'avg_ring_1'] = avg_ring_1 
        
            if len(values_ring_1) >= 2:
                #variance requires at least two data points
                stddev_ring_1 = statistics.stdev(values_ring_1)
                df.loc[i,'stddev_ring_1'] = stddev_ring_1 
                
                if current_hex_value > avg_ring_1 + 2* stddev_ring_1:
                    df.loc[i,'is_outlier'] = 1
                    is_decided = True
                elif current_hex_value < avg_ring_1 - 2* stddev_ring_1:
                    df.loc[i,'is_outlier'] = -1
                    is_decided = True
                    
                
            else:
                #only one hexagone with value on ring 1
                #postpone decision to after computing the second ring
                None
        else:
            #no hexagon with value on ring 1, consider the current one as isolated
            df.loc[i,'is_isolated'] = 1
            is_decided = True
                
            
        if is_decided == False:
            #check also the second ring
            ring_2 = list(list_hex_on_rings_levels[2])
            values_ring_2 = [dict_hex_value[x] for x in ring_2  if x in dict_hex_value.keys()] 
            #consider both rings together
            values_ring_2.extend(values_ring_1)
            avg_rings_1_2 = statistics.mean(values_ring_2)
            df.loc[i,'avg_rings_1_2'] = avg_rings_1_2 
            
            if len(values_ring_2) >= 2:
                stddev_rings_1_2 = statistics.stdev(values_ring_2)
                df.loc[i,'stddev_rings_1_2'] = stddev_rings_1_2 

                if current_hex_value > avg_rings_1_2 + 3* stddev_rings_1_2:
                    df.loc[i,'is_outlier'] = 1
                    is_decided = True
                elif current_hex_value < avg_rings_1_2 - 3* stddev_rings_1_2:
                    df.loc[i,'is_outlier'] = -1
                    is_decided = True 
                
                
            else:
                #it has only 1 hexagon with value within the first 2 k-rings, we consider it isolated
                df.loc[i,'is_isolated'] = 1
                is_decided = True
                
        
                
    return df

d = datetime.today() - timedelta(days=1)
e=datetime.today() 
s_day=d.strftime('%d-%b-%Y')
e_day=e.strftime('%d-%b-%Y')
# tehran
#city_id ='A49985304F7542489DC15D26BBED22E5'
########################
#shiraz
city_id='F9CA365EAC7147778517031A42238005'
resolution_Set=9


# In[13]:


#shiraz
city_lat1=29.5721
city_lat2=29.837
city_long1=52.38
city_long2=52.68 


# In[14]:


#tehran
#city_lat1=35.614383
#city_lat2=35.819774
#city_long1=51.172642
#city_long2=51.602743


#if (tab=="پیشنهاد جمع آوری"):
#    resolution_Set = st.selectbox('Zoom level',['<select>', 7, 8, 9,10],3,key=3)
#resolution_Set = st.slider("Choose your resolution: ", min_value=7,max_value=10, value=8, step=1)


sql1="""select b_lock.lock_serial,latitude,longitude from REMOVED.b_lock, NODOOD.rep_monitor_lock where b_lock.lock_status in ('C') and rep_monitor_lock.lock_serial=b_lock.lock_serial and latitude between %s and %s and longitude between %s and %s and 
    rep_monitor_lock.lock_id not in (select lock_id from NODOOD.b_trip where start_time >= '%s' and  start_time < '%s') and b_lock.lock_serial in(select lock_serial from NODOOD.rep_monitor_lock where state in ('O')) """%(city_lat1,city_lat2,city_long1,city_long2,s_day,e_day)
no_trip=pd.read_sql(sql1,db)
lat=no_trip['LATITUDE']
long=no_trip['LONGITUDE']
pelak=no_trip['LOCK_SERIAL']


# In[16]:


sql2="""select * from REMOVED.b_parking where city_id ='%s'"""%(city_id)
parking=pd.read_sql(sql2,db)
#parking.shape
#parking.columns
parking=df_to_hex_df(parking,resolution_Set)


# In[17]:


df_aggreg = counts_by_hexagon(df = no_trip, resolution = resolution_Set)
#print(df_aggreg.shape)
df_aggreg.sort_values(by = "value", ascending = False, inplace = True)
df_aggreg=df_aggreg[df_aggreg['hex_id']!='89433183343ffff']
df_aggreg=df_aggreg[df_aggreg['value']>1]
# df_aggreg
df_aggreg=pd.merge(df_aggreg,parking,on='hex_id', indicator=True, how='outer').query('_merge=="left_only"').drop('_merge', axis=1)


# In[18]:


df_aggreg.drop(columns=['LATITUDE','LONGITUDE','geometry_y'],inplace=True)


# In[19]:


df_aggreg.rename({'geometry_x':'geometry'},axis=1,inplace=True)


# In[20]:


no_trip=df_to_hex_df(no_trip,resolution_Set)


# In[21]:


no_trip=pd.merge(no_trip,parking,on='hex_id', indicator=True, how='outer').query('_merge=="left_only"').drop('_merge', axis=1)
#no_trip.shape


# In[22]:

if(len(df_aggreg)>0):
    m_hex = choropleth_map(df_aggreg = df_aggreg, with_legend = True)
    for index,row in no_trip.iterrows():
        folium.Marker([row['LATITUDE_x'], row['LONGITUDE_x']], popup = row['LOCK_SERIAL'],radius=1).add_to(m_hex)

# m_hex.save('./3_choropleth_counts_by_hexid9.html')
# m_hex


# In[23]:



    if (tab=="پیشنهاد جمع آوری"):
        st.title('<دوچرخه در 24 ساعت گذشته سفر نداشتند>')
        st.markdown(m_hex._repr_html_(), unsafe_allow_html=True)
# i=91


    
