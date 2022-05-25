# Import libraries
import sys # used for retrieving arguments
import matplotlib.pyplot as plt # used for plotting 
import pandas as pd # used for reading data
import numpy as np #used for quantile analysis
import wget # used for downloading data
import zipfile # used for reading zipped data

def main():

    # Ensure correct usage
    # Salem omid = 249169
    if len(sys.argv) != 3:
        sys.exit("Usage: python boxplots.py runid omid")

    runid = sys.argv[1]
    omid = sys.argv[2]

    runinfo_df = get_runinfo(runid, omid)
    elemname = runinfo_df.elemname
    elemname = [elemname]
    print(elemname[-1])

    df = get_rundata(runid, omid)
    Qout = df.Qout

    quantiles = np.quantile(Qout, [0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0])

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

    data = [data_jan.Qout, data_feb.Qout, data_mar.Qout, data_apr.Qout, data_may.Qout, data_jun.Qout,
    data_jul.Qout, data_aug.Qout, data_sep.Qout, data_oct.Qout, data_nov.Qout, data_dec.Qout]
    
    fig = plt.figure(figsize =(10, 7))
    
    # create plot
    plt.boxplot(data)

    # add title
    plt.title("{}: Qout by Month".format(elemname))

    # add axis labels
    plt.xlabel("Month")
    plt.ylabel("Qout (cfs)")

    # save plot
    plt.savefig("boxplot_Qout_{}.{}.png".format(runid, omid),bbox_inches='tight')

    # show plot
    plt.show()


def get_rundata(runid, omid, baseurl = "http://deq1.bse.vt.edu:81"):

    # download the runlog zip file
    runlog = "{}/data/proj3/out/runlog{}.{}.log.zip".format(baseurl, runid, omid)
    wget.download(runlog)

    # read in the runlog file contained within the zipped folder
    zf = zipfile.ZipFile("runlog{}.{}.log.zip".format(runid, omid))
    df = pd.read_csv(zf.open("runlog{}.{}.log".format(runid, omid)))

    return df

def get_runinfo(runid, omid, baseurl = "http://deq1.bse.vt.edu:81"):

    runinfo_url = "{}/om/remote/get_modelData.php?operation=11&delimiter=,&elementid={}&runid={}&startdate=1984-10-01&enddate=2005-09-30".format(baseurl, omid, runid)
    runinfo = wget.download(runinfo_url)
    runinfo_df = pd.read_csv(runinfo)

    return runinfo_df

if __name__ == "__main__":
    main()