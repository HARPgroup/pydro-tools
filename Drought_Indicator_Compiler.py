# Import libraries
import pandas as pd


def main():

    sw_df = get_data_vahydro(viewurl = 'streamflow-drought-timeseries-all-export')
    print(sw_df.head())

    res_df = get_data_vahydro(viewurl = 'reservoir-drought-features-export')
    print(res_df.head())


def get_data_vahydro(viewurl, baseurl = "http://deq1.bse.vt.edu:81/d.dh"):

    url = baseurl + "/" + viewurl
    print("Retrieving Data From: " + url)
    df=pd.read_csv(url)

    return df


if __name__ == "__main__":
    main()