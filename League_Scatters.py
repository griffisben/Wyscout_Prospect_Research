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

matplotlib.rcParams.update(matplotlib.rcParamsDefault)

st.title('AFC Scatter Plot Program')
st.subheader("All data from Wyscout (please see footer for each league's latest data update)")
st.subheader('Created by Ben Griffis (Twitter: @BeGriffis)')

with st.expander('Read App Details'):
    st.write('''
    This app allows you to create your own scatter plots to visualize players.
    First, choose a league, position, & minimum minutes threshold.
    These will determine the sample size of players that scatters will generate for.
    Then, use the metric selectors on the side to choose the X and Y variables.
    ''')

df = pd.read_csv('https://raw.githubusercontent.com/griffisben/Wyscout_Prospect_Research/main/Japan_Korea_2022_WS.csv')
df = df.dropna(subset=['Position','Team within selected timeframe', 'Age']).reset_index(drop=True)

with st.sidebar:
    st.header('Choose Basic Options')
    league = st.selectbox('League', ('Indian Super League', 'K League 1', 'K League 2', 'J1', 'J2', 'J3', 'Chinese Super League',
                                     'Indonesian Liga 1', 'Thai League 1', 'Malaysian Super League',
                                     'Latvian Virsliga', 'Estonian Meistriliiga', 'Allsvenskan',
                                     'Eliteserien', 'Veikkausliiga', 'MLS', 'Argentinian Primera División', 'Chilean Primera División', 'Peruvian Primera División',
                                    'Uruguayan Primera División', 'Brasileirão', 'Uzbek Super League', 'Kazakh Premier League',
                                    'English Championship', 'English League One', 'English League Two',
                                    '1. Bundesliga', '2. Bundesliga', '3. Liga',
                                     'Ekstraklasa', 'Hungarian NB I', 'Czech Fortuna Liga', 'Slovak Super Liga', ))
    pos = st.selectbox('Positions', ('Strikers', 'Strikers and Wingers', 'Forwards (AM, W, CF)',
                                    'Forwards no ST (AM, W)', 'Wingers', 'Central Midfielders (DM, CM, CAM)',
                                    'Central Midfielders no CAM (DM, CM)', 'Central Midfielders no DM (CM, CAM)', 'Fullbacks (FBs/WBs)',
                                    'Defenders (CB, FB/WB, DM)', 'Centre-Backs'))
    mins = st.number_input('Minimum Minutes Played', 300, max(df['Minutes played'].astype(int)), 900)
    xx = st.selectbox('X-Axis', (df.columns[8:len(df.columns)-1].tolist()))
    yy = st.selectbox('Y-Axis', (df.columns[8:len(df.columns)-1].tolist()))

df['pAdj Tkl+Int per 90'] = df['PAdj Sliding tackles'] + df['PAdj Interceptions']
df['1st, 2nd, 3rd assists'] = df['Assists per 90'] + df['Second assists per 90'] + df['Third assists per 90']
df['xA per Shot Assist'] = df['xA per 90'] / df['Shot assists per 90']
df['Aerial duels won per 90'] = df['Aerial duels per 90'] * (df['Aerial duels won, %']/100)
df['Cards per 90'] = df['Yellow cards per 90'] + df['Red cards per 90']
df['Clean sheets, %'] = df['Clean sheets'] / df['Matches played']
df['npxG'] = df['xG'] - (.76 * df['Penalties taken'])
df['npxG per 90'] = df['npxG'] / (df['Minutes played'] / 90)
df['npxG per shot'] = df['npxG'] / (df['Shots'] - df['Penalties taken'])

df = df.dropna(subset=['Position', 'Team within selected timeframe', 'Age']).reset_index(drop=True)


df['Main Position'] = ''
for i in range(len(df)):
    df['Main Position'][i] = df['Position'][i].split()[0]


# Filter data
dfProspect = df[(df['Minutes played']>=mins) & (df['League']==league)].copy()


if pos == 'Forwards (AM, W, CF)':
    dfProspect = dfProspect[(dfProspect['Main Position'].str.contains('CF')) |
                           (dfProspect['Main Position'].str.contains('RW')) |
                           (dfProspect['Main Position'].str.contains('LW')) |
                           (dfProspect['Main Position'].str.contains('AMF'))]
if pos == 'Strikers and Wingers':
    dfProspect = dfProspect[(dfProspect['Main Position'].str.contains('CF')) |
                           (dfProspect['Main Position'].str.contains('RW')) |
                           (dfProspect['Main Position'].str.contains('LW'))]
if pos == 'Forwards no ST (AM, W)':
    dfProspect = dfProspect[(dfProspect['Main Position'].str.contains('AMF')) |
                           (dfProspect['Main Position'].str.contains('RW')) |
                           (dfProspect['Main Position'].str.contains('LW')) |
#                                (dfProspect['Main Position'].str.contains('LAMF')) |
                           (dfProspect['Main Position'].str.contains('AMF'))]
if pos == 'Wingers':
    dfProspect = dfProspect[(dfProspect['Main Position'].str.contains('WF')) |
                           (dfProspect['Main Position'].str.contains('LAMF')) |
                           (dfProspect['Main Position'].str.contains('RAMF')) |
                           (dfProspect['Main Position'].str.contains('LW')) |
                           (dfProspect['Main Position'].str.contains('RW'))]
    dfProspect = dfProspect[~dfProspect['Main Position'].str.contains('WB')]
if pos == 'Central Midfielders (DM, CM, CAM)':
    dfProspect = dfProspect[(dfProspect['Main Position'].str.contains('CMF')) |
                           (dfProspect['Main Position'].str.contains('DMF')) |
                           (dfProspect['Main Position'].str.contains('AMF'))]
if pos == 'Central Midfielders no CAM (DM, CM)':
    dfProspect = dfProspect[(dfProspect['Main Position'].str.contains('CMF')) |
                           (dfProspect['Main Position'].str.contains('DMF'))]
if pos == 'Central Midfielders no DM (CM, CAM)':
    dfProspect = dfProspect[(dfProspect['Main Position'].str.contains('CMF')) |
                           (dfProspect['Main Position'].str.contains('AMF'))]
    dfProspect = dfProspect[~dfProspect['Main Position'].str.contains('LAMF')]
    dfProspect = dfProspect[~dfProspect['Main Position'].str.contains('RAMF')]

if pos == 'Fullbacks (FBs/WBs)':
    dfProspect = dfProspect[(dfProspect['Main Position'].str.contains('LB')) |
                           (dfProspect['Main Position'].str.contains('RB')) |
                           (dfProspect['Main Position'].str.contains('WB'))]
if pos == 'Defenders (CB, FB/WB, DM)':
    dfProspect = dfProspect[(dfProspect['Main Position'].str.contains('LB')) |
                           (dfProspect['Main Position'].str.contains('RB')) |
                           (dfProspect['Main Position'].str.contains('WB')) |
                           (dfProspect['Main Position'].str.contains('CB')) |
                           (dfProspect['Main Position'].str.contains('LCB')) |
                           (dfProspect['Main Position'].str.contains('RCB')) |
                           (dfProspect['Main Position'].str.contains('DMF'))]
if pos == 'Centre-Backs':
    dfProspect = dfProspect[(dfProspect['Main Position'].str.contains('CB'))]

if pos == 'Strikers':
    dfProspect = dfProspect[(dfProspect['Main Position'].str.contains('CF'))]


fig = px.scatter(
    df,
    x = xx,
    y = yy,
    text = 'Player',
    hover_data=['Team within selected timeframe', 'Age', 'Main Position',],
    hover_name = 'Player')

st.plotly_chart(fig, theme="streamlit", use_container_width=True)


