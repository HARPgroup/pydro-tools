# Import libraries
import pandas as pd
from pandasql import sqldf
from fpdf import FPDF
from datetime import date

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
    sw_status_df = sqldf("""SELECT `drought_evaluation_region`, 
                                `[q_7day_cfs]_tstime` AS tstime, 
                                `[q_7day_cfs]_tsendtime` AS tsendtime, 
                                `[nonex_pct]_propcode`, 
                                `drought_status_override`,
                                CASE
                                    WHEN `drought_status_override` < `[nonex_pct]_propcode` THEN `drought_status_override`
                                    ELSE `[nonex_pct]_propcode`
                                END AS final_status
                            FROM sw_official_df
                            WHERE `[nonex_pct]_propcode` > 0""")
                            # FROM sw_official_df""") 
    print(f'Surface Water Indicators:\n{sw_status_df}\n')

    sw_status_df_all = sqldf("""SELECT `containing_drought_region` AS reg, 
                                `[q_7day_cfs]_tstime` AS tstime, 
                                `[q_7day_cfs]_tsendtime` AS tsendtime, 
                                `[nonex_pct]_propcode` AS C, 
                                `drought_status_override` AS O,
                                CASE
                                    WHEN `drought_status_override` < `[nonex_pct]_propcode` THEN `drought_status_override`
                                    ELSE `[nonex_pct]_propcode`
                                END AS final_status
                            FROM sw_df
                            WHERE `[nonex_pct]_propcode` > 0""")
    print(f'Surface Water Indicators (All):\n{sw_status_df_all}\n')
    sw_all_pd = pd.DataFrame(sw_status_df_all)


    gw_df = get_data_vahydro(viewurl = 'groundwater-drought-timeseries-all-export')
    # print(gw_df.head())

    # return only those with a below normal drought status
    # retuen the maximum status by region for those regions with multiple gw indicators
    gw_max_status_df = sqldf("""SELECT `drought_evaluation_region`, 
                                    `[gwl_7day_ft]_tstime` AS tstime, 
                                    `[gwl_7day_ft]_tsendtime` AS tsendtime, 
                                    MAX(`[nonex_pct]_propcode`) AS max_status, 
                                    `drought_status_override`,
                                    CASE
                                        WHEN `drought_status_override` < `[nonex_pct]_propcode` THEN `drought_status_override`
                                        ELSE `[nonex_pct]_propcode`
                                    END AS final_status
                                FROM gw_df
                                WHERE `[nonex_pct]_propcode` > 0
                                GROUP BY `drought_evaluation_region`""")
    print(f'Groundwater Indicators:\n{gw_max_status_df}\n')


    res_df = get_data_vahydro(viewurl = 'reservoir-drought-features-export')
    # print(res_df.head())
    res_status_df = sqldf("""SELECT `Drought Region`, `Feature Name`, `Drought Status (propcode)` 
                            FROM res_df 
                          """)
    # print(res_status_df)


    today = date.today()
    today = today.strftime('%m/%d/%Y')
    print("Today's date:", today)

    # set up pdf doc
    pdf=FPDF()
    pdf.add_page()
    pdf.set_font('arial', 'B', 8)
    pdf.cell(60)
    pdf.cell(75, 10,'Iris Dataset Measurements by Class', 0, 2, 'C')
    pdf.cell(90, 10, '', 0, 2, 'C')
    pdf.cell(-55)
    columnNameList = list(sw_all_pd.columns)
    for header in columnNameList[:-1]:
        pdf.cell(35, 10, header, 1, 0, 'C')
    pdf.cell(35, 10, columnNameList[-1], 1, 2, 'C')
    pdf.cell(-140)
    pdf.set_font('arial', '', 8)
    for row in range(0, len(sw_all_pd)):
        for col_num, col_name in enumerate(columnNameList):
            if col_num != len(columnNameList) - 1:
                # pdf.cell(35, 10, str(sw_all_pd['%s' % (col_name)].iloc[row]), 1, 0, 'C')
                pdf.cell(35, 10, str(sw_all_pd['%s' % (col_name)].iloc[row]), 1, 0, 'C')
            else:
                pdf.cell(35, 10, str(sw_all_pd['%s' % (col_name)].iloc[row]), 1, 2, 'C')
                pdf.cell(-140)
    # pdf.cell(35, 10, "", 0, 2)
    # pdf.cell(20)
    # pdf.image('iris_grouped_df.png', x = None, y = None, w = 0, h = 0, type = '', link = '')
    pdf.output('test12.pdf', 'F')



def get_data_vahydro(viewurl, baseurl = "http://deq1.bse.vt.edu:81/d.dh"):

    url = baseurl + "/" + viewurl
    # print("Retrieving Data From: " + url)
    df=pd.read_csv(url)

    return df


if __name__ == "__main__":
    main()