import streamlit as st
import pandas as pd
import psycopg2
from sqlalchemy import create_engine

@st.cache_resource
def get_db_connection():
    engine = create_engine(
        'postgresql://airflow:airflow@localhost:5432/nba_db'
    )
    return engine

# Load data
@st.cache_data
def load_cumulative_win_loss_data():
    engine  = get_db_connection()
    query = "SELECT * FROM silver.game_logs_with_cumulative_win_loss"
    df = pd.read_sql(query, engine)
    return df

@st.cache_data
def load_playoff_results():
    engine = get_db_connection()
    query = "SELECT * FROM gold.playoff_results ORDER BY year, po_wins DESC"
    df = pd.read_sql(query, engine)
    return df

@st.cache_data
def load_40_20_data():
    engine  = get_db_connection()
    query = "SELECT * FROM gold.rule_40_20 ORDER BY year, team_name"
    df = pd.read_sql(query, engine)
    return df

@st.cache_data
def load_champion_data():
    engine  = get_db_connection()
    query = "SELECT * FROM gold.champion_40_20 ORDER BY year DESC"
    df = pd.read_sql(query, engine)
    return df

# Page config
st.set_page_config(
    layout='wide',
    page_title="NBA 40-20 Rule Analysis",
    page_icon='basketball-ball.png')
st.title("🏀 NBA 40-20 Rule Analysis")

# Load data
cumu_win_loss_df = load_cumulative_win_loss_data()
playoff_df = load_playoff_results()
data_40_20 = load_40_20_data()
champion_data = load_champion_data()

# Sidebar filters
st.sidebar.header("Filters")
selected_year = st.sidebar.selectbox(
    "Select Year",
    sorted(data_40_20['year'].unique()),
    index=len(data_40_20['year'].unique()) - 1
)

wins_threshold = st.sidebar.slider(
    "Wins Threshold",
    min_value=0,
    max_value=82,
    value=40,
    step=1,
    help="Custom wins threshold before losses"
)

losses_threshold = st.sidebar.slider(
    "Losses Threshold",
    min_value=0,
    max_value=82,
    value=20,
    step=1,
    help="Custom losses threshold"
)

# Main tabs
tab1, tab2, tab3 = st.tabs(["Custom Rule Analysis", "Champions Analysis", "Full Season Breakdown"])

# Tab 1: Custom Rule Analysis
with tab1:
    st.subheader(f"Teams achieving {wins_threshold}W before {losses_threshold}L in {selected_year}")
    
    # Apply custom rule to all years
    all_data = data_40_20.copy()
    all_data['custom_rule'] = (all_data['wins_at_20th_loss'].isna()) | (all_data['wins_at_20th_loss'] >= wins_threshold)
    
    # Load playoff results for all years
    playoff_df = load_playoff_results()
    
    # Merge with 40-20 data
    all_data = all_data.merge(playoff_df[['team_id', 'year', 'playoff_round']], on=['team_id', 'year'], how='left')
    
    # Filter to satisfied teams
    satisfied = all_data[all_data['custom_rule'] == True].sort_values(['year', 'team_name'], ascending=[False, True])
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Teams Satisfied (All Time)", len(satisfied))
    with col2:
        st.metric("Unique Seasons", satisfied['year'].nunique())
    
    st.dataframe(
        satisfied[['year', 'team_name', 'final_wins', 'final_losses', 'wins_at_20th_loss', 'playoff_round']],
        width='stretch'
    )

# Tab 2: Champions Analysis
with tab2:
    st.subheader("Championship Analysis: 40-20 Rule Adherence")
    
    satisfied_count = len(champion_data[champion_data['achieved_40_20_rule'] == True])
    total_count = len(champion_data)
    pct = (satisfied_count / total_count * 100) if total_count > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Champions Satisfied Rule", satisfied_count)
    with col2:
        st.metric("Total Champions", total_count)
    with col3:
        st.metric("Percentage", f"{pct:.1f}%")
    
    st.dataframe(
        champion_data[['year', 'team_name', 'wins', 'losses', 'achieved_40_20_rule', 'rule_verdict']],
        width='stretch'
    )
    
    # Exceptions
    st.subheader("Notable Exceptions")
    exceptions = champion_data[champion_data['achieved_40_20_rule'] == False]
    if len(exceptions) > 0:
        st.dataframe(
            exceptions[['year', 'team_name', 'wins_at_20th_loss']],
            width='stretch'
        )
    else:
        st.write("No exceptions found in this dataset")

# Tab 3: Full Season Breakdown
with tab3:
    
    playoff_df = playoff_df[['year', 'team_id', 'gp', 'wins', 'losses', 'conf_rank','po_wins','po_losses', 'playoff_round']]
    data_40_20 = data_40_20[['year', 'team_id', 'team_name', 'date_of_20th_loss', 'wins_at_20th_loss','achieved_40_20_rule']]

    df = pd.merge(left=playoff_df, right=data_40_20, on=['team_id', 'year'], how='inner')

    years = sorted(df['year'].unique(), reverse=True)

    selected_year = st.selectbox(
        "Select Year",
        years,
        index=None,
        placeholder='Select year from dropdown...'
    )
    
    if selected_year:
        st.subheader(f"All Teams - {selected_year} Season")
    
        year_data = df[df['year'] == selected_year].sort_values(['po_wins', 'wins'], ascending=False)
        
        # Filter option
        exclude_missed = st.checkbox("Exclude teams that missed playoffs", value=False)
        if exclude_missed:
            year_data = year_data[year_data['playoff_round'] != 'Missed Playoffs']
        
        st.dataframe(
            year_data[['team_name', 'wins', 'losses', 'wins_at_20th_loss', 'achieved_40_20_rule', 'playoff_round']],
            width='stretch',
            column_config={
                "achieved_40_20_rule": st.column_config.CheckboxColumn("40-20 Rule")
            }
        )
    