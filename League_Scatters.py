import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
from statistics import mean
from math import pi
import streamlit as st
sns.set_style("white")
import warnings
warnings.filterwarnings('ignore')
import matplotlib
import plotly.express as px
import plotly.figure_factory as ff
from plotly.graph_objects import Layout
def click_button():
    st.session_state.clicked = True
def reset_click_button():
    st.session_state.clicked = False
def click_button2():
    st.session_state.clicked = True
def reset_click_button2():
    st.session_state.clicked = False


matplotlib.rcParams.update(matplotlib.rcParamsDefault)
colorscales = px.colors.named_colorscales()

st.title('Player Scatter Plot Program')
st.subheader('Created by Ben Griffis (Twitter: @BeGriffis)\nAll data from Wyscout')

with st.expander('Read App Details'):
    st.write('''
    This app allows you to create your own scatter plots to visualize players.
    First, choose a league, position, & minimum minutes threshold.
    These will determine the sample size of players that scatters will generate for.
    Then, use the metric selectors on the side to choose the X and Y variables.
    ''')

with st.sidebar:
    st.header('Choose Gender')
    gender = st.selectbox('Gender', ('Men','Women'))

if gender == 'Men':
    lg_lookup = pd.read_csv('https://raw.githubusercontent.com/griffisben/Wyscout_Prospect_Research/main/league_info_lookup.csv')
elif gender == 'Women':
    lg_lookup = pd.read_csv('https://raw.githubusercontent.com/griffisben/Wyscout_Prospect_Research/main/league_info_lookup_women.csv')

with st.sidebar:
    st.header('Choose Basic Options')
    with st.expander('Note on Seasons'):
        st.write('''
        Please note that with prior seasons, the players & leagues are correct but the team names can sometimes be off. Ages are also current ages, not ages in the season... I'm working on remedying this.
        ''')
    lg_season = st.selectbox('Season', (['23-24','2024','2023','22-23','2022','21-22']))
    lg_lookup_ssn = lg_lookup[lg_lookup.Season==lg_season]
    league = st.selectbox('League', (lg_lookup_ssn.League.tolist()))
    pos = st.selectbox('Positions', ('Strikers', 'Strikers and Wingers', 'Forwards (AM, W, CF)',
                                    'Forwards no ST (AM, W)', 'Wingers', 'Central Midfielders (DM, CM, CAM)',
                                    'Central Midfielders no CAM (DM, CM)', 'Central Midfielders no DM (CM, CAM)', 'Fullbacks (FBs/WBs)',
                                    'Defenders (CB, FB/WB, DM)', 'Centre-Backs', 'CBs & DMs', 'Goalkeepers'))
full_league_name = f"{league} {lg_season}"


if gender == 'Men':
    df = pd.read_csv(f'https://raw.githubusercontent.com/griffisben/Wyscout_Prospect_Research/main/Main%20App/{full_league_name.replace(" ","%20")}.csv')
elif gender == 'Women':
    df = pd.read_csv(f'https://raw.githubusercontent.com/griffisben/Wyscout_Prospect_Research/main/Main%20App/Women/{full_league_name.replace(" ","%20")}.csv')
df['League'] = full_league_name
df = df.dropna(subset=['Position','Team within selected timeframe', 'Age']).reset_index(drop=True)


df['pAdj Tkl+Int per 90'] = df['PAdj Sliding tackles'] + df['PAdj Interceptions']
df['1st, 2nd, 3rd assists'] = df['Assists per 90'] + df['Second assists per 90'] + df['Third assists per 90']
df['1st, 2nd, 3rd assists per 90'] = df['1st, 2nd, 3rd assists'] / (df['Minutes played'] / 90)
df['xA per Shot Assist'] = df['xA per 90'] / df['Shot assists per 90']
df['Aerial duels won per 90'] = df['Aerial duels per 90'] * (df['Aerial duels won, %']/100)
df['Cards per 90'] = df['Yellow cards per 90'] + df['Red cards per 90']
df['Clean sheets, %'] = df['Clean sheets'] / df['Matches played']
df['npxG'] = df['xG'] - (.76 * df['Penalties taken'])
df['npxG per 90'] = df['npxG'] / (df['Minutes played'] / 90)
df['npxG per shot'] = df['npxG'] / (df['Shots'] - df['Penalties taken'])

df = df.dropna(subset=['Position', 'Team within selected timeframe', 'Age']).reset_index(drop=True)
df.rename(columns={'Team':'xxxTeam', 'Team within selected timeframe':'Team'})

df['Main Position'] = df['Position'].str.split().str[0].str.rstrip(',')
df = df.dropna(subset=['Main Position']).reset_index(drop=True)
position_replacements = {
    'LAMF': 'LW',
    'RAMF': 'RW',
    'LCB3': 'LCB',
    'RCB3': 'RCB',
    'LCB5': 'LCB',
    'RCB5': 'RCB',
    'LB5': 'LB',
    'RB5': 'RB',
    'RWB': 'RB',
    'LWB': 'LB'
}
df['Main Position'] = df['Main Position'].replace(position_replacements)
df.fillna(0,inplace=True)

colorscales2 = [f"{cc}_r" for cc in colorscales]
colorscales += colorscales2

with st.sidebar:
    mins = st.number_input('Minimum Minutes Played', 400, max(df['Minutes played'].astype(int)), 900)
    ages = st.selectbox('Age Group', ('All Ages', 'U23', 'U22', 'U21', 'U20', 'U19', 'U18'))
    xx = st.selectbox('X-Axis Variable', ['Age']+(df.columns[18:len(df.columns)].tolist()))
    yy = st.selectbox('Y-Axis Variable', ['Age']+(df.columns[18:len(df.columns)].tolist()))
    cc = st.selectbox('Point Color Variable', ['Age']+(df.columns[18:len(df.columns)].tolist()))
    cscale = st.selectbox('Point Colorscale', colorscales, index=78)
    
    flipX = xx
    flipY = yy
    
    if 'clicked' not in st.session_state:
        st.session_state.clicked = False
    st.button('Swap X & Y Axes', on_click=click_button)
    if st.session_state.clicked:
        xx = flipY
        yy = flipX
    if 'clicked' not in st.session_state:
        st.session_state.clicked = False
    st.button('Swap X & Y Axes Back', on_click=reset_click_button)

        

ssn = lg_lookup[(lg_lookup['League']==league) & (lg_lookup['Season']==lg_season)].Season.values[0]
date = lg_lookup[(lg_lookup['League']==league) & (lg_lookup['Season']==lg_season)].Date.values[0]
    
# Filter data
def filter_by_position(df, position):
    fw = ["CF", "RW", "LW", "AMF"]
    if position == "Forwards (AM, W, CF)":
        return df[df['Main Position'].str.contains('|'.join(fw), na=False)]
    
    stw = ["CF", "RW", "LW", "LAMF", "RAMF"]
    if position == "Strikers and Wingers":
        return df[df['Main Position'].str.contains('|'.join(stw), na=False)]
    
    fwns = ["RW", "LW", "AMF"]
    if position == "Forwards no ST (AM, W)":
        return df[df['Main Position'].str.contains('|'.join(fwns), na=False)]
    
    wing = ["RW", "LW", "WF", "LAMF", "RAMF"]
    if position == "Wingers":
        return df[df['Main Position'].str.contains('|'.join(wing), na=False)]

    mids = ["DMF", "CMF", "AMF"]
    if position == "Central Midfielders (DM, CM, CAM)":
        return df[df['Main Position'].str.contains('|'.join(mids), na=False)]

    cms = ["CMF", "AMF"]
    if position == "Central Midfielders no DM (CM, CAM)":
        return df[df['Main Position'].str.contains('|'.join(cms), na=False)]

    dms = ["CMF", "DMF"]
    if position == "Central Midfielders no CAM (DM, CM)":
        return df[df['Main Position'].str.contains('|'.join(dms), na=False)]

    fbs = ["LB", "RB", "WB"]
    if position == "Fullbacks (FBs/WBs)":
        return df[df['Main Position'].str.contains('|'.join(fbs), na=False)]

    defs = ["LB", "RB", "WB", "CB", "DMF"]
    if position == "Defenders (CB, FB/WB, DM)":
        return df[df['Main Position'].str.contains('|'.join(defs), na=False)]

    cbdm = ["CB", "DMF"]
    if position == "CBs & DMs":
        return df[df['Main Position'].str.contains('|'.join(cbdm), na=False)]

    cf = ["CF"]
    if position == "Strikers":
        return df[df['Main Position'].str.contains('|'.join(cf), na=False)]

    cb = ["CB"]
    if position == "Centre-Backs":
        return df[df['Main Position'].str.contains('|'.join(cb), na=False)]
    
    gk = ["GK"]
    if position == "Goalkeepers":
        return df[df['Main Position'].str.contains('|'.join(gk), na=False)]

    else:
        return df

dfProspect = df[(df['Minutes played'] >= mins) & (df['League'] == full_league_name)].copy()
dfProspect = filter_by_position(dfProspect, pos)
age_text = ''
if ages != 'All Ages':
    age_text = f' {ages} '
    age_num = int(ages[1:])
    dfProspect = dfProspect[dfProspect['Age']<=age_num]



fig = px.scatter(
    dfProspect,
    x = xx,
    y = yy,
    color = cc,
    color_continuous_scale = cscale,
    text = 'Player',
    hover_data=['Team', 'Age', 'Position', 'Minutes played'],
    hover_name = 'Player',
    title = '%s %s, %s & %s <br><sup>%s%s | Minimum %i minutes played | %s | Code by @BeGriffis</sup>' %(ssn,league,xx,yy,age_text,pos,mins,date),
    width=900,
    height=700)
fig.update_traces(textposition='top right', marker=dict(size=10, line=dict(width=1, color='black')))

fig.add_hline(y=dfProspect[yy].median(), name='Median', line_width=0.5)
fig.add_vline(x=dfProspect[xx].median(), name='Median', line_width=0.5)

st.plotly_chart(fig, theme=None, use_container_width=False)



with st.expander('Metric Glossary'):
    st.write('''
    Short & Medium Pass = Passes shorter than 40 meters.  \n
    Long Pass = Passes longer than 40 meters.  \n
    Smart Pass = A creative and penetrative pass that attempts to break the opposition's defensive lines to gain a significant advantage in attack.  \n
    Cross = Pass from the offensive flanks aimed towards a teammate in the area in front of the opponent’s goal.  \n
    Shot Assist = A pass where the receiver's next action is a shot.  \n
    Expected Assists (xA) = The expected goal (xG) value of shots assisted by a pass. xA only exists on passes that are Shot Assists.  \n
    xA per Shot Assist = The average xA of a player's shot assists.  \n
    Second Assist = The last action of a player from the goalscoring team, prior to an Assist by a teammate.  \n
    Third Assist = The penultimate action of a player from the goalscoring team, prior to an Assist by a teammate.  \n
    Expected Goals (xG) = The likelihood a shot becomes a goal, based on many factors (player position, body part of shot, location of assist, etc.).  \n
    Non-Penalty xG (npxG) = xG from non-penalty shots only.  \n
    npxG per Shot = The average npxG of a player's (non-penalty) shots.  \n
    Acceleration = A run with the ball with a significant speed up.  \n
    Progressive Carry = A continuous ball control by one player attempting to draw the team significantly closer to the opponent goal. (see Wyscout's glossary for more info)  \n
    Progressive Pass = A forward pass that attempts to advance a team significantly closer to the opponent’s goal.  \n
    Defensive Duel = When a player attempts to dispossess an opposition player to stop an attack progressing.  \n
    ''')
        
