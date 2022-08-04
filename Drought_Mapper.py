# Import libraries
import pandas as pd
from pandasql import sqldf
import geopandas as gpd
import folium
# from shapely import wkt
# import matplotlib.pyplot as plt

def main():

    map = mapgen()
    map.save("drought_map_v2.html")



def mapgen():
    # import data layer as dataframe
    states_df = pd.read_csv('https://raw.githubusercontent.com/HARPgroup/HARParchive/master/GIS_layers/STATES.tsv', sep='\t')
    # print(states_df.head())

    # select only the virginia polygon
    va_df = sqldf("""SELECT * FROM states_df WHERE `state` == 'VA'""")
    # print(va_df.head())

    # convert to GeoDataFrame
    va_df['geom'] = gpd.GeoSeries.from_wkt(va_df['geom'])
    va_gdf = gpd.GeoDataFrame(va_df, geometry='geom')

    # generate simple plot of layer
    # va_gdf.plot(figsize=(6, 6))
    # plt.show()

    # generate a leaflet map via folium
    # m = folium.Map(location=[37.412664, -78.680033], zoom_start=7)
    m = folium.Map(location=[37.412664, -78.680033], tiles="cartodbpositron", zoom_start=7)

    for _, r in va_gdf.iterrows():
        # Without simplifying the representation of each polygon,the map might not be displayed
        sim_geo = gpd.GeoSeries(r['geom']).simplify(tolerance=0.001)
        geo_j = sim_geo.to_json()
        geo_j = folium.GeoJson(data=geo_j,style_function=lambda x: {'fillColor': 'gray', 'color': 'black'})
        folium.Popup(r['state']).add_to(geo_j)
        geo_j.add_to(m)
    # m
    return m



if __name__ == "__main__":
    main()