# Import libraries
import pandas as pd
from pandasql import sqldf
from fpdf import FPDF
from datetime import date
import matplotlib.pyplot as plt

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

    df = sw_all_pd

    # set up pdf doc
    pdf=FPDF()
    pdf.add_page()
    pdf.set_font("Times", size=10)
    # line_height = pdf.font_size * 2.5
    # # col_width = pdf.epw / 4
    # col_width = 20
    # for row in data:
    #         for datum in row:
    #             pdf.multi_cell(col_width, line_height, datum, border=1)
    #         pdf.ln(line_height)


    fig, ax =plt.subplots(figsize=(12,4))
    ax.axis('tight')
    ax.axis('off')
    the_table = ax.table(cellText=df.values,colLabels=df.columns,loc='center')
    the_table
    
    pdf.output('test12.pdf')



def get_data_vahydro(viewurl, baseurl = "http://deq1.bse.vt.edu:81/d.dh"):

    url = baseurl + "/" + viewurl
    # print("Retrieving Data From: " + url)
    df=pd.read_csv(url)

    return df


if __name__ == "__main__":
    main()