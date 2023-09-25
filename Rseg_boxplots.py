# Import libraries
import sys # used for retrieving arguments
import matplotlib.pyplot as plt # used for plotting 
import pandas as pd # used for retrieving and working with run data
import numpy as np #used for quantile analysis
import wget # used for downloading data
import zipfile # used for reading zipped data

def main():

    # Ensure correct usage
    # Salem omid = 249169
    if len(sys.argv) != 4:
        sys.exit("Usage: python boxplots.py runid omid")

    runid = sys.argv[1]
    omid = sys.argv[2]
    metric = sys.argv[3]

    runinfo_df = get_runinfo(runid, omid)
    elemname = runinfo_df["elemname"]
    elemname = pd.Series.to_string(elemname) 
    elemname = elemname.replace("0    ", "")

    df = get_rundata(runid, omid)
    # Qout = df[metric]
    print(df.columns.tolist())
    # quantiles = np.quantile(Qout, [0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0])
    # metric = 'Qout'

    data_jan = df[df['month'] == 1]
    data_feb = df[df['month'] == 2]
    data_mar = df[df['month'] == 3]
    data_apr = df[df['month'] == 4]
    data_may = df[df['month'] == 5]
    data_jun = df[df['month'] == 6]
    data_jul = df[df['month'] == 7]
    data_aug = df[df['month'] == 8]
    data_sep = df[df['month'] == 9]
    data_oct = df[df['month'] == 10]
    data_nov = df[df['month'] == 11]
    data_dec = df[df['month'] == 12]

    data = [data_jan[metric], data_feb[metric], data_mar[metric], data_apr[metric], data_may[metric], data_jun[metric],
    data_jul[metric], data_aug[metric], data_sep[metric], data_oct[metric], data_nov[metric], data_dec[metric]]
    
    # fig = plt.figure(figsize =(10, 7))
    fig, ax = plt.subplots(constrained_layout=True)

    # create plot
    plt.boxplot(data)

    # add title
    plt.title("{}: {} by Month, Run {}".format(elemname,metric,runid))

    # add axis labels
    plt.xlabel("Month")
    # plt.ylabel("Qout (cfs)", color = 'b', loc='bottom')

    # set axis limits
    # print(max(data))
    plt.ylim([0, 1500])

    # secondary axis in mgd
    temperature = np.random.randn(len(data))
    def mgd_to_anomaly(x):
        return (x * 0.64631688969744)

    def anomaly_to_mgd(x):
        return (x + 1000)

    # use of a float for the position:
    # secax_y2 = ax.secondary_yaxis(1.2, functions=(mgd_to_anomaly, anomaly_to_mgd))
    # secax_y2 = ax.secondary_yaxis('right', functions=(mgd_to_anomaly, anomaly_to_mgd))
    secax_y2 = ax.secondary_yaxis(-0.1, functions=(mgd_to_anomaly, anomaly_to_mgd))
    secax_y2.set_ylabel(metric, color = 'black', loc='center')

    plt.text(-0.05, -0.06, "cfs", fontsize=10, transform = ax.transAxes)
    plt.text(-0.16, -0.06, "mgd", fontsize=10, transform = ax.transAxes)

    # save plot
    plt.savefig("boxplot_{}_{}.{}.png".format(metric, runid, omid),bbox_inches='tight')

    # show plot
    plt.show()


def get_rundata(runid, omid, baseurl = "http://deq1.bse.vt.edu:81"):

    # download the runlog zip file
    runlog = "{}/data/proj3/out/runlog{}.{}.log.zip".format(baseurl, runid, omid)
    wget.download(runlog)

    # read in the runlog file contained within the zipped folder
    zf = zipfile.ZipFile("runlog{}.{}.log.zip".format(runid, omid))
    df = pd.read_csv(zf.open("runlog{}.{}.log".format(runid, omid)))

    # remove model warm-up period
    syear = min(df['year'])
    eyear = max(df['year'])
    sdate = "{}-10-01".format(syear)
    edate = "{}-09-30".format(eyear)
    print("\nStart Date: ",sdate)
    print("\nEnd Date:   ",edate)
    mask = (df['thisdate'] > sdate) & (df['thisdate'] <= edate)
    df = df.loc[mask]

    # print col names
    # for col in df.columns:
    #     print(col)
    # print(df['thisdate'])

    return df

def get_runinfo(runid, omid, baseurl = "http://deq1.bse.vt.edu:81"):

    runinfo_url = "{}/om/remote/get_modelData.php?operation=11&delimiter=,&elementid={}&runid={}&startdate=1984-10-01&enddate=2005-09-30".format(baseurl, omid, runid)
    runinfo = wget.download(runinfo_url)
    runinfo_df = pd.read_csv(runinfo)

    return runinfo_df

if __name__ == "__main__":
    main()