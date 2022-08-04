# Import libraries
import pandas as pd
from pandasql import sqldf
import geopandas as gpd
import folium
from shapely import wkt

def main():

    sw_df = get_data_vahydro(viewurl = 'streamflow-drought-timeseries-all-export')
    # print(sw_df.head())

    # reutrn only the 11 official drought evaluation region stream gage indicators
    sw_official_df = sw_df[pd.notna(sw_df)['drought_evaluation_region'] == True]

    # return only those with a below normal drought status:
    # pandas method below:
    # sw_status_df = sw_official_df.query('`[nonex_pct]_propcode` > 0')
    # print(sw_status_df[['drought_evaluation_region', '[nonex_pct]_propcode']])
    
    # sqldf method below:
    # note: 3-quote method allows formatting query across multiple lines
    sw_status_df = sqldf("""SELECT `drought_evaluation_region`, `[nonex_pct]_propcode`, `drought_status_override`,
                                CASE
                                    WHEN `drought_status_override` < `[nonex_pct]_propcode` THEN `drought_status_override`
                                    ELSE `[nonex_pct]_propcode`
                                END AS final_status
                            FROM sw_official_df""")
                            # WHERE `[nonex_pct]_propcode` > 0""")
    print(sw_status_df)
    print(' ') 

    gw_df = get_data_vahydro(viewurl = 'groundwater-drought-timeseries-all-export')
    # print(gw_df.head())

    # return only those with a below normal drought status
    gw_status_df = gw_df.query('`[nonex_pct]_propcode` > 0')
    # print(gw_status_df[['drought_evaluation_region', '[nonex_pct]_propcode']])
    gw_status_df = gw_status_df[['drought_evaluation_region', '[nonex_pct]_propcode', 'drought_status_override']]
    # print(gw_status_df)

    # gw_max_status_df = gw_status_df.groupby(['drought_evaluation_region']).max()
    # print(gw_max_status_df)

    gw_max_status_df = sqldf("""SELECT `drought_evaluation_region`, MAX(`[nonex_pct]_propcode`) AS max_status, `drought_status_override`,
                                    CASE
                                        WHEN `drought_status_override` < `[nonex_pct]_propcode` THEN `drought_status_override`
                                        ELSE `[nonex_pct]_propcode`
                                    END AS final_status
                                FROM gw_status_df
                                WHERE `[nonex_pct]_propcode` > 0
                                GROUP BY `drought_evaluation_region`""")
    print(gw_max_status_df)


    res_df = get_data_vahydro(viewurl = 'reservoir-drought-features-export')
    # print(res_df.head())
    res_status_df = sqldf("""SELECT `Drought Region`, `Feature Name`, `Drought Status (propcode)` 
                            FROM res_df 
                          """)
    # print(res_status_df)


    map = mapgen(test = 'test')


def get_data_vahydro(viewurl, baseurl = "http://deq1.bse.vt.edu:81/d.dh"):

    url = baseurl + "/" + viewurl
    # print("Retrieving Data From: " + url)
    df=pd.read_csv(url)

    return df



def mapgen(test):
    print(test)

    states_df = pd.read_csv('https://raw.githubusercontent.com/HARPgroup/HARParchive/master/GIS_layers/STATES.tsv', sep='\t')
    states_df['geom'] = gpd.GeoSeries.from_wkt(states_df['geom'])
    states_gdf = gpd.GeoDataFrame(states_df, geometry='geom')


    # states_df.rename(columns = {"geom":"geometry"}, inplace = True)
    print(states_df.head())
    print(states_gdf.head())

    states_gdf.plot()

    # states_df.plot()

    # m = folium.Map(location=[37.412664, -78.680033], zoom_start=8)
    # m = folium.Map(location=[37.412664, -78.680033], tiles="cartodbpositron", zoom_start=8)
    # m.save("drought_map.html")

    # states_df.plot(figsize=(6, 6))
    

    # path = gpd.datasets.get_path('nybb')
    # df = gpd.read_file(states_df)
    # print(df.head())

    # return states_df
    return states_df



if __name__ == "__main__":
    main()