#!/usr/local/bin/python3.9
'''
to run type: 'streamlit run dashboard.py' in terminal

sources: 
git@github.com:Sven-Bo/streamlit-sales-dashboard.git
git@github.com:AbhisheakSaraswat/PythonStreamlit.git
'''

#import packages
import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
warnings.filterwarnings('ignore')

#define paths and infile
top = os.getcwd()
data_dir = os.path.join(top, 'data')
infile = os.path.join(data_dir, 'supermarket_sales1.xlsx')

#set page configuration
st.set_page_config(page_title="Superstore Data Visualization", 
                   page_icon=":bar_chart:",
                   layout="wide")

#read data
@st.cache_data
def get_data_from_excel():
    df = pd.read_excel(
        io=infile,
        engine="openpyxl",
        sheet_name="Sales",
        #nrows=1000,
    )
    # Add 'hour' column to dataframe
    df["hour"] = pd.to_datetime(df["Time"], format="%H:%M:%S").dt.hour
    #Create new product_type column
    df["product_type"] = df["Product line"]
    return df

df = get_data_from_excel()

#comment to turn off dataframe return
#st.dataframe(df)

# ---- SIDEBAR ----
st.sidebar.header("Please Filter Here:")
city = st.sidebar.multiselect(
    "Select the City:",
    options=df["City"].unique(),
    default=df["City"].unique()
)

customer_type = st.sidebar.multiselect(
    "Select the Customer Type:",
    options=df["Customer_type"].unique(),
    default=df["Customer_type"].unique(),
)

gender = st.sidebar.multiselect(
    "Select the Gender:",
    options=df["Gender"].unique(),
    default=df["Gender"].unique()
)

product = st.sidebar.multiselect(
    "Select the Product:",
    options=df["product_type"].unique(),
    default=df["product_type"].unique()
)

df_selection = df.query(
    "(City == @city) and (Customer_type ==@customer_type) and (Gender == @gender) and (product_type ==  @product)"
)

#comment to turn off dataframe return with selection
#st.dataframe(df_selection)

# Check if the dataframe is empty:
if df_selection.empty:
    st.warning("No data available based on the current filter settings!")
    st.stop() # This will halt the app from further execution.

# ---- MAIN PAGE ----
st.title(":bar_chart: Sales Dashboard")
st.markdown("##")

#define key performance indicators
total_sales = int(df_selection["Total"].sum())
average_rating = round(df_selection["Rating"].mean(), 1)
star_rating = ":star:" * int(round(average_rating, 0))
average_sale_by_transaction = round(df_selection["Total"].mean(), 2)
average_gmp = round(df_selection["gross margin percentage"].mean(),1)

#create dashboard with KPIs
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.subheader("Total Sales:")
    st.subheader(f"US $ {total_sales:,}")
with col2:
    st.subheader("Average Rating:")
    st.subheader(f"{average_rating} {star_rating}")
with col3:
    st.subheader("Average Sales Per Transaction:")
    st.subheader(f"US $ {average_sale_by_transaction}")
with col4:
    st.subheader("Average Gross Margin %:")
    st.subheader(f"US $ {average_gmp}")

st.markdown("""---""")

#grouped bar chart - sales by product line
sales_by_product_line = df_selection.groupby(by=["product_type"])[["Total"]].sum().sort_values(by="Total")
fig_product_sales = px.bar(
    sales_by_product_line,
    x="Total",
    y=sales_by_product_line.index,
    orientation="h",
    title="<b>Sales by Product Line</b>",
    color_discrete_sequence=["#0083B8"] * len(sales_by_product_line),
    template="plotly_white",
)
fig_product_sales.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False))
)

#grouped bar chart - sales by hour
sales_by_hour = df_selection.groupby(by=["hour"])[["Total"]].sum()
fig_hourly_sales = px.bar(
    sales_by_hour,
    x=sales_by_hour.index,
    y="Total",
    title="<b>Sales by hour</b>",
    color_discrete_sequence=["#0083B8"] * len(sales_by_hour),
    template="plotly_white",
)
fig_hourly_sales.update_layout(
    xaxis=dict(tickmode="linear"),
    plot_bgcolor="rgba(0,0,0,0)",
    yaxis=(dict(showgrid=False)),
)

income_price = df_selection.groupby(by=["Unit price"])[["gross income"]].mean()
fig_price_income = px.scatter(
    income_price, 
    x = income_price.index, 
    y = "gross income", 
    #size = "gross income",
    color = "gross income",
    trendline="ols",
    marginal_y="violin",
    marginal_x="box",
    title="<b>Average Gross Income by Unit Price</b>",
)
fig_price_income.update_layout(
    xaxis=dict(tickmode="linear"),
    plot_bgcolor="rgba(0,0,0,0)",
    yaxis=(dict(showgrid=False)),
)


#customization
# create grid for display
def make_grid(cols,rows):
    grid = [0]*cols
    for i in range(cols):
        with st.container():
            grid[i] = st.columns(rows)
    return grid
mygrid = make_grid(2,2)

#plot using grid customization
mygrid[0][0].plotly_chart(fig_product_sales, use_container_width=True)
mygrid[0][1].plotly_chart(fig_hourly_sales, use_container_width=True)
mygrid[1][0].plotly_chart(fig_price_income,use_container_width=False)

#plot using streamlin columns
#st.plotly_chart(fig_product_sales)
#left_column, right_column = st.columns(2)
#left_column.plotly_chart(fig_hourly_sales, use_container_width=True)
#right_column.plotly_chart(fig_product_sales, use_container_width=True)

# hide_st_style = """
#             <style>
#             #MainMenu {visibility: hidden;}
#             footer {visibility: hidden;}
#             header {visibility: hidden;}
#             </style>
#             """
# st.markdown(hide_st_style, unsafe_allow_html=True)
