# Import libraries
import pandas as pd
from pandasql import sqldf
from fpdf import FPDF
from datetime import date

def main():

    precip_df = get_data_vahydro(viewurl = 'precipitation-drought-timeseries-export')
    # print(precip_df.head())
    precip_df = sqldf("""SELECT `drought_region` AS region, 
                                `startdate` AS startdate, 
                                `enddate` AS enddate,
                                `[Water_Year_pct_of_Normal]_propvalue` AS 'water yr % of normal',
                                `[Drought_Status]_propcode` AS status
                            FROM precip_df
                            WHERE `[Drought_Status]_propcode` > 0""")
    # print(f'Precipitation Indicators:\n{precip_df}\n')
    precip_pd = pd.DataFrame(precip_df)

    sw_df = get_data_vahydro(viewurl = 'streamflow-drought-timeseries-all-export')
    # print(sw_df.head())

    # reutrn only the 11 official drought evaluation region stream gage indicators
    sw_official_df = sw_df[pd.notna(sw_df)['drought_evaluation_region'] == True]
    # print(sw_official_df)

    # return only those with a below normal drought status:
    # pandas method below:
    # sw_status_df = sw_official_df.query('`[nonex_pct]_propcode` > 0')
    # print(sw_status_df[['drought_evaluation_region', '[nonex_pct]_propcode']])
    
    # sqldf method below:
    # note: 3-quote method allows formatting query across multiple lines
    sw_status_df = sqldf("""SELECT `drought_evaluation_region` AS region, 
                                `[q_7day_cfs]_tstime` AS tstime, 
                                `[q_7day_cfs]_tsendtime` AS tsendtime, 
                                `[nonex_pct]_propvalue` AS 'percentile',
                                `[nonex_pct]_propcode` AS status, 
                                `drought_status_override` AS override,
                                CASE
                                    WHEN `drought_status_override` < `[nonex_pct]_propcode` THEN `drought_status_override`
                                    ELSE `[nonex_pct]_propcode`
                                END AS final_status
                            FROM sw_official_df
                            WHERE `[nonex_pct]_propcode` > 0""")
                            # FROM sw_official_df""") 
    # print(f'Surface Water Indicators:\n{sw_status_df}\n')
    sw_pd = pd.DataFrame(sw_status_df)

    # sw_status_df_all = sqldf("""SELECT `containing_drought_region` AS region, 
    #                             `[q_7day_cfs]_tstime` AS tstime, 
    #                             `[q_7day_cfs]_tsendtime` AS tsendtime,
    #                             `[nonex_pct]_propvalue` AS 'percentile',
    #                             `[nonex_pct]_propcode` AS status, 
    #                             `drought_status_override` AS override,
    #                             CASE
    #                                 WHEN `drought_status_override` < `[nonex_pct]_propcode` THEN `drought_status_override`
    #                                 ELSE `[nonex_pct]_propcode`
    #                             END AS final_status
    #                         FROM sw_df
    #                         WHERE `[nonex_pct]_propcode` > 0""")

    # format table using CTE temporary table
    sw_status_df_all = sqldf("""WITH cte AS(
                                    SELECT  CASE
                                            WHEN `drought_status_override` < `[nonex_pct]_propcode` THEN `drought_status_override`
                                                ELSE `[nonex_pct]_propcode`
                                            END AS final_status,
                                            COUNT(`containing_drought_region`) AS gage_count
                                    FROM sw_df
                                    WHERE `[nonex_pct]_propcode` > 0
                                    GROUP BY final_status 
                                )
    
                                SELECT  CASE
                                            WHEN `final_status` = 1 THEN 'watch'
                                            WHEN `final_status` = 2 THEN 'warning'
                                            WHEN `final_status` = 3 THEN 'emergency'
                                        END AS gage_status,
                                        gage_count
                                FROM cte
                                """)

    # print(f'Surface Water Indicators (All):\n{sw_status_df_all}\n')
    sw_all_pd = pd.DataFrame(sw_status_df_all)


    gw_df = get_data_vahydro(viewurl = 'groundwater-drought-timeseries-all-export')
    # print(gw_df.head())

    # return only those with a below normal drought status
    # retuen the maximum status by region for those regions with multiple gw indicators
    gw_max_status_df = sqldf("""SELECT `drought_evaluation_region` AS region, 
                                    `[gwl_7day_ft]_tstime` AS tstime, 
                                    `[gwl_7day_ft]_tsendtime` AS tsendtime,
                                    `[nonex_pct]_propvalue` AS 'percentile', 
                                    MAX(`[nonex_pct]_propcode`) AS max_status, 
                                    `drought_status_override` AS override,
                                    CASE
                                        WHEN `drought_status_override` < `[nonex_pct]_propcode` THEN `drought_status_override`
                                        ELSE `[nonex_pct]_propcode`
                                    END AS final_status
                                FROM gw_df
                                WHERE `[nonex_pct]_propcode` > 0
                                GROUP BY `drought_evaluation_region`""")
    # print(f'Groundwater Indicators:\n{gw_max_status_df}\n')
    gw_pd = pd.DataFrame(gw_max_status_df)


    res_df = get_data_vahydro(viewurl = 'reservoir-drought-features-export')
    # print(res_df.head())
    res_status_df = sqldf("""SELECT `Drought Region`, `Feature Name`, `Drought Status (propcode)` 
                            FROM res_df 
                          """)
    # print(res_status_df)


    class PDF(FPDF):
        def header(self):
            # self.image('example.jpg', 50, 30, 100)
            self.set_font('Times', 'B', 15)
            self.cell(w=0, h=10, txt=title, border=1, align='C', new_x='LMARGIN', new_y='NEXT')

        def footer(self):
            self.set_y(-15)
            self.set_font('Times', 'I', 8)
            self.cell(w=0, h=10, txt='Page ' + str(self.page_no()) + '/{nb}', align='C', new_x='LMARGIN', new_y='NEXT')




    today = date.today()
    today = today.strftime('%m/%d/%Y')
    print("Today's date:", today)
    title = "Daily Drought Indicator Status: {}".format(today)


    # Start pdf creating
    # pdf = FPDF()
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Times", size=10)
    pdf.ln(4)
    line_height = pdf.font_size * 2.5
    # col_width = pdf.epw / 4  # distribute content evenly

    # section of tables showing indicators that are below normal drought status
    pdf.set_font("Times", style = 'U', size=12)
    pdf.cell(w=0, h=10, txt="Indicators Below Normal:", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Times", size=10)
    pdf.cell(txt="Precipitation Indicators:", new_x="LMARGIN", new_y="NEXT")
    render_table(pdf,precip_pd,line_height)
    pdf.cell(txt="Surface Water Indicators:", new_x="LMARGIN", new_y="NEXT")
    render_table(pdf,sw_pd,line_height)
    pdf.cell(txt="Groundwater Indicators:", new_x="LMARGIN", new_y="NEXT")
    render_table(pdf,gw_pd,line_height)

    pdf.image('https://deq1.bse.vt.edu/drought/state/images/maps/virginia_drought.png', w=100)

    # section of tables showing all dorught monitoring indicators
    pdf.set_font("Times", style = 'U', size=12)
    pdf.cell(w=0, h=10, txt="Indicators All:", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Times", size=10)
    pdf.cell(txt="Surface Water Indicators (All):", new_x="LMARGIN", new_y="NEXT")
    render_table(pdf,sw_all_pd,line_height)


    output_filename = "Daily_Drought_Indicator_Status_{}.pdf".format(date.today().strftime('%m.%d.%Y'))
    pdf.output(output_filename)
    # pdf.output('test16.pdf')



def render_table(pdf,data_pd,line_height):
    
    # format pandas dataframe as list (required for rendering the table in pdf)
    data_str= data_pd.applymap(str)  # Convert all data inside dataframe into string type
    data_str_columns = [list(data_str)]  # Get list of dataframe columns
    data_str_rows = data_str.values.tolist()  # Get list of dataframe rows
    data_all_data = data_str_columns + data_str_rows  # Combine columns and rows in one list

    # render the table
    for row in data_all_data:
        for datum in row:
            pdf.multi_cell(
                20,
                line_height,
                datum,
                border=1,
                new_y="TOP",
                max_line_height=pdf.font_size,
            )
        pdf.ln(line_height)
    pdf.ln(4)


def get_data_vahydro(viewurl, baseurl = "http://deq1.bse.vt.edu:81/d.dh"):

    url = baseurl + "/" + viewurl
    # print("Retrieving Data From: " + url)
    df=pd.read_csv(url)

    return df


if __name__ == "__main__":
    main()