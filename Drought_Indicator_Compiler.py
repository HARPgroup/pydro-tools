# Import libraries
import pandas as pd


def main():

    sw_df = get_data_vahydro(viewurl = 'streamflow-drought-timeseries-all-export')
    # print(sw_df.head())

    # reutrn only the 11 official drought evaluation region stream gage indicators
    sw_official_df = sw_df[pd.notna(sw_df)['official_drought_region'] == True]

    # return only those with a below normal drought status
    sw_status_df = sw_official_df.query('`[nonex_pct]_propcode` > 0')
    print(sw_status_df[['official_drought_region', '[nonex_pct]_propcode']])


    gw_df = get_data_vahydro(viewurl = 'groundwater-drought-timeseries-all-export')
    # print(gw_df.head())

    # return only those with a below normal drought status
    sw_status_df = gw_df.query('`[nonex_pct]_propcode` > 0')
    print(sw_status_df[['Drought_Evaluation_Region', '[nonex_pct]_propcode']])
    # print(sw_status_df.loc[sw_status_df['[nonex_pct]_propcode'].idxmax()])


    res_df = get_data_vahydro(viewurl = 'reservoir-drought-features-export')
    # print(res_df.head())


def get_data_vahydro(viewurl, baseurl = "http://deq1.bse.vt.edu:81/d.dh"):

    url = baseurl + "/" + viewurl
    print("Retrieving Data From: " + url)
    df=pd.read_csv(url)

    return df


if __name__ == "__main__":
    main()