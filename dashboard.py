import streamlit as st
import pandas as pd
import plotly.express as px
import io

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(page_title="SSC 2026 Dashboard", layout="wide")

# Custom CSS for styling metrics
st.markdown("""
<style>
    div[data-testid="metric-container"] {
        background-color: #f0f2f6;
        border: 1px solid #d6d6d6;
        padding: 10px;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. DATA EMBEDDING (February 2026 Data)
# -----------------------------------------------------------------------------

# --- LOB COMPARISON ---
csv_lob = """LOB,Sum of Sarawak,Sum of Sabah,Sum of East Coast,Sum of Southern,Sum of Northern,Sum of Central
Apple Watch & iPhone (Fail),27,43,20,69,64,84
Apple Watch & iPhone (Pass),33,23,25,34,64,48
iPad (Fail),21,44,24,68,57,84
iPad (Pass),39,22,21,35,70,48
Mac (Fail),0,0,0,0,0,0
Mac (Pass),0,0,0,0,0,0
Grand Total,120,132,90,206,255,264""".strip()

# --- REGION PERFORMANCE ---
csv_regional = """Region,Sum of Pass,Sum of Fail,Sum of Total Headcount
Central,48,84,132
East Coast,21,24,45
Northern,70,57,127
Sabah,22,44,66
Sarawak ,39,21,60
Southern,35,68,103
Grand Total,235,298,533""".strip()

# --- CENTRAL OUTLETS ---
csv_central = """Outlet,Sum of Pass,Sum of Fail,Sum of Total Crew
AP,2,3,5
BG,0,4,4
BK,2,2,4
BV,4,1,5
EK,3,2,5
EV,1,4,5
LY,2,3,5
MF,3,3,6
MT,4,2,6
PR,0,5,5
PS,1,4,5
PU,2,3,5
PY,9,7,16
QS,5,0,5
SA,0,7,7
SL,1,4,5
SWKLAA,0,3,3
SWKLGC,1,3,4
SWSGKG,1,2,3
SWSGKW,2,3,5
SWSGSY,2,3,5
TG,0,7,7
UK,1,0,1
UP,0,5,5
WW,2,4,6
Grand Total,48,84,132""".strip()

# --- NORTHERN OUTLETS ---
csv_northern = """Outlet,Sum of Pass,Sum of Fail,Sum of Total Crew
AC,5,2,7
AJ,7,0,7
AL,3,4,7
AR,0,8,8
AS,0,5,5
BM,3,3,6
GT,7,8,15
KI,5,0,5
LW,4,0,4
PG,4,3,7
QB,9,6,15
SQ,2,3,5
SU,9,4,13
SWKDSW,1,3,4
TM,2,4,6
TS,4,3,7
VM,5,1,6
Grand Total,70,57,127""".strip()

# --- SOUTHERN OUTLETS ---
csv_southern = """Outlet,Sum of Pass,Sum of Fail,Sum of Total Crew
BP,3,4,7
JB,6,5,11
KJ,3,4,7
KP,1,3,4
MP,4,0,4
NL,3,5,8
PD,2,10,12
SC,0,6,6
SG,1,5,6
SR,3,4,7
SWJHBX,0,4,4
SWJHDS,2,3,5
SWJHEL,0,5,5
SWJHGP,1,4,5
SWNSLJ,2,2,4
SWNSLT,0,3,3
WE,4,1,5
Grand Total,35,68,103""".strip()

# --- EAST COAST OUTLETS ---
csv_east = """Outlet,Sum of Pass,Sum of Fail,Sum of Total Crew
EC,4,3,7
KA,2,5,7
KM,0,6,6
KT,4,0,4
MM,3,0,3
SWPHCH,0,4,4
SWPHLK,2,2,4
SWTRGD,4,1,5
SWTRMY,2,3,5
Grand Total,21,24,45""".strip()

# --- SABAH OUTLETS ---
csv_sabah = """Row Labels,Sum of Pass,Sum of Fail,Sum of Total Crew
HS,5,1,6
IG,4,15,19
PQ,6,1,7
SS,0,10,10
SWLBFP,0,5,5
SWSBCC,0,3,3
SWSBCM,2,3,5
SWSBKK,1,3,4
TW,4,3,7
Grand Total,22,44,66""".strip()

# --- SARAWAK OUTLETS ---
csv_sarawak = """Row Labels,Sum of Pass,Sum of Fail,Sum of Total Crew
CK,5,2,7
MB,5,0,5
MR,3,2,5
SB,4,1,5
SP,9,3,12
SWSWDM,1,4,5
SWSWER,1,4,5
SY,2,4,6
VC,9,1,10
Grand Total,39,21,60""".strip()

# -----------------------------------------------------------------------------
# 3. DATA PROCESSING FUNCTIONS
# -----------------------------------------------------------------------------

def clean_excel_pivot_csv(df):
    """
    Cleans CSVs that come from Excel Pivot Tables:
    1. Removes 'Grand Total' row.
    2. Removes 'Sum of ' prefix from value columns.
    """
    # Remove Grand Total row
    df = df[df.iloc[:, 0] != 'Grand Total'].copy()
    
    # Rename columns: Remove "Sum of "
    df.columns = df.columns.str.replace('Sum of ', '')
    
    return df

@st.cache_data
def load_and_clean_data():
    # --- 1. Regional Data ---
    df_reg = pd.read_csv(io.StringIO(csv_regional), skipinitialspace=True)
    df_reg = clean_excel_pivot_csv(df_reg)
    if 'Row Labels' in df_reg.columns:
        df_reg = df_reg.rename(columns={'Row Labels': 'Region'})
    df_reg['Region'] = df_reg['Region'].str.strip()
    
    # --- 2. LOB Data ---
    df_lob = pd.read_csv(io.StringIO(csv_lob), skipinitialspace=True)
    df_lob = clean_excel_pivot_csv(df_lob)
    
    if 'LOB' in df_lob.columns:
        df_lob = df_lob.rename(columns={'LOB': 'Result'})
    elif 'Row Labels' in df_lob.columns:
        df_lob = df_lob.rename(columns={'Row Labels': 'Result'})
    
    # --- 3. Outlet Data ---
    # Helper to process outlet files
    def process_outlet_file(csv_data, region_name):
        df = pd.read_csv(io.StringIO(csv_data), skipinitialspace=True)
        df = clean_excel_pivot_csv(df)
        
        # Rename first column to 'Outlet' (handles 'Row Labels' vs 'Outlet' discrepancy)
        first_col = df.columns[0]
        df = df.rename(columns={first_col: 'Outlet'})
        
        df['Region'] = region_name
        return df

    # Process all outlet files
    outlets = [
        process_outlet_file(csv_central, 'Central'),
        process_outlet_file(csv_northern, 'Northern'),
        process_outlet_file(csv_southern, 'Southern'),
        process_outlet_file(csv_east, 'East Coast'),
        process_outlet_file(csv_sabah, 'Sabah'),
        process_outlet_file(csv_sarawak, 'Sarawak')
    ]
    
    df_outlet_all = pd.concat(outlets, ignore_index=True)
    
    # Ensure numeric columns (Pivot exports sometimes have formatting issues)
    cols_to_numeric = ['Pass', 'Fail', 'Total Crew', 'Total Headcount']
    
    # Clean Outlet Data Types
    for c in cols_to_numeric:
        if c in df_outlet_all.columns:
            df_outlet_all[c] = pd.to_numeric(df_outlet_all[c], errors='coerce').fillna(0)

    # Clean Regional Data Types
    for c in cols_to_numeric:
        if c in df_reg.columns:
            df_reg[c] = pd.to_numeric(df_reg[c], errors='coerce').fillna(0)

    return df_reg, df_lob, df_outlet_all

def process_lob_data(df):
    # Melt from wide (Regions in columns) to long
    # Identify region columns (all columns except 'Result')
    region_cols = [c for c in df.columns if c != 'Result']
    
    df_long = df.melt(id_vars=['Result'], value_vars=region_cols, var_name='Region', value_name='Count')
    
    # Ensure Count is numeric
    df_long['Count'] = pd.to_numeric(df_long['Count'], errors='coerce').fillna(0)
    
    # Extract Status and Product
    df_long['Status'] = df_long['Result'].apply(lambda x: 'Pass' if '(Pass)' in str(x) else 'Fail')
    df_long['Product'] = df_long['Result'].apply(lambda x: str(x).split(' (')[0])
    
    return df_long

# Load Data
try:
    df_regional, df_lob, df_outlet = load_and_clean_data()
except Exception as e:
    st.error(f"Error processing data: {e}")
    st.stop()

# -----------------------------------------------------------------------------
# 4. SIDEBAR
# -----------------------------------------------------------------------------
with st.sidebar:
    st.header("SSC 2026 Dashboard")
    st.write("Explorer Quest - Feb 2026") # Updated to Feb
    
    view_selection = st.selectbox(
        "Select Dataset:",
        ["Regional Performance", "Outlet Performance", "LOB Comparison"]
    )
    
    st.markdown("---")
    st.caption("© 2026 Insight Team")

# -----------------------------------------------------------------------------
# 5. MAIN LOGIC
# -----------------------------------------------------------------------------

st.title(f"📊 {view_selection}")

active_df = pd.DataFrame()
chart_fig = None
total_pass = 0
total_fail = 0
total_vol = 0

if view_selection == "Regional Performance":
    active_df = df_regional
    
    # Use "Total Headcount" as volume for Regional
    vol_col = 'Total Headcount' if 'Total Headcount' in active_df.columns else active_df.columns[-1]
    
    total_pass = active_df['Pass'].sum()
    total_fail = active_df['Fail'].sum()
    total_vol = active_df[vol_col].sum()
    
    # Chart
    chart_df = active_df.melt(id_vars=['Region'], value_vars=['Pass', 'Fail'], var_name='Status', value_name='Count')
    chart_fig = px.bar(chart_df, x='Region', y='Count', color='Status', barmode='group',
                       color_discrete_map={'Pass': '#00CC96', 'Fail': '#EF553B'}, 
                       title="Pass vs Fail by Region")

elif view_selection == "Outlet Performance":
    active_df = df_outlet
    
    # Filter
    regions_list = sorted(active_df['Region'].unique().tolist())
    selected_region = st.sidebar.multiselect("Filter by Region:", regions_list, default=regions_list[0] if regions_list else None)
    
    if selected_region:
        filtered_df = active_df[active_df['Region'].isin(selected_region)]
        title_text = f"Outlet Performance ({', '.join(selected_region)})"
    else:
        filtered_df = active_df
        title_text = "Outlet Performance (All)"
    
    # Metrics
    if not filtered_df.empty:
        total_pass = filtered_df['Pass'].sum()
        total_fail = filtered_df['Fail'].sum()
        # For outlets, use Pass + Fail or Total Crew if available
        if 'Total Crew' in filtered_df.columns:
            total_vol = filtered_df['Total Crew'].sum()
        else:
            total_vol = total_pass + total_fail
        
        # Chart
        chart_df = filtered_df.melt(id_vars=['Outlet'], value_vars=['Pass', 'Fail'], var_name='Status', value_name='Count')
        chart_df = chart_df.sort_values(by='Count', ascending=False)
        
        chart_fig = px.bar(chart_df, x='Outlet', y='Count', color='Status', barmode='group',
                           color_discrete_map={'Pass': '#00CC96', 'Fail': '#EF553B'}, 
                           title=title_text)

elif view_selection == "LOB Comparison":
    active_df = df_lob
    processed_lob = process_lob_data(df_lob)
    
    total_pass = processed_lob[processed_lob['Status'] == 'Pass']['Count'].sum()
    total_fail = processed_lob[processed_lob['Status'] == 'Fail']['Count'].sum()
    total_vol = total_pass + total_fail
    
    # Chart
    chart_fig = px.bar(processed_lob, x='Product', y='Count', color='Region',
                       facet_row='Status',
                       title="Product Performance: Regional Breakdown")
    chart_fig.update_layout(height=600)

# Calculate Pass Rate safely
pass_rate = (total_pass / total_vol) * 100 if total_vol > 0 else 0

# -----------------------------------------------------------------------------
# 6. LAYOUT
# -----------------------------------------------------------------------------

# ROW 1: KPIs
st.subheader("1. Key Performance Indicators")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Volume", f"{int(total_vol)}")
c2.metric("Total Pass", f"{int(total_pass)}")
c3.metric("Total Fail", f"{int(total_fail)}")
c4.metric("Pass Rate", f"{pass_rate:.1f}%")

st.markdown("---")

# ROW 2: CHART
st.subheader("2. Graphical Analysis")
if chart_fig:
    st.plotly_chart(chart_fig, use_container_width=True)
else:
    st.info("Select a region to view outlet performance.")

st.markdown("---")

# ROW 3: TABLE
st.subheader("3. Data Table")

display_df = active_df.copy()

# Show filtered data for outlets
if view_selection == "Outlet Performance" and 'filtered_df' in locals():
    display_df = filtered_df.copy()

if not display_df.empty and 'Pass' in display_df.columns and 'Fail' in display_df.columns:
    # Calculate Total for rate calc (Ensure we don't divide by zero)
    total_col = display_df['Pass'] + display_df['Fail']
    
    display_df['Pass Rate (%)'] = display_df.apply(
        lambda x: (x['Pass'] / (x['Pass'] + x['Fail']) * 100) if (x['Pass'] + x['Fail']) > 0 else 0, 
        axis=1
    ).round(1)
    
    st.dataframe(
        display_df.style.background_gradient(cmap='RdYlGn', subset=['Pass Rate (%)'], vmin=0, vmax=100),
        use_container_width=True
    )
else:
    st.dataframe(display_df, use_container_width=True)
