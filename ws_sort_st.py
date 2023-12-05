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
from PIL import Image
import urllib.request
matplotlib.rcParams.update(matplotlib.rcParamsDefault)
@st.cache_data()
def read_csv(link):
    return pd.read_csv(link)

def rank_column(df, column_name):
    return stats.rankdata(df[column_name], "average") / len(df[column_name])
def rank_column_inverse(df, column_name):
    return 1-stats.rankdata(df[column_name], "average") / len(df[column_name])

st.title('Soccer Prospect Research & Radar Creation')
st.subheader("All data from Wyscout")
st.subheader('Created by Ben Griffis (Twitter: @BeGriffis)')

with st.expander('Read App Details'):
    st.write('''
    This app helps you find players that meet specific criteria.
    First, choose a league, position, minimum minutes threshold, and maximum age.
    These will determine the sample size of players that percentile ratings will generate for.
    Then, use the metric filters on the sidebar to pass minimum percentile ranking thresholds.
    Players not meeting all of these criteria will be filtered out.
    Finally, you can type or copy+paste any of the player names into the textbox below to generate their radar chart.
    ''')

##################################################################

lg_lookup = read_csv('https://raw.githubusercontent.com/griffisben/Wyscout_Prospect_Research/main/league_info_lookup.csv')
df = read_csv('https://raw.githubusercontent.com/griffisben/Wyscout_Prospect_Research/main/WS_Data.csv')
df = df.dropna(subset=['Position','Team within selected timeframe', 'Age']).reset_index(drop=True)

with st.sidebar:
    st.header('Choose Basic Options')
    league = st.selectbox('League', (lg_lookup.League.tolist()))
    pos = st.selectbox('Positions', ('Strikers', 'Strikers and Wingers', 'Forwards (AM, W, CF)',
                                    'Forwards no ST (AM, W)', 'Wingers', 'Central Midfielders (DM, CM, CAM)',
                                    'Central Midfielders no CAM (DM, CM)', 'Central Midfielders no DM (CM, CAM)', 'Fullbacks (FBs/WBs)',
                                    'Defenders (CB, FB/WB, DM)', 'Centre-Backs', 'CBs & DMs'))
    mins = st.number_input('Minimum Minutes Played', 400, max(df['Minutes played'].astype(int)), 900)
    maxage = st.slider('Max Age', min(df.Age.astype(int)), max(df.Age.astype(int)), 25)
    callout = st.selectbox('Data Labels on Bars', ('Per 90', 'Percentile'))


#####################################################################

############################################################################

df['pAdj Tkl+Int per 90'] = df['PAdj Sliding tackles'] + df['PAdj Interceptions']
df['1st, 2nd, 3rd assists'] = df['Assists per 90'] + df['Second assists per 90'] + df['Third assists per 90']
df['xA per Shot Assist'] = df['xA per 90'] / df['Shot assists per 90']
df['xA per Shot Assist'] = [0 if df['Shot assists per 90'][i]==0 else df['xA per 90'][i] / df['Shot assists per 90'][i] for i in range(len(df))]
df['Aerial duels won per 90'] = df['Aerial duels per 90'] * (df['Aerial duels won, %']/100)
df['Cards per 90'] = df['Yellow cards per 90'] + df['Red cards per 90']
df['Clean sheets, %'] = df['Clean sheets'] / df['Matches played']
df['npxG'] = df['xG'] - (.76 * df['Penalties taken'])
df['npxG per 90'] = df['npxG'] / (df['Minutes played'] / 90)
df['npxG per shot'] = df['npxG'] / (df['Shots'] - df['Penalties taken'])
df['npxG per shot'] = [0 if df['Shots'][i]==0 else df['npxG'][i] / (df['Shots'][i] - df['Penalties taken'][i]) for i in range(len(df))]

df = df.dropna(subset=['Position', 'Team within selected timeframe', 'Age']).reset_index(drop=True)

df['Main Position'] = df['Position'].str.split().str[0].str.rstrip(',')
df['Main Position'] = df['Main Position'].replace('LAMF','LW')
df['Main Position'] = df['Main Position'].replace('RAMF','RW')
df['Main Position'] = df['Main Position'].replace('LCB3','LCB')
df['Main Position'] = df['Main Position'].replace('RCB3','RCB')
df['Main Position'] = df['Main Position'].replace('LCB5','LCB')
df['Main Position'] = df['Main Position'].replace('RCB5','RCB')
df['Main Position'] = df['Main Position'].replace('LB5','LB')
df['Main Position'] = df['Main Position'].replace('RB5','RB')
df.fillna(0,inplace=True)

#############################################################################################################################

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
    else:
        return df

dfProspect = df[(df['Minutes played'] >= mins) & (df['League'] == league)].copy()
dfProspect = filter_by_position(dfProspect, pos)

########## PROSPECT RESEARCH ##########
#######################################

# FORWARD
fwd1 = "Non-penalty goals per 90"
fwd2 = "npxG per 90"
fwd3 = "Assists per 90"
fwd4 = "xA per 90"
fwd5 = "Successful dribbles, %"
fwd6 = "Goal conversion, %"
fwd7 = "Shot assists per 90"
fwd8 = "Second assists per 90"
fwd9 = "Progressive runs per 90"
fwd10 = "Progressive passes per 90"
fwd11 = "Touches in box per 90"
fwd12 = "Aerial duels won, %"
# MIDFIELD
mid1 = "Accurate short / medium passes, %"
mid2 = "Accurate long passes, %"
mid3 = "Accurate smart passes, %"
mid4 = "Shot assists per 90"
mid5 = "xA per 90"
mid6 = "Assists per 90"
mid7 = "Second assists per 90"
mid8 = "Third assists per 90"
mid9 = "Progressive passes per 90"
mid10 = "Progressive runs per 90"
mid11 = "Duels won, %"
mid12 = "pAdj Tkl+Int per 90"
#DEFENDER
def1 = "Successful defensive actions per 90"
def2 = "PAdj Sliding tackles"
def3 = "Defensive duels won, %"
def4 = "Fouls per 90"
def5 = "Cards per 90"
def6 = "Shots blocked per 90"
def7 = "PAdj Interceptions"
def8 = "Aerial duels won, %"
def9 = "Accurate long passes, %"
def10 = "1st, 2nd, 3rd assists"
def11 = "Progressive passes per 90"
def12 = "Progressive runs per 90"
# #GOALKEEPER
# gk1 = "Conceded goals per 90"
# gk2 = "Prevented goals per 90"
# gk3 = "Shots against per 90"
# gk4 = "Save rate, %"
# gk5 = "Clean sheets, %"
# gk6 = "Exits per 90"
# gk7 = "Aerial duels per 90"
# gk8 = "Passes per 90"
# gk9 = "Accurate long passes, %"
# gk10 = "Average long pass length, m"
#EXTRA
extra = "Accurate passes, %"
extra2 = 'Shots per 90'
extra3 = 'Accurate crosses, %'
extra4 = 'Smart passes per 90'
extra5 = 'xA per Shot Assist'
extra6 = 'Accelerations per 90'
extra7 = 'Aerial duels won per 90'
extra8 = 'Fouls suffered per 90'
extra9 = 'npxG per shot'
extra10 = 'Crosses per 90'

ranked_columns = [
    'midpct1', 'midpct2', 'midpct3', 'midpct4', 'midpct5', 'midpct6', 'midpct7',
    'midpct8', 'midpct9', 'midpct10', 'midpct11', 'midpct12',
    'fwdpct1', 'fwdpct2', 'fwdpct3', 'fwdpct4', 'fwdpct5', 'fwdpct6', 'fwdpct7',
    'fwdpct8', 'fwdpct9', 'fwdpct10', 'fwdpct11', 'fwdpct12',
    'defpct1','defpct2','defpct3','defpct6','defpct7','defpct8','defpct9','defpct10','defpct11','defpct12',
    'extrapct','extrapct2','extrapct3','extrapct4','extrapct5','extrapct6','extrapct7','extrapct8','extrapct9','extrapct10',
]
inverse_ranked_columns = [
    'defpct4','defpct5'
]
ranked_columns_r = [
    mid1, mid2, mid3, mid4, mid5, mid6, mid7,
    mid8, mid9, mid10, mid11, mid12,
    fwd1, fwd2, fwd3, fwd4, fwd5, fwd6, fwd7,
    fwd8, fwd9, fwd10, fwd11, fwd12,
    def1,def2,def3,def6,def7,def8,def9,def10,def11,def12,
    extra,extra2,extra3,extra4,extra5,extra6,extra7,extra8,extra9,extra10,
]
inverse_ranked_columns_r = [
    def4,def5
]

dfProspect[ranked_columns] = 0.0
dfProspect[inverse_ranked_columns] = 0.0

for column, column_r in zip(ranked_columns, ranked_columns_r):
    dfProspect[column] = rank_column(dfProspect, column_r)
for column, column_r in zip(inverse_ranked_columns, inverse_ranked_columns_r):
    dfProspect[column] = rank_column_inverse(dfProspect, column_r)


final = dfProspect[['Player','Age','League','Position','Team within selected timeframe','Birth country',
'fwdpct1','fwdpct2','fwdpct5','fwdpct6','fwdpct11','midpct1','midpct3','midpct4','midpct5','midpct6','midpct7','midpct8','midpct9','midpct10','midpct11','midpct12','defpct1','defpct2','defpct3','defpct4','defpct5','defpct6','defpct7','defpct8','defpct9','defpct10',
#                     'gkpct1','gkpct2','gkpct3','gkpct4','gkpct5','gkpct6','gkpct7','gkpct8','gkpct10',
                    'extrapct','extrapct2','extrapct3','extrapct4','extrapct5','extrapct6','extrapct7','extrapct8','extrapct9','extrapct10',
]]

final.rename(columns={'fwdpct1': "Non-penalty goals per 90",
'fwdpct2': "npxG per 90",
'fwdpct5': "Successful dribbles, %",
'fwdpct6': "Goal conversion, %",
'fwdpct11': "Touches in box per 90",
'midpct1': "Accurate short / medium passes, %",
'midpct3': "Accurate smart passes, %",
'midpct4': "Shot assists per 90",
'midpct5': "xA per 90",
'midpct6': "Assists per 90",
'midpct7': "Second assists per 90",
'midpct8': "Third assists per 90",
'midpct9': "Progressive passes per 90",
'midpct10': "Progressive runs per 90",
'midpct11': "Duels won, %",
'midpct12': "pAdj Tkl+Int per 90",
'defpct1': "Successful defensive actions per 90",
'defpct2': "PAdj Sliding tackles",
'defpct3': "Defensive duels won, %",
'defpct4': "Fouls per 90",
'defpct5': "Cards per 90",
'defpct6': "Shots blocked per 90",
'defpct7': "PAdj Interceptions",
'defpct8': "Aerial duels won, %",
'defpct9': "Accurate long passes, %",
'defpct10': "1st, 2nd, 3rd assists",
# 'gkpct1': "Conceded goals per 90",
# 'gkpct2': "Prevented goals per 90",
# 'gkpct3': "Shots against per 90",
# 'gkpct4': "Save rate, %",
# 'gkpct5': "Clean sheets, %",
# 'gkpct6': "Exits per 90",
# 'gkpct7': "Aerial duels per 90",
# 'gkpct8': "Passes per 90",
# 'gkpct10': "Average long pass length, m",
'extrapct': "Accurate passes, %",
'extrapct2': "Shots per 90",
'extrapct3': "Accurate crosses, %",
'extrapct4': "Smart passes per 90",
'extrapct5': "xA per Shot Assist",
'extrapct6': "Accelerations per 90",
'extrapct7': "Aerial duels won per 90",
'extrapct8': "Fouls suffered per 90",
'extrapct9': "npxG per shot",
'extrapct10': "Crosses per 90",
'Team within selected timeframe': 'Team',
}, inplace=True)


final.Age = final.Age.astype(int)
final.sort_values(by=['Age'], inplace=True)
final = final[final['Age']<=maxage].reset_index(drop=True)
final.fillna(0,inplace=True)

##################################################################################################

with st.sidebar:
    st.header('Minimum Percentile Filters')
    def _update_slider(value):
        st.session_state["slider1"] = value
        st.session_state["slider2"] = value
        st.session_state["slider3"] = value
        st.session_state["slider4"] = value
        st.session_state["slider5"] = value
        st.session_state["slider6"] = value
        st.session_state["slider7"] = value
        st.session_state["slider8"] = value
        st.session_state["slider9"] = value
        st.session_state["slider10"] = value
        st.session_state["slider11"] = value
        st.session_state["slider12"] = value
        st.session_state["slider13"] = value
        st.session_state["slider14"] = value
        st.session_state["slider15"] = value
        st.session_state["slider16"] = value
        st.session_state["slider17"] = value
        st.session_state["slider18"] = value
        st.session_state["slider19"] = value
        st.session_state["slider20"] = value
        st.session_state["slider21"] = value
        st.session_state["slider22"] = value
        st.session_state["slider23"] = value
        st.session_state["slider24"] = value
        st.session_state["slider25"] = value
        st.session_state["slider26"] = value
        st.session_state["slider27"] = value
        st.session_state["slider28"] = value
        st.session_state["slider29"] = value
        st.session_state["slider30"] = value
        st.session_state["slider31"] = value
        st.session_state["slider32"] = value
        st.session_state["slider33"] = value

    st.button("Reset Sliders", on_click=_update_slider, kwargs={"value": 0.0})

    if ['slider1','slider2','slider3','slider4','slider5','slider6','slider7','slider8','slider9','slider10','slider11','slider12','slider13','slider14','slider15','slider16','slider17','slider18','slider19','slider20','slider21','slider22','slider23','slider24','slider25','slider26','slider27','slider28','slider29','slider30','slider31','slider32','slider33'] not in st.session_state:
        pass
    
    short = st.slider('Short & Medium Pass Cmp %', 0.0, 1.0, 0.0, key='slider1')
    long = st.slider('Long Pass Cmp %', 0.0, 1.0, 0.0, key='slider2')
    smartpct = st.slider('Smart Pass Cmp %', 0.0, 1.0, 0.0, key='slider3')
    smart = st.slider('Smart Passes per 90', 0.0, 1.0, 0.0, key='slider4')
    crosspct = st.slider('Cross Cmp %', 0.0, 1.0, 0.0, key='slider5')
    crosses = st.slider('Crosses per 90', 0.0, 1.0, 0.0, key='slider6')
    shotassist = st.slider('Shot Assists per 90', 0.0, 1.0, 0.0, key='slider7')
    xa = st.slider('xA per 90', 0.0, 1.0, 0.0, key='slider8')
    xasa = st.slider('xA per Shot Assist', 0.0, 1.0, 0.0, key='slider9')
    ast = st.slider('Assists per 90', 0.0, 1.0, 0.0, key='slider10')
    ast2 = st.slider('Second Assists per 90', 0.0, 1.0, 0.0, key='slider11')
    ast123 = st.slider('1st, 2nd, & 3rd Assists', 0.0, 1.0, 0.0, key='slider12')
    npxg = st.slider('npxG per 90', 0.0, 1.0, 0.0, key='slider13')
    npg = st.slider('Non-Pen Goals per 90', 0.0, 1.0, 0.0, key='slider14')
    gc = st.slider('Goals per Shot on Target', 0.0, 1.0, 0.0, key='slider15')
    npxgshot = st.slider('npxG per shot', 0.0, 1.0, 0.0, key='slider16')
    shots = st.slider('Shots per 90', 0.0, 1.0, 0.0, key='slider17')
    boxtouches = st.slider('Touches in Penalty Box per 90', 0.0, 1.0, 0.0, key='slider18')
    drib = st.slider('Dribble Success %', 0.0, 1.0, 0.0, key='slider19')
    accel = st.slider('Accelerations per 90', 0.0, 1.0, 0.0, key='slider20')
    progcarry = st.slider('Progressive Carries per 90', 0.0, 1.0, 0.0, key='slider21')
    progpass = st.slider('Progressive Passes per 90', 0.0, 1.0, 0.0, key='slider22')
    aerial = st.slider('Aerial Win %', 0.0, 1.0, 0.0, key='slider23')
    aerialswon = st.slider('Aerials Won per 90', 0.0, 1.0, 0.0, key='slider24')
    defduels = st.slider('Defensive Duels Success %', 0.0, 1.0, 0.0, key='slider25')
    defend = st.slider('Successful Defensive Actions per 90', 0.0, 1.0, 0.0, key='slider26')
    tklint = st.slider('Tackles & Interceptions per 90', 0.0, 1.0, 0.0, key='slider27')
    tkl = st.slider('Sliding Tackles per 90', 0.0, 1.0, 0.0, key='slider28')
    intercept = st.slider('Interceptions per 90', 0.0, 1.0, 0.0, key='slider29')
    shotblock = st.slider('Shots Blocked per 90', 0.0, 1.0, 0.0, key='slider30')
    foul = st.slider('Fouls Committed per 90', 0.0, 1.0, 0.0, key='slider31')
    fouldraw = st.slider('Fouls Drawn per 90', 0.0, 1.0, 0.0, key='slider32')
    cards = st.slider('Cards per 90', 0.0, 1.0, 0.0, key='slider33')



final = final[(final['Accurate short / medium passes, %']>=short) &
             (final['Accurate long passes, %']>=long) &
              (final['Smart passes per 90']>=smart) &
             (final['Accurate smart passes, %']>=smartpct) &
              (final['Crosses per 90']>=crosses) &
              (final['Accurate crosses, %']>=crosspct) &
              (final['Shot assists per 90']>=shotassist) &
              (final['xA per 90']>=xa) &
              (final['xA per Shot Assist']>=xasa) &
              (final['Assists per 90']>=ast) &
              (final['Second assists per 90']>=ast2) &
              (final['1st, 2nd, 3rd assists']>=ast123) &
              (final['npxG per 90']>=npxg) &
              (final['Non-penalty goals per 90']>=npg) &
              (final['Goal conversion, %']>=gc) &
              (final['npxG per shot']>=npxgshot) &
              (final['Shots per 90']>=shots) &
              (final['Touches in box per 90']>=boxtouches) &
              (final['Successful dribbles, %']>=drib) &
              (final['Accelerations per 90']>=accel) &
              (final['Progressive runs per 90']>=progcarry) &
              (final['Progressive passes per 90']>=progpass) &
              (final['Successful defensive actions per 90']>=defend) &
              (final['Defensive duels won, %']>=defduels) &
              (final['pAdj Tkl+Int per 90']>=tklint) &
              (final['PAdj Sliding tackles']>=tkl) &
              (final['PAdj Interceptions']>=intercept) &
              (final['Aerial duels won, %']>=aerial) &
              (final['Aerial duels won per 90']>=aerialswon) &
              (final['Shots blocked per 90']>=shotblock) &
              (final['Fouls per 90']>=foul) &
              (final['Fouls suffered per 90']>=fouldraw) &
              (final['Cards per 90']>=cards)
             ].reset_index(drop=True)

final


########################################################################################################
########################################################################################################
########################################################################################################
def scout_report(league, season, xtra, template, pos, player_pos, mins, minplay, compares, name, ws_name, team, age, sig, club_image, extra_text):
    plt.clf()
    df = read_csv('https://raw.githubusercontent.com/griffisben/Wyscout_Prospect_Research/main/WS_Data.csv')
    df = df.fillna(0)
    df = df[df['League']==league].reset_index(drop=True)
    df = df.dropna(subset=['Age', 'Position', 'Team within selected timeframe',]).reset_index(drop=True)
#         if league == 'Latvian Virsliga':
#             df.replace({'Valmiera / BSS': 'Valmiera',
#                        'Metta / LU': 'Metta'}, inplace=True)

    df['pAdj Tkl+Int per 90'] = df['PAdj Sliding tackles'] + df['PAdj Interceptions']
    df['1st, 2nd, 3rd assists'] = df['Assists per 90'] + df['Second assists per 90'] + df['Third assists per 90']
    df['xA per Shot Assist'] = df['xA per 90'] / df['Shot assists per 90']
    df['xA per Shot Assist'] = [0 if df['Shot assists per 90'][i]==0 else df['xA per 90'][i] / df['Shot assists per 90'][i] for i in range(len(df))]
    df['Aerial duels won per 90'] = df['Aerial duels per 90'] * (df['Aerial duels won, %']/100)
    df['Cards per 90'] = df['Yellow cards per 90'] + df['Red cards per 90']
    df['Clean sheets, %'] = df['Clean sheets'] / df['Matches played']
    df['npxG'] = df['xG'] - (.76 * df['Penalties taken'])
    df['npxG per 90'] = df['npxG'] / (df['Minutes played'] / 90)
    df['npxG per shot'] = df['npxG'] / (df['Shots'] - df['Penalties taken'])
    df['npxG per shot'] = [0 if df['Shots'][i]==0 else df['npxG'][i] / (df['Shots'][i] - df['Penalties taken'][i]) for i in range(len(df))]

    df['Main Position'] = df['Position'].str.split().str[0].str.rstrip(',')
    df['Main Position'] = df['Main Position'].replace('LAMF','LW')
    df['Main Position'] = df['Main Position'].replace('RAMF','RW')
    df['Main Position'] = df['Main Position'].replace('LCB3','LCB')
    df['Main Position'] = df['Main Position'].replace('RCB3','RCB')
    df['Main Position'] = df['Main Position'].replace('LCB5','LCB')
    df['Main Position'] = df['Main Position'].replace('RCB5','RCB')
    df['Main Position'] = df['Main Position'].replace('LB5','LB')
    df['Main Position'] = df['Main Position'].replace('RB5','RB')

    #####################################################################################
    # Filter data
    dfProspect = df[(df['Minutes played'] >= mins) & (df['League'] == league)].copy()
    dfProspect = filter_by_position(dfProspect, pos)
    raw_valsdf = dfProspect[(dfProspect['Player']==ws_name) & (dfProspect['Team within selected timeframe']==team) & (dfProspect['Age']==age)]

    # FORWARD
    fwd1 = "Non-penalty goals per 90"
    fwd2 = "npxG per 90"
    fwd3 = "Assists per 90"
    fwd4 = "xA per 90"
    fwd5 = "Successful dribbles, %"
    fwd6 = "Goal conversion, %"
    fwd7 = "Shot assists per 90"
    fwd8 = "Second assists per 90"
    fwd9 = "Progressive runs per 90"
    fwd10 = "Progressive passes per 90"
    fwd11 = "Touches in box per 90"
    fwd12 = "Aerial duels won, %"
    # MIDFIELD
    mid1 = "Accurate short / medium passes, %"
    mid2 = "Accurate long passes, %"
    mid3 = "Accurate smart passes, %"
    mid4 = "Shot assists per 90"
    mid5 = "xA per 90"
    mid6 = "Assists per 90"
    mid7 = "Second assists per 90"
    mid8 = "Third assists per 90"
    mid9 = "Progressive passes per 90"
    mid10 = "Progressive runs per 90"
    mid11 = "Duels won, %"
    mid12 = "pAdj Tkl+Int per 90"
    # DEFENDER
    def1 = "Successful defensive actions per 90"
    def2 = "PAdj Sliding tackles"
    def3 = "Defensive duels won, %"
    def4 = "Fouls per 90" 
    def5 = "Cards per 90"
    def6 = "Shots blocked per 90"
    def7 = "PAdj Interceptions"
    def8 = "Aerial duels won, %"
    def9 = "Accurate long passes, %"
    def10 = "1st, 2nd, 3rd assists"
    def11 = "Progressive passes per 90"
    def12 = "Progressive runs per 90"
    # GOALKEEPER
    gk1 = "Conceded goals per 90"
    gk2 = "Prevented goals per 90"
    gk3 = "Shots against per 90"
    gk4 = "Save rate, %"
    gk5 = "Clean sheets, %"
    gk6 = "Exits per 90"
    gk7 = "Aerial duels per 90"
    gk8 = "Passes per 90"
    gk9 = "Accurate long passes, %"
    gk10 = "Average long pass length, m"
    # OTHERS
    extra = "Accurate passes, %"
    extra2 = 'Shots per 90'
    extra3 = 'Accurate crosses, %'
    extra4 = 'Smart passes per 90'
    extra5 = 'xA per Shot Assist'
    extra6 = 'Accelerations per 90'
    extra7 = 'Aerial duels won per 90'
    extra8 = 'Fouls suffered per 90'
    extra9 = 'npxG per shot'
    extra10 = 'Crosses per 90'

    df_pros = dfProspect

    ranked_columns = [
        'midpct1', 'midpct2', 'midpct3', 'midpct4', 'midpct5', 'midpct6', 'midpct7',
        'midpct8', 'midpct9', 'midpct10', 'midpct11', 'midpct12',
        'fwdpct1', 'fwdpct2', 'fwdpct3', 'fwdpct4', 'fwdpct5', 'fwdpct6', 'fwdpct7',
        'fwdpct8', 'fwdpct9', 'fwdpct10', 'fwdpct11', 'fwdpct12',
        'defpct1','defpct2','defpct3','defpct6','defpct7','defpct8','defpct9','defpct10','defpct11','defpct12',
        'extrapct','extrapct2','extrapct3','extrapct4','extrapct5','extrapct6','extrapct7','extrapct8','extrapct9','extrapct10',
    ]
    inverse_ranked_columns = [
        'defpct4','defpct5'
    ]
    ranked_columns_r = [
        mid1, mid2, mid3, mid4, mid5, mid6, mid7,
        mid8, mid9, mid10, mid11, mid12,
        fwd1, fwd2, fwd3, fwd4, fwd5, fwd6, fwd7,
        fwd8, fwd9, fwd10, fwd11, fwd12,
        def1,def2,def3,def6,def7,def8,def9,def10,def11,def12,
        extra,extra2,extra3,extra4,extra5,extra6,extra7,extra8,extra9,extra10,
    ]
    inverse_ranked_columns_r = [
        def4,def5
    ]
    
    dfProspect[ranked_columns] = 0.0
    dfProspect[inverse_ranked_columns] = 0.0

    for column, column_r in zip(ranked_columns, ranked_columns_r):
        dfProspect[column] = rank_column(dfProspect, column_r)
    for column, column_r in zip(inverse_ranked_columns, inverse_ranked_columns_r):
        dfProspect[column] = rank_column_inverse(dfProspect, column_r)

    ######################################################################

    dfRadarMF = dfProspect[(dfProspect['Player']==ws_name) & (dfProspect['Team within selected timeframe']==team) & (dfProspect['Age']==age)].reset_index(drop=True)
    dfRadarMF = dfRadarMF.fillna(0)
    # Define a dictionary to map old column names to new ones
    column_mapping = {
        'attacking': {
            'midpct1': "Short & Med\nPass %",
            'midpct2': "Long\nPass %",
            'midpct3': "Smart\nPass %",
            'extrapct3': 'Cross\nCompletion %',
            'midpct4': "Shot\nAssists",
            'midpct5': "Expected\nAssists (xA)",
            'extrapct5': 'xA per\nShot Assist',
            'midpct6': "Assists",
            'midpct7': "Second\nAssists",
            'extrapct4': 'Smart\nPasses',
            'fwdpct2': "npxG",
            'fwdpct1': "Non-Pen\nGoals",
            'fwdpct6': "Goals/Shot\non Target %",
            'extrapct9': 'npxG\nper shot',
            'extrapct2': "Shots",
            'fwdpct11': 'Touches in\nPen Box',
            'fwdpct5': "Dribble\nSuccess %",
            'extrapct6': 'Acceleration\nwith Ball',
            'midpct10': "Prog.\nCarries",
            'midpct9': "Prog.\nPasses",
            'defpct1': "Defensive\nActions",
            'midpct12': "Tackles & Int\n(pAdj)",
            'defpct8': 'Aerial\nWin %'
        },
        'defensive': {
            'defpct1': 'Defensive\nActions',
            'defpct2': "Tackles\n(pAdj)",
            'defpct3': "Defensive\nDuels Won %",
            'defpct6': "Shot Blocks",
            'defpct7': "Interceptions\n(pAdj)",
            'extrapct7': 'Aerial Duels\nWon',
            'defpct8': "Aerial\nWin %",
            'defpct9': "Long\nPass %",
            'extrapct10': 'Crosses',
            'extrapct3': 'Cross\nCompletion %',
            'defpct10': "Assists &\n2nd/3rd Assists",
            'defpct11': "Prog.\nPasses",
            'defpct12': "Prog.\nCarries",
            'fwdpct5': "Dribble\nSucces %",
            'extrapct6': 'Acceleration\nwith Ball',
            'midpct5': "Expected\nAssists",
            'defpct4': "Fouls",
            'defpct5': "Cards",
            'extrapct8': 'Fouls Drawn'
        },
        'cb': {
            'defpct1': 'Defensive\nActions',
            'defpct2': "Tackles\n(pAdj)",
            'defpct3': "Defensive\nDuels Won %",
            'defpct6': "Shot Blocks",
            'defpct7': "Interceptions\n(pAdj)",
            'extrapct7': 'Aerial Duels\nWon',
            'defpct8': "Aerial\nWin %",
            'defpct9': "Long\nPass %",
            'defpct10': "Assists &\n2nd/3rd Assists",
            'defpct11': "Prog.\nPasses",
            'defpct12': "Prog.\nCarries",
            'fwdpct5': "Dribble\nSucces %",
            'extrapct6': 'Acceleration\nwith Ball',
            'midpct5': "Expected\nAssists",
            'defpct4': "Fouls",
            'defpct5': "Cards",
            'extrapct8': 'Fouls Drawn'
        }
    }
    if template == 'attacking':
        raw_vals = raw_valsdf[["Player",
                           mid1, mid2, mid3, extra3,
                           mid4,mid5,extra5, mid6, mid7,extra4,
                               fwd2,fwd1,fwd6,extra9,extra2,fwd11,
                           fwd5,extra6,mid10,mid9,
                               def1,mid12,def8
                          ]]
    if template == 'defensive':
        raw_vals = raw_valsdf[["Player",
                           def1, def2, def3, def6,def7,extra7,def8,
                           def9,extra10,extra3, def10, def11,def12,fwd5,extra6,mid5,
                           def4,def5,extra8,
                          ]]

    if template == 'cb':
        raw_vals = raw_valsdf[["Player",
                           def1, def2, def3, def6,def7,extra7,def8,
                           def9, def10, def11,def12,fwd5,extra6,mid5,
                           def4,def5,extra8,
                          ]]

    if template in column_mapping:
        selected_columns = column_mapping[template]
        dfRadarMF = dfRadarMF[['Player'] + list(selected_columns.keys())]
        dfRadarMF.rename(columns=selected_columns, inplace=True)
#         raw_vals = raw_valsdf[['Player'] + list(selected_columns.values())]



#         if template == 'gk':
#             dfRadarMF = dfRadarMF[["Player",
#                                    'gkpct1','gkpct2','gkpct3','gkpct4','gkpct5',
#                                    'gkpct6','gkpct7','gkpct8','gkpct9','gkpct10'
#                                   ]]
#             dfRadarMF.rename(columns={'gkpct1': 'Goals\nConceded',
#                                       'gkpct2': "Goals Prevented\nvs Expected",
#                                       'gkpct3': "Shots Against",
#                                       'gkpct4': "Save %",
#                                       'gkpct5': "Clean Sheet %",
#                                       'gkpct6': 'Att. Cross Claims\nor Punches',
#                                       'gkpct7': "Aerial Wins",
#                                       'gkpct8': "Passes",
#                                       'gkpct9': 'Long Passes',
#                                       'gkpct10': "Long\nPass %",
#                                      }, inplace=True)
#             print('Number of players comparing to:',len(dfProspect))

    ###########################################################################

    df1 = dfRadarMF.T.reset_index()

    df1.columns = df1.iloc[0] 

    df1 = df1[1:]
    df1 = df1.reset_index()
    df1 = df1.rename(columns={'Player': 'Metric',
                        ws_name: 'Value',
                             'index': 'Group'})

    if template == 'attacking':
        for i in range(len(df1)):
            if df1['Group'][i] <= 4:
                df1['Group'][i] = 'Passing'
            elif df1['Group'][i] <= 10:
                df1['Group'][i] = 'Creativity'
            elif df1['Group'][i] <= 16:
                df1['Group'][i] = 'Shooting'
            elif df1['Group'][i] <= 20:
                df1['Group'][i] = 'Ball Movement'
            elif df1['Group'][i] <= 23:
                df1['Group'][i] = 'Defense'

    if template == 'defensive':
        for i in range(len(df1)):
            if df1['Group'][i] <= 7:
                df1['Group'][i] = 'Defending'
            elif df1['Group'][i] <= 16:
                df1['Group'][i] = 'Attacking'
            elif df1['Group'][i] <= 19:
                df1['Group'][i] = 'Fouling'

    if template == 'cb':
        for i in range(len(df1)):
            if df1['Group'][i] <= 7:
                df1['Group'][i] = 'Defending'
            elif df1['Group'][i] <= 14:
                df1['Group'][i] = 'Attacking'
            elif df1['Group'][i] <= 17:
                df1['Group'][i] = 'Fouling'


    #####################################################################

    ### This link below is where I base a lot of my radar code off of
    ### https://www.python-graph-gallery.com/circular-barplot-with-groups

    def get_label_rotation(angle, offset):
        # Rotation must be specified in degrees :(
        rotation = np.rad2deg(angle + offset)+90
        if angle <= np.pi/2:
            alignment = "center"
            rotation = rotation + 180
        elif 4.3 < angle < np.pi*2:  # 4.71239 is 270 degrees
            alignment = "center"
            rotation = rotation - 180
        else: 
            alignment = "center"
        return rotation, alignment


    def add_labels(angles, values, labels, offset, ax):

        # This is the space between the end of the bar and the label
        padding = .05

        # Iterate over angles, values, and labels, to add all of them.
        for angle, value, label, in zip(angles, values, labels):
            angle = angle

            # Obtain text rotation and alignment
            rotation, alignment = get_label_rotation(angle, offset)

            # And finally add the text
            ax.text(
                x=angle, 
                y=1.05,
                s=label, 
                ha=alignment, 
                va="center", 
                rotation=rotation,
            )



    # Grab the group values
    GROUP = df1["Group"].values
    VALUES = df1["Value"].values
    LABELS = df1["Metric"].values
    OFFSET = np.pi / 2

    PAD = 2
    ANGLES_N = len(VALUES) + PAD * len(np.unique(GROUP))
    ANGLES = np.linspace(0, 2 * np.pi, num=ANGLES_N, endpoint=False)
    WIDTH = (2 * np.pi) / len(ANGLES)

    offset = 0
    IDXS = []

    template_group_sizes = {
        'attacking': [4, 6, 6, 4, 3],
        'defensive': [7, 9, 3],
        'cb': [7, 7, 3],
        'gk': [5, 5]
    }

    GROUPS_SIZE = template_group_sizes.get(template, [])



    for size in GROUPS_SIZE:
        IDXS += list(range(offset + PAD, offset + size + PAD))
        offset += size + PAD

    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={"projection": "polar"})
    ax.set_theta_offset(OFFSET)
    ax.set_ylim(-.5, 1)
    ax.set_frame_on(False)
    ax.xaxis.grid(False)
    ax.yaxis.grid(False)
    ax.set_xticks([])
    ax.set_yticks([])


    COLORS = [f"C{i}" for i, size in enumerate(GROUPS_SIZE) for _ in range(size)]

    ax.bar(
        ANGLES[IDXS], VALUES, width=WIDTH, color=COLORS,
        edgecolor="#4A2E19", linewidth=1
    )

    add_labels(ANGLES[IDXS], VALUES, LABELS, OFFSET, ax)

    offset = 0 
    for group, size in zip(GROUPS_SIZE, GROUPS_SIZE): #replace first GROUPS SIZE with ['Passing', 'Creativity'] etc if needed
        # Add line below bars
        x1 = np.linspace(ANGLES[offset + PAD], ANGLES[offset + size + PAD - 1], num=50)
        ax.plot(x1, [-.02] * 50, color="#4A2E19")


        # Add reference lines at 20, 40, 60, and 80
        x2 = np.linspace(ANGLES[offset], ANGLES[offset + PAD - 1], num=50)
        ax.plot(x2, [.2] * 50, color="#bebebe", lw=0.8)
        ax.plot(x2, [.4] * 50, color="#bebebe", lw=0.8)
        ax.plot(x2, [.60] * 50, color="#bebebe", lw=0.8)
        ax.plot(x2, [.80] * 50, color="#bebebe", lw=0.8)
        ax.plot(x2, [1] * 50, color="#bebebe", lw=0.8)

        offset += size + PAD

    if callout == 'Per 90':
        callout_text = "per 90'"
        for i, bar in enumerate(ax.patches):
            ax.annotate(f'{round(raw_vals.iloc[0][i+1],2)}',
                           (bar.get_x() + bar.get_width() / 2,
                            bar.get_height()-.1), ha='center', va='center',
                           size=10, xytext=(0, 8),
                           textcoords='offset points',
                       bbox=dict(boxstyle="round", fc='white', ec="black", lw=1))
    if callout == 'Percentile':
        callout_text = 'percentile'
        for bar in ax.patches:
            ax.annotate(format(bar.get_height()*100, '.0f'),
                           (bar.get_x() + bar.get_width() / 2,
                            bar.get_height()-.1), ha='center', va='center',
                           size=12, xytext=(0, 8),
                           textcoords='offset points',
                       bbox=dict(boxstyle="round", fc='white', ec="black", lw=1))


    PAD = 0.02
    ax.text(0.15, 0 + PAD, "0", size=10, color='#4A2E19')
    ax.text(0.15, 0.2 + PAD, "20", size=10, color='#4A2E19')
    ax.text(0.15, 0.4 + PAD, "40", size=10, color='#4A2E19')
    ax.text(0.15, 0.6 + PAD, "60", size=10, color='#4A2E19')
    ax.text(0.15, 0.8 + PAD, "80", size=10, color='#4A2E19')
    ax.text(0.15, 1 + PAD, "100", size=10, color='#4A2E19')

    plt.suptitle('%s (%i, %s, %i mins.), %s\n%s %s Percentile Rankings'
                 %(name, age, player_pos, minplay, team, season, league),
                 fontsize=17,
                 fontfamily="DejaVu Sans",
                color="#4A2E19", #4A2E19
                 fontweight="bold", fontname="DejaVu Sans",
                x=0.5,
                y=.97)

    plt.annotate(f"Bars are percentiles | Values shown are {callout_text} values\nAll values are per 90 minutes | %s\nCompared to %s %s, %i+ mins\nData: Wyscout | %s\nSample Size: %i players" %(extra_text, league, compares, mins, sig, len(dfProspect)),
                 xy = (0, -.075), xycoords='axes fraction',
                ha='left', va='center',
                fontsize=9, fontfamily="DejaVu Sans",
                color="#4A2E19", fontweight="regular", fontname="DejaVu Sans",
                ) 

    if club_image == 'y':
#         ######## Club Image ########
#         clubpath = f'https://raw.githubusercontent.com/griffisben/Wyscout_Prospect_Research/main/Club%20Images/{league.replace(" ","%20")}/{team.replace(" ","%20")}.png'
#         image = Image.open(urllib.request.urlopen(clubpath))
#         newax = fig.add_axes([.44,.43,0.15,0.15], anchor='C', zorder=1)
#         newax.imshow(image)
#         newax.axis('off')
        ######## Club Image ########
        clubpath = raw_valsdf['Team logo'].values[0]
        image = Image.open(urllib.request.urlopen(clubpath))
        newax = fig.add_axes([.44,.43,0.15,0.15], anchor='C', zorder=1)
        newax.imshow(image)
        newax.axis('off')

#         ######## League Logo Image ########
#         l_path = f'https://raw.githubusercontent.com/griffisben/Wyscout_Prospect_Research/main/Club%20Images/{league.replace(" ","%20")}/{league.replace(" ","%20")}%20Logo.png'
#         image = Image.open(urllib.request.urlopen(l_path))
#         newax = fig.add_axes([.76,.845,0.1,0.1], anchor='C', zorder=1)
#         newax.imshow(image)
#         newax.axis('off')

    ax.set_facecolor('#fbf9f4')
    fig = plt.gcf()
    fig.patch.set_facecolor('#fbf9f4')
#     ax.set_facecolor('#fbf9f4')
    fig.set_size_inches(12, (12*.9)) #length, height


    return fig
########################################################################################
########################################################################################
########################################################################################
########################################################################################
########################################################################################


df = read_csv('https://raw.githubusercontent.com/griffisben/Wyscout_Prospect_Research/main/WS_Data.csv')

st.header('Enter player name below to generate their radar (you can copy+paste from table above)')
player = st.text_input("Player's Radar to Generate", "")
page = st.number_input("Age of the player to generate (to guarantee the correct player)", step=1)

try:
    df = df[df['Minutes played']>=mins].reset_index(drop=True)
    df = df[df['League']==league].reset_index(drop=True)
    df1 = df[['Player', 'Team within selected timeframe', 'Position', 'Age', 'Minutes played']]
    df1 = df1.dropna(subset=['Age', 'Position', 'Team within selected timeframe',]).reset_index(drop=True)
    df1['Age'] = df1['Age'].astype(int)
    df1['Main Position'] = df1['Position'].str.split().str[0].str.rstrip(',')
    df1['Main Position'] = df1['Main Position'].replace('LAMF','LW')
    df1['Main Position'] = df1['Main Position'].replace('RAMF','RW')

    a = df1['Main Position'].unique()
    a = list(set(a))

    ws_pos = ['LAMF','LW','RB','LB','LCMF','DMF','RDMF','RWF','AMF','LCB','RWB','CF','LWB','GK','LDMF','RCMF','LWF','RW','RAMF','RCB','CB']
    #     pos = ['Wingers','Wingers','Fullbacks (FBs/WBs)','Fullbacks (FBs/WBs)','Central Midfielders (DM, CM, CAM)',
    #            'Central Midfielders no CAM (DM, CM)','Central Midfielders no CAM (DM, CM)',
    #            'Wingers','Central Midfielders no DM (CM, CAM)','Centre-Backs','Fullbacks (FBs/WBs)','Strikers','Fullbacks (FBs/WBs)','GK',
    #            'Central Midfielders no CAM (DM, CM)',
    #            'Central Midfielders (DM, CM, CAM)','Wingers','Wingers','Wingers','Centre-Backs','Centre-Backs']
    template = ['attacking','attacking','defensive','defensive','attacking','defensive','defensive','attacking','attacking','cb','defensive','attacking','defensive','gk','defensive','attacking','attacking','attacking','attacking','cb','cb']
    compares = ['Wingers','Wingers','Fullbacks','Fullbacks','Central Midfielders','Central & Defensive Mids','Central & Defensive Mids','Wingers','Central & Attacking Mids','Center Backs','Fullbacks','Strikers','Fullbacks','Goalkeepers','Central & Defensive Mids','Central Midfielders','Wingers','Wingers','Wingers','Center Backs','Center Backs']

    gen = df1[(df1['Player']==player) & (df1['Age']==page)]
    ix = ws_pos.index(gen['Main Position'].values[0])
    minplay = int(gen['Minutes played'].values[0])

    ##########################################################################################


    #######################################################################################################
    #######################################################################################################
    #######################################################################################################
    #######################################################################################################
    ssn_ = lg_lookup[lg_lookup['League']==league].Season.values[0]
    xtratext = lg_lookup[lg_lookup['League']==league].Date.values[0]

    radar_img = scout_report(
                 league = league,  ######
                 season = ssn_,  
                 xtra = ' current',  ######
                 template = template[ix],
    #                  pos_buckets = pos_buckets[ix],
    #                  pos = pos[ix],
                pos = pos,
                 player_pos = ws_pos[ix],
                 compares = compares[ix],
                 mins = mins,
                minplay=minplay,
                 name = gen['Player'].values[0],
                 ws_name = gen['Player'].values[0],
                 team = gen['Team within selected timeframe'].values[0],
                 age = gen['Age'].values[0],
                 sig = 'Twitter: @BeGriffis',
                 club_image = 'y',
                 extra_text = xtratext,
                )
    st.pyplot(radar_img.figure)
except:
    st.text("Please enter a valid name & age.  \nPlease check spelling as well as the position filters that they include your player's position.")
    
    
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
    
