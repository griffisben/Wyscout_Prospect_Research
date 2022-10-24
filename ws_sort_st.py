import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats
from statistics import mean
from math import pi
import streamlit as st
sns.set_style("white")

st.title('Prospect Research')
st.header('All data from Wyscout')
st.header('Created by Ben Griffis (@BeGriffis')

##################################################################

df = pd.read_csv('https://raw.githubusercontent.com/griffisben/Wyscout_Prospect_Research/main/Japan_Korea_2022_WS.csv')

with st.sidebar:
    st.header('Choose Basic Options')
    mins = st.slider('Minimum Minutes Played', 0, max(df['Minutes played'].astype(int)), 500)
    maxage = st.slider('Max Age', 17, 50, 25)
    pos = st.selectbox('Positions', ('Strikers', 'Strikers and Wingers', 'Forwards (AM, W, CF)',
                                    'Forwards no ST (AM, W)', 'Wingers', 'Central Midfielders (DM, CM, CAM)',
                                    'Central Midfielders no CAM (DM, CM)', 'Fullbacks (FBs/WBs)',
                                    'Defenders (CB, FB/WB, DM)', 'Centre-Backs'))
    league = st.selectbox('League', ('J1', 'J2', 'J3', 'K League 1', 'K League 2'))

#####################################################################

############################################################################
df = pd.read_csv('https://raw.githubusercontent.com/griffisben/Wyscout_Prospect_Research/main/Japan_Korea_2022_WS.csv')

df['pAdj Tkl+Int per 90'] = df['PAdj Sliding tackles'] + df['PAdj Interceptions']
df['1st, 2nd, 3rd assists'] = df['Assists per 90'] + df['Second assists per 90'] + df['Third assists per 90']
df['xA per Shot Assist'] = df['xA per 90'] / df['Shot assists per 90']
df['Aerial duels won per 90'] = df['Aerial duels per 90'] * (df['Aerial duels won, %']/100)
df['Cards per 90'] = df['Yellow cards per 90'] + df['Red cards per 90']
df['Clean sheets, %'] = df['Clean sheets'] / df['Matches played']
df['npxG'] = df['xG'] - (.76 * df['Penalties taken'])
df['npxG per 90'] = df['npxG'] / (df['Minutes played'] / 90)
df['npxG per shot'] = df['npxG'] / (df['Shots'] - df['Penalties taken'])

df = df.dropna(subset=['Position', 'Age']).reset_index(drop=True)


df['Main Position'] = ''
for i in range(len(df)):
    df['Main Position'][i] = df['Position'][i].split()[0]

#############################################################################################################################

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
if pos == 'Fullbacks (FBs/WBs)':
    dfProspect = dfProspect[(dfProspect['Main Position'].str.contains('LB')) |
                           (dfProspect['Main Position'].str.contains('RB')) |
                           (dfProspect['Main Position'].str.contains('WB'))]
if pos == 'Defenders (CB, FB/WB, DM)':
    dfProspect = dfProspect[(dfProspect['Main Position'].str.contains('LB')) |
                           (dfProspect['Main Position'].str.contains('RB')) |
                           (dfProspect['Main Position'].str.contains('WB')) |
                           (dfProspect['Main Position'].str.contains('CB')) |
                           (dfProspect['Main Position'].str.contains('DMF'))]
if pos == 'Centre-Backs':
    dfProspect = dfProspect[(dfProspect['Main Position'].str.contains('CB'))]
if pos == 'Strikers':
    dfProspect = dfProspect[(dfProspect['Main Position'].str.contains('CF'))]


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

df_pros = dfProspect

dfProspect["midpct1"] = stats.rankdata(dfProspect[mid1], "average")/len(dfProspect[mid1])
dfProspect["midpct2"] = stats.rankdata(dfProspect[mid2], "average")/len(dfProspect[mid2])
dfProspect["midpct3"] = stats.rankdata(dfProspect[mid3], "average")/len(dfProspect[mid3])
dfProspect["midpct4"] = stats.rankdata(dfProspect[mid4], "average")/len(dfProspect[mid4])
dfProspect["midpct5"] = stats.rankdata(dfProspect[mid5], "average")/len(dfProspect[mid5])
dfProspect["midpct6"] = stats.rankdata(dfProspect[mid6], "average")/len(dfProspect[mid6])
dfProspect["midpct7"] = stats.rankdata(dfProspect[mid7], "average")/len(dfProspect[mid7])
dfProspect["midpct8"] = stats.rankdata(dfProspect[mid8], "average")/len(dfProspect[mid8])
dfProspect["midpct9"] = stats.rankdata(dfProspect[mid9], "average")/len(dfProspect[mid9])
dfProspect["midpct10"] = stats.rankdata(dfProspect[mid10], "average")/len(dfProspect[mid10])
dfProspect["midpct11"] = stats.rankdata(dfProspect[mid11], "average")/len(dfProspect[mid11])
dfProspect["midpct12"] = stats.rankdata(dfProspect[mid12], "average")/len(dfProspect[mid12])
dfProspect["fwdpct1"] = stats.rankdata(dfProspect[fwd1], "average")/len(dfProspect[fwd1])
dfProspect["fwdpct2"] = stats.rankdata(dfProspect[fwd2], "average")/len(dfProspect[fwd2])
dfProspect["fwdpct3"] = stats.rankdata(dfProspect[fwd3], "average")/len(dfProspect[fwd3])
dfProspect["fwdpct4"] = stats.rankdata(dfProspect[fwd4], "average")/len(dfProspect[fwd4])
dfProspect["fwdpct5"] = stats.rankdata(dfProspect[fwd5], "average")/len(dfProspect[fwd5])
dfProspect["fwdpct6"] = stats.rankdata(dfProspect[fwd6], "average")/len(dfProspect[fwd6])
dfProspect["fwdpct7"] = stats.rankdata(dfProspect[fwd7], "average")/len(dfProspect[fwd7])
dfProspect["fwdpct8"] = stats.rankdata(dfProspect[fwd8], "average")/len(dfProspect[fwd8])
dfProspect["fwdpct9"] = stats.rankdata(dfProspect[fwd9], "average")/len(dfProspect[fwd9])
dfProspect["fwdpct10"] = stats.rankdata(dfProspect[fwd10], "average")/len(dfProspect[fwd10])
dfProspect["fwdpct11"] = stats.rankdata(dfProspect[fwd11], "average")/len(dfProspect[fwd11])
dfProspect["fwdpct12"] = stats.rankdata(dfProspect[fwd12], "average")/len(dfProspect[fwd12])
dfProspect["defpct1"] = stats.rankdata(dfProspect[def1], "average")/len(dfProspect[def1])
dfProspect["defpct2"] = stats.rankdata(dfProspect[def2], "average")/len(dfProspect[def2])
dfProspect["defpct3"] = stats.rankdata(dfProspect[def3], "average")/len(dfProspect[def3])
dfProspect["defpct4"] = 1-stats.rankdata(dfProspect[def4], "average")/len(dfProspect[def4])
dfProspect["defpct5"] = 1-stats.rankdata(dfProspect[def5], "average")/len(dfProspect[def5])
dfProspect["defpct6"] = stats.rankdata(dfProspect[def6], "average")/len(dfProspect[def6])
dfProspect["defpct7"] = stats.rankdata(dfProspect[def7], "average")/len(dfProspect[def7])
dfProspect["defpct8"] = stats.rankdata(dfProspect[def8], "average")/len(dfProspect[def8])
dfProspect["defpct9"] = stats.rankdata(dfProspect[def9], "average")/len(dfProspect[def9])
dfProspect["defpct10"] = stats.rankdata(dfProspect[def10], "average")/len(dfProspect[def10])
dfProspect["defpct11"] = stats.rankdata(dfProspect[def11], "average")/len(dfProspect[def11])
dfProspect["defpct12"] = stats.rankdata(dfProspect[def12], "average")/len(dfProspect[def12])
dfProspect["gkpct1"] = 1-stats.rankdata(dfProspect[gk1], "average")/len(dfProspect[gk1])
dfProspect["gkpct2"] = stats.rankdata(dfProspect[gk2], "average")/len(dfProspect[gk2])
dfProspect["gkpct3"] = stats.rankdata(dfProspect[gk3], "average")/len(dfProspect[gk3])
dfProspect["gkpct4"] = stats.rankdata(dfProspect[gk4], "average")/len(dfProspect[gk4])
dfProspect["gkpct5"] = stats.rankdata(dfProspect[gk5], "average")/len(dfProspect[gk5])
dfProspect["gkpct6"] = stats.rankdata(dfProspect[gk6], "average")/len(dfProspect[gk6])
dfProspect["gkpct7"] = stats.rankdata(dfProspect[gk7], "average")/len(dfProspect[gk7])
dfProspect["gkpct8"] = stats.rankdata(dfProspect[gk8], "average")/len(dfProspect[gk8])
dfProspect["gkpct9"] = stats.rankdata(dfProspect[gk9], "average")/len(dfProspect[gk9])
dfProspect["gkpct10"] = stats.rankdata(dfProspect[gk10], "average")/len(dfProspect[gk10])
dfProspect["extrapct"] = stats.rankdata(dfProspect[extra], "average")/len(dfProspect[extra])
dfProspect["extrapct2"] = stats.rankdata(dfProspect[extra2], "average")/len(dfProspect[extra2])
dfProspect["extrapct3"] = stats.rankdata(dfProspect[extra3], "average")/len(dfProspect[extra3])
dfProspect["extrapct4"] = stats.rankdata(dfProspect[extra4], "average")/len(dfProspect[extra4])
dfProspect["extrapct5"] = stats.rankdata(dfProspect[extra5], "average")/len(dfProspect[extra5])
dfProspect["extrapct6"] = stats.rankdata(dfProspect[extra6], "average")/len(dfProspect[extra6])
dfProspect["extrapct7"] = stats.rankdata(dfProspect[extra7], "average")/len(dfProspect[extra7])
dfProspect["extrapct8"] = stats.rankdata(dfProspect[extra8], "average")/len(dfProspect[extra8])
dfProspect["extrapct9"] = stats.rankdata(dfProspect[extra9], "average")/len(dfProspect[extra9])
dfProspect["extrapct10"] = stats.rankdata(dfProspect[extra10], "average")/len(dfProspect[extra10])

final = dfProspect[['Player','Age','League','Position','Team within selected timeframe','Birth country', 'Contract expires',
'fwdpct1','fwdpct2','fwdpct5','fwdpct6','fwdpct11','midpct1','midpct3','midpct4','midpct5','midpct6','midpct7','midpct8','midpct9','midpct10','midpct11','midpct12','defpct1','defpct2','defpct3','defpct4','defpct5','defpct6','defpct7','defpct8','defpct9','defpct10','gkpct1','gkpct2','gkpct3','gkpct4','gkpct5','gkpct6','gkpct7','gkpct8','gkpct10','extrapct','extrapct2','extrapct3','extrapct4','extrapct5','extrapct6','extrapct7','extrapct8','extrapct9','extrapct10',
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
'gkpct1': "Conceded goals per 90",
'gkpct2': "Prevented goals per 90",
'gkpct3': "Shots against per 90",
'gkpct4': "Save rate, %",
'gkpct5': "Clean sheets, %",
'gkpct6': "Exits per 90",
'gkpct7': "Aerial duels per 90",
'gkpct8': "Passes per 90",
'gkpct10': "Average long pass length, m",
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

##################################################################################################

with st.sidebar:
    st.header('Minimum Percentile Filters')
    npg = st.slider('Non-penalty goals per 90 ', 0.0, 1.0, 0.5)
    npxg = st.slider('npxG per 90 ', 0.0, 1.0, 0.5)
    drib = st.slider('Successful dribbles, % ', 0.0, 1.0, 0.5)
    gc = st.slider('Goal conversion, % ', 0.0, 1.0, 0.5)
    boxtouch = st.slider('Touches in box per 90 ', 0.0, 1.0, 0.5)



final = final[(final['Non-penalty goals per 90']>=npg) &
             (final['npxG per 90']>=npxg) &
             (final['Successful dribbles, %']>=drib) &
              (final['Goal conversion, %']>=gc) &
              (final['Touches in box per 90']>=boxtouch)
             ].reset_index(drop=True)
final
