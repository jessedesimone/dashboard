#!/usr/local/bin/python3.9
'''
to run type in terminal:
> 'Python3.9 dashboard2.py'     #activation of streamlit; throws error without
> 'streamlit run dashboard2.py'         #run application

'''

#import packages
import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
import plotly.graph_objects as go
import numpy as np
warnings.filterwarnings('ignore')

#define paths and infile
top = os.getcwd()
data_dir = os.path.join(top, 'data')
infile = os.path.join(data_dir, 'biomarkers.xlsx')

#set page configuration
st.set_page_config(page_title="Biomarker Data Visualization", 
                   page_icon=":brain:",
                   layout="wide")

#read data
@st.cache_data
def get_data_from_excel():
    df = pd.read_excel(
        io=infile,
        engine="openpyxl",
        #sheet_name="",
        #nrows=1000,
    )
    #create new "sex column"
    sex_dict ={1 : 'Male', 2 : 'Female'}
    df['sex_bin'] = df['sex'].map(sex_dict)
    return df

df = get_data_from_excel()

#comment to turn off dataframe return
#st.dataframe(df)

# ---- SIDEBAR ----
st.sidebar.header("Please Filter Here:")
group = st.sidebar.multiselect(
    "Select the Patient Group:",
    options=df["grp"].unique(),
    default=df["grp"].unique()
)

sex = st.sidebar.multiselect(
    "Select the Patient Sex:",
    options=df["sex_bin"].unique(),
    default=df["sex_bin"].unique(),
)

# values = st.sidebar.slider(
#     'Select a range of values',
#     0.0, 3.0, (0.05, 2.71))

df_selection = df.query(
    "(grp == @group) and (sex_bin == @sex)"
)

#comment to turn off dataframe return with selection
#st.dataframe(df_selection)

# Check if the dataframe is empty:
if df_selection.empty:
    st.warning("No data available based on the current filter settings!")
    st.stop() # This will halt the app from further execution.

# ---- MAIN PAGE ----
st.title(":brain: Biomarker Dashboard")
st.markdown("##")

#define key performance indicators
total_patients = int(df_selection["subj_id"].count())
average_age = round(df_selection["age"].mean(), 1)
average_ptau = round(df_selection["ptau217"].mean(), 1)
average_nfl = round(df_selection["nfl"].mean(), 1)
average_gfap = round(df_selection["gfap"].mean(), 1)

#create dashboard with KPIs
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.subheader("Total Patients:")
    st.subheader(f"{total_patients:,}")
with col2:
    st.subheader("Average Age:")
    st.subheader(f"{average_age}")
with col3:
    st.subheader("Plasma ptau217:")
    st.subheader(f"{average_ptau}")
with col4:
    st.subheader("Plasma NfL:")
    st.subheader(f"{average_nfl}")
with col5:
    st.subheader("Average GFAP:")
    st.subheader(f"{average_gfap}")

st.markdown("""---""")

#grouped bar chart
ptau_by_grp = df_selection.groupby(by=["grp"])[["ptau217"]].mean().sort_values(by="ptau217")
fig_ptau_by_grp = px.bar(
    ptau_by_grp,
    x=ptau_by_grp.index,
    y="ptau217",
    orientation="v",
    title="<b>Plasma p-tau217 by Group</b>",
    color_discrete_sequence=["#0083B8"] * len(ptau_by_grp),
    template="plotly_white",
)
fig_ptau_by_grp.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False))
)

nfl_by_grp = df_selection.groupby(by=["grp"])[["nfl"]].mean().sort_values(by="nfl")
fig_nfl_by_grp = px.bar(
    nfl_by_grp,
    x=nfl_by_grp.index,
    y="nfl",
    orientation="v",
    title="<b>Plasma NfL by Group</b>",
    color_discrete_sequence=["#0083B8"] * len(ptau_by_grp),
    template="plotly_white",
)
fig_nfl_by_grp.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False))
)

gfap_by_grp = df_selection.groupby(by=["grp"])[["gfap"]].mean().sort_values(by="gfap")
fig_gfap_by_grp = px.bar(
    gfap_by_grp,
    x=gfap_by_grp.index,
    y="gfap",
    orientation="v",
    title="<b>Plasma GFAP by Group</b>",
    color_discrete_sequence=["#0083B8"] * len(gfap_by_grp),
    template="plotly_white",
)
fig_gfap_by_grp.update_layout(
    plot_bgcolor="rgba(0,0,0,0)",
    xaxis=(dict(showgrid=False))
)

ptau_nfl = df_selection[['grp', 'nfl', 'ptau217']]
fig_nfl_by_ptau = px.scatter(
    ptau_nfl, 
    x = "nfl", 
    y = "ptau217", 
    #size = "",
    color = "grp",
    trendline="ols",
    #marginal_y="violin",
    #marginal_x="box",
    title="<b>Test</b>",
)
fig_nfl_by_ptau.update_layout(
    xaxis=dict(tickmode="linear"),
    plot_bgcolor="rgba(0,0,0,0)",
    yaxis=(dict(showgrid=False)),
)

ptau_gfap = df_selection[['grp', 'ptau217', 'gfap']]
fig_ptau_by_gfap = px.scatter(
    ptau_gfap, 
    x = "gfap", 
    y = "ptau217", 
    #size = "",
    color = "grp",
    trendline="ols",
    #marginal_y="violin",
    #marginal_x="box",
    title="<b>Test</b>",
)
fig_ptau_by_gfap.update_layout(
    xaxis=dict(tickmode="linear"),
    plot_bgcolor="rgba(0,0,0,0)",
    yaxis=(dict(showgrid=False)),
)

cols = ['ptau217', 'nfl', 'gfap']
df_corr = df_selection[cols].corr() # Generate correlation matrix
fig = go.Figure()
fig.add_trace(
    go.Heatmap(
        x = df_corr.columns,
        y = df_corr.index,
        z = np.array(df_corr)
    )
)

#customization
# create grid for display
def make_grid(cols,rows):
    grid = [0]*cols
    for i in range(cols):
        with st.container():
            grid[i] = st.columns(rows)
    return grid
mygrid = make_grid(2,3)

#plot using grid customization
mygrid[0][0].plotly_chart(fig_ptau_by_grp, use_container_width=True)
mygrid[0][1].plotly_chart(fig_nfl_by_grp, use_container_width=True)
mygrid[0][2].plotly_chart(fig_gfap_by_grp, use_container_width=True)
mygrid[1][0].plotly_chart(fig, use_container_width=True)
mygrid[1][1].plotly_chart(fig_nfl_by_ptau, use_container_width=True)
mygrid[1][2].plotly_chart(fig_ptau_by_gfap, use_container_width=True)

placeholder = st.empty()
# Replace the text with a chart:
placeholder.line_chart({"data": [1, 5, 2, 6]})

# #plot using streamlin columns
# #st.plotly_chart(fig_product_sales)
# #left_column, right_column = st.columns(2)
# #left_column.plotly_chart(fig_hourly_sales, use_container_width=True)
# #right_column.plotly_chart(fig_product_sales, use_container_width=True)

# # hide_st_style = """
# #             <style>
# #             #MainMenu {visibility: hidden;}
# #             footer {visibility: hidden;}
# #             header {visibility: hidden;}
# #             </style>
# #             """
# # st.markdown(hide_st_style, unsafe_allow_html=True)
