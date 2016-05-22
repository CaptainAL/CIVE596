# -*- coding: utf-8 -*-
"""
Created on Thu Oct 29 12:06:08 2015

@author: Alex
"""
import pandas as pd

maindir = 'C:/Users/Alex/Documents/GitHub/CIVE596/'
datadir = maindir+'Data/'

## Open Data
XL = pd.ExcelFile(datadir+'River_Watch_Water_Chemistry_2004_2014.xlsx')
data = XL.parse('River_Watch_Water_Chemistry', index_col = 'Sample Date', parse_dates=True)
## Select Sites for analysis
data = data[data['FeatureID'].isin(['RW-009','RW-010','RW-011W','RW-013','RW-014','RW-015','RW-013','RW-012','RW-016'])]
## Add our Site #'s
Site_dict = {'RW-009':'8','RW-010':'9','RW-011W':'10','RW-013':'11','RW-014':'12','RW-015':'13','RW-013':'11','RW-012':'14','RW-016':'15'}
data['Site #'] = data['FeatureID'].apply(lambda x: Site_dict[x])


## Add Lat/Lon from Locations List
## Open Locations List
Loc_XL = pd.ExcelFile(datadir+'RiverWatchSites_LocationList.xlsx')
locations = Loc_XL.parse('RiverWatchSites_PointCollection',index_col = 'FeatureID', parse_dates=False)
location_df = locations[['Latitude','Longitude']]
location_df['FeatureID'] = location_df.index
location_df = location_df [location_df ['FeatureID'].isin(['RW-009','RW-010','RW-011W','RW-013','RW-014','RW-015','RW-013','RW-012','RW-016'])]
location_df['Site #'] = location_df['FeatureID'].apply(lambda x: Site_dict[x])
data['Latitude'] = data['FeatureID'].apply(lambda x: location_df.loc[x]['Latitude'])
data['Longitude'] = data['FeatureID'].apply(lambda x: location_df.loc[x]['Longitude'])

## some date columns
data['Sample Date'] = data.index
data['Year'] = data['Sample Date'].apply(lambda x: "{:%Y}".format(x))
data['Month'] = data['Sample Date'].apply(lambda x: "{:%m}".format(x))
## Add a field for season
Season_dict = {'09':'Fall','10':'Fall','11':'Fall','12':'Winter','01':'Winter','02':'Winter','03':'Spring','04':'Spring','05':'Spring','06':'Summer','07':'Summer','08':'Summer'}
data['Season'] = data['Month'].apply(lambda x: Season_dict[x])



Site_nums = range(8,16,1)
Analytes = ['Dissolved Oxygen','Percent Dissolved Oxygen','pH','Specific Conductivity','Temperature','Phosphate','NO3 as N']
Years = range(2004,2015,1)
Seasons = ['Fall','Winter','Spring','Summer']

annual_avg_std = pd.DataFrame()
for analyte in Analytes:
    for site_num in Site_nums:
        for year in Years:
            site_data =  data[(data['Analyte']==str(analyte)) & (data['Site #']==str(site_num)) & (data['Year']==str(year))]
            annual_avg_std = annual_avg_std.append(pd.DataFrame({'Analyte':analyte,'Year':year,'Avg':site_data['Result'].mean(),'STD':site_data['Result'].std(),
            'Lat':site_data['Latitude'].max(),'Lon':site_data['Longitude'].max()}, index = [site_num]))
            
long_term_avg = pd.DataFrame()
for analyte in Analytes:
    for site_num in Site_nums:
        site_data =  data[(data['Analyte']==str(analyte)) & (data['Site #']==str(site_num)) & (data['Year']==str(year))]
        long_term_avg= long_term_avg.append(pd.DataFrame({'Analyte':analyte,'Avg':site_data['Result'].mean(),
            'Lat':site_data['Latitude'].max(),'Lon':site_data['Longitude'].max()},index = [site_num]))
        
        
seasonal_avg = pd.DataFrame()
for analyte in Analytes:
    for site_num in Site_nums:
        for season in Seasons:
            site_data =  data[(data['Analyte']==str(analyte)) & (data['Site #']==str(site_num)) & (data['Season']==str(season))]
            seasonal_avg = seasonal_avg.append(pd.DataFrame({'Analyte':analyte,'Season':season,'Avg':site_data['Result'].mean(),
            'Lat':site_data['Latitude'].max(),'Lon':site_data['Longitude'].max()},index = [site_num]))

Analytes = ['Dissolved Oxygen','Percent Dissolved Oxygen','pH']


for analyte in Analytes:    
    df_seasonal = seasonal_avg[seasonal_avg['Analyte']==analyte]       
    fig, [(spring,summer), (fall,winter)] = plt.subplots(2,2,sharey=True)
    df_spring = df_seasonal[df_seasonal['Season']=='Spring']
    df_summer = df_seasonal[df_seasonal['Season']=='Summer']
    df_fall = df_seasonal[df_seasonal['Season']=='Fall']
    df_winter = df_seasonal[df_seasonal['Season']=='Winter']
    
    
    spring.bar(df_spring.index.values,df_spring['Avg'].values)
    summer.bar(df_summer.index.values,df_summer['Avg'].values)
    fall.bar(df_fall.index.values,df_fall['Avg'].values)
    winter.bar(df_winter.index.values,df_winter['Avg'].values)
    
    spring.set_title('Spring')
    summer.set_title('Summer')
    fall.set_title('Fall')
    winter.set_title('Winter')
    
    plt.suptitle(analyte)
    fall.set_xlabel('Site #'), winter.set_xlabel('Site #')
    plt.savefig(maindir+'Figures/'+analyte+'_seasonal average.png')   
    plt.show()     
            

from mpl_toolkits.basemap import Basemap


def scaleSeries(series,new_scale=[100,10]):
    new_scale = new_scale
    OldRange = (series.max() - series.min())  
    NewRange = (new_scale[0] - new_scale[1])  
    NewSeriesValues = (((series - series.min()) * NewRange) / OldRange) + new_scale[1]
    return NewSeriesValues   
    
## Map coordinates  
ur = [32.87, -116.96] 
ll = [32.81, -117.08 ]


for analyte in Analytes:
    df = long_term_avg[long_term_avg['Analyte']==analyte]
    

    fig, ax = plt.subplots(1)
    plt.suptitle(analyte)
    m = Basemap(projection='merc', resolution='c',
                llcrnrlon=ll[1], llcrnrlat=ll[0],
                urcrnrlon=ur[1], urcrnrlat=ur[0], ax=ax)
    m.readshapefile(datadir+'sd_river','sd_river',color='b')           
    sc = m.scatter(df['Lon'].values,df['Lat'].values,latlon=True, s= scaleSeries(df['Avg'].values), c=df['Avg'].values,cmap=plt.get_cmap('rainbow'),edgecolor='None')
    
    for d in df.iterrows():   
        name = d[0]
        name
        d = d[1]
        x_i, y_i = m(float(d['Lon']), float(d['Lat']))
        plt.text(x_i, y_i, name)

    m.etopo()

    m.drawparallels(np.arange(ll[0],ur[0],.02),labels=[1,0,0,0])
    m.drawmeridians(np.arange(ll[1],ur[1],.02),labels=[0,0,1,0],rotation=60)
    
    from mpl_toolkits.axes_grid1 import make_axes_locatable
    divider = make_axes_locatable(m.ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    cbar=plt.colorbar(sc,cax=cax)
    
    plt.savefig(maindir+'Figures/'+analyte+' Long term avg.png')
    plt.show()
    plt.close('all')



for analyte in ['Specific Conductivity','Temperature','Phosphate','NO3 as N']:
    df = annual_avg_std[annual_avg_std['Analyte']==analyte]
    df = df.dropna()
    

    fig, ax = plt.subplots(1)
    plt.suptitle(analyte)
    m = Basemap(projection='merc', resolution='c',
                llcrnrlon=ll[1], llcrnrlat=ll[0],
                urcrnrlon=ur[1], urcrnrlat=ur[0], ax=ax)
    m.readshapefile(datadir+'sd_river','sd_river',color='b')           
    sc = m.scatter(df['Lon'].values,df['Lat'].values,latlon=True, s= scaleSeries(df['Avg'].values), c=df['Avg'].values,cmap=plt.get_cmap('rainbow'),edgecolor='None')
    
    for d in df.iterrows():   
        name = d[0]
        name
        d = d[1]
        x_i, y_i = m(float(d['Lon']), float(d['Lat']))
        plt.text(x_i, y_i, name)

    m.etopo()

    m.drawparallels(np.arange(ll[0],ur[0],.02),labels=[1,0,0,0])
    m.drawmeridians(np.arange(ll[1],ur[1],.02),labels=[0,0,1,0],rotation=60)
    
    from mpl_toolkits.axes_grid1 import make_axes_locatable
    divider = make_axes_locatable(m.ax)
    cax = divider.append_axes("right", size="5%", pad=0.05)
    cbar=plt.colorbar(sc,cax=cax)
    
    plt.savefig(maindir+'Figures/'+analyte+' available data.png')
    plt.show()
    plt.close('all')          
         
            
            
            
            