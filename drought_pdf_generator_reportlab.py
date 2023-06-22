# Import libraries
import pandas as pd
from pandasql import sqldf
# from fpdf import FPDF
from reportlab.pdfgen import canvas
# from datetime import date

# def get_data_vahydro(viewurl, baseurl = "http://deq1.bse.vt.edu:81/d.dh"):
def get_data_vahydro(viewurl, baseurl = "https://deq1.bse.vt.edu/d.dh"):
    url = baseurl + "/" + viewurl
    # print("Retrieving Data From: " + url)
    df=pd.read_csv(url)
    return df

# def render_table(pdf,data_pd,line_height):
#     # format pandas dataframe as list (required for rendering the table in pdf)
#     data_str= data_pd.applymap(str)  # Convert all data inside dataframe into string type
#     data_str_columns = [list(data_str)]  # Get list of dataframe columns
#     data_str_rows = data_str.values.tolist()  # Get list of dataframe rows
#     data_all_data = data_str_columns + data_str_rows  # Combine columns and rows in one list
#     # render the table
#     for row in data_all_data:
#         for datum in row:
#             pdf.multi_cell(
#                 20,
#                 line_height,
#                 datum,
#                 border=1,
#                 new_y="TOP",
#                 max_line_height=pdf.font_size,
#             )
#         pdf.ln(line_height)
#     pdf.ln(4)

# def process_data(pdf,data_pd,line_height):
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
print(sw_df.head())

# reutrn only the 11 official drought evaluation region stream gage indicators
sw_official_df = sw_df[pd.notna(sw_df)['drought_evaluation_region'] == True]
# print(sw_official_df)

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

###############################################################
# THIS WORKS:
# from reportlab.lib.units import inch
# from reportlab.lib.pagesizes import letter
# from reportlab.platypus import SimpleDocTemplate
# from reportlab.platypus.tables import Table,TableStyle,colors
# my_path='C:\\Users\\jklei\\Desktop\\Learning Python\\pydro-tools\\reportlab_test.pdf' 
# my_doc = SimpleDocTemplate(my_path,pagesize=letter)


# c_width=[1*inch] # width of the columns 

# sw_data=sw_pd.values.tolist() # create a list using Dataframe
# sw_t=Table(sw_data,colWidths=c_width,repeatRows=1)
# sw_t.setStyle(TableStyle([('FONTSIZE',(0,0),(-1,-1),12),('BACKGROUND',(0,0),(-1,0),colors.lightgreen),('VALIGN',(0,0),(-1,0),'TOP')]))

# gw_data=gw_pd.values.tolist() # create a list using Dataframe
# gw_t=Table(gw_data,colWidths=c_width,repeatRows=1)
# gw_t.setStyle(TableStyle([('FONTSIZE',(0,0),(-1,-1),12),('BACKGROUND',(0,0),(-1,0),colors.lightgreen),('VALIGN',(0,0),(-1,0),'TOP')]))


# elements=[]
# elements.append(sw_t)
# elements.append(gw_t)

# my_doc.build(elements)
###############################################################


###############################################################
###############################################################
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.platypus.tables import Table,TableStyle,colors
my_path='C:\\Users\\jklei\\Desktop\\Learning Python\\pydro-tools\\reportlab_test2.pdf' 
my_doc = SimpleDocTemplate(my_path,pagesize=letter)


c_width=[2.0*inch,1*inch,1*inch,1*inch,0.7*inch,0.7*inch,0.7*inch] # width of the columns 

sw_data=sw_pd.values.tolist() # create a list using Dataframe
colnames = [['region', 'tstime', 'tsendtime', 'percentile', 'status', 'override', 'final_status']]
sw_data = colnames + sw_data
sw_t=Table(sw_data,colWidths=c_width,repeatRows=1)
sw_t.setStyle(TableStyle([('FONTSIZE',(0,0),(-1,-1),12),('BACKGROUND',(0,0),(-1,0),colors.lightgreen),('VALIGN',(0,0),(-1,0),'TOP')]))

gw_data=gw_pd.values.tolist() # create a list using Dataframe
gw_data = colnames + gw_data
gw_t=Table(gw_data,colWidths=c_width,repeatRows=1)
gw_t.setStyle(TableStyle([('FONTSIZE',(0,0),(-1,-1),12),('BACKGROUND',(0,0),(-1,0),colors.lightgreen),('VALIGN',(0,0),(-1,0),'TOP')]))


elements=[]
# print(type(elements))
# print(type(sw_t))


elements.append(Spacer(1,0.2*inch))
sw_text = Paragraph("Surface Water:")
elements.append(sw_text)
elements.append(sw_t)

elements.append(Spacer(1,0.2*inch))
gw_text = Paragraph("Groundwater:")
elements.append(gw_text)
elements.append(gw_t)

my_doc.build(elements)
###############################################################