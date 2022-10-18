#Name: Jason Woodson
#Date: 1/17/2021
#Purpose: Looking at each team's distribution of shot's based on when it was taken in the 24 second shot clock and each team's EFG% for that interval


#import applicable modules
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import date
from nba_api.stats.endpoints._base import Endpoint
from nba_api.stats.library.http import NBAStatsHTTP
from nba_api.stats.library.parameters import LeagueID, PerModeSimple, Season, SeasonTypeAllStar, ConferenceNullable, DivisionNullable, GameSegmentNullable, LastNGamesNullable, LocationNullable, MonthNullable, OutcomeNullable, PeriodNullable, SeasonSegmentNullable, ShotClockRangeNullable

#using NBA stats endpoint, scrape shot clock data from NBA.com
class LeagueDashTeamPtShot(Endpoint):
    endpoint = 'leaguedashteamptshot'
    expected_data = {'LeagueDashPTShots': ['TEAM_ID', 'TEAM_NAME', 'TEAM_ABBREVIATION', 'GP', 'G', 'FGA_FREQUENCY', 'FGM', 'FGA', 'FG_PCT', 'EFG_PCT', 'FG2A_FREQUENCY', 'FG2M', 'FG2A', 'FG2_PCT', 'FG3A_FREQUENCY', 'FG3M', 'FG3A', 'FG3_PCT']}

    nba_response = None
    data_sets = None
    player_stats = None
    team_stats = None
    headers = None

    def __init__(self,
                 league_id=LeagueID.default,
                 per_mode_simple=PerModeSimple.default,
                 season=Season.default,
                 season_type_all_star=SeasonTypeAllStar.default,
                 close_def_dist_range_nullable='',
                 conference_nullable=ConferenceNullable.default,
                 date_from_nullable='',
                 date_to_nullable='',
                 division_nullable=DivisionNullable.default,
                 dribble_range_nullable='',
                 game_segment_nullable=GameSegmentNullable.default,
                 general_range_nullable='',
                 last_n_games_nullable=LastNGamesNullable.default,
                 location_nullable=LocationNullable.default,
                 month_nullable=MonthNullable.default,
                 opponent_team_id_nullable='',
                 outcome_nullable=OutcomeNullable.default,
                 po_round_nullable='',
                 period_nullable=PeriodNullable.default,
                 season_segment_nullable=SeasonSegmentNullable.default,
                 shot_clock_range_nullable=ShotClockRangeNullable.default,
                 shot_dist_range_nullable='',
                 team_id_nullable='',
                 touch_time_range_nullable='',
                 vs_conference_nullable=ConferenceNullable.default,
                 vs_division_nullable=DivisionNullable.default,
                 proxy=None,
                 headers=None,
                 timeout=30,
                 get_request=True):
        self.proxy = proxy
        if headers is not None:
            self.headers = headers
        self.timeout = timeout
        self.parameters = {
                'LeagueID': league_id,
                'PerMode': per_mode_simple,
                'Season': season,
                'SeasonType': season_type_all_star,
                'CloseDefDistRange': close_def_dist_range_nullable,
                'Conference': conference_nullable,
                'DateFrom': date_from_nullable,
                'DateTo': date_to_nullable,
                'Division': division_nullable,
                'DribbleRange': dribble_range_nullable,
                'GameSegment': game_segment_nullable,
                'GeneralRange': general_range_nullable,
                'LastNGames': last_n_games_nullable,
                'Location': location_nullable,
                'Month': month_nullable,
                'OpponentTeamID': opponent_team_id_nullable,
                'Outcome': outcome_nullable,
                'PORound': po_round_nullable,
                'Period': period_nullable,
                'SeasonSegment': season_segment_nullable,
                'ShotClockRange': shot_clock_range_nullable,
                'ShotDistRange': shot_dist_range_nullable,
                'TeamID': team_id_nullable,
                'TouchTimeRange': touch_time_range_nullable,
                'VsConference': vs_conference_nullable,
                'VsDivision': vs_division_nullable
        }
        if get_request:
            self.get_request()
    
    def get_request(self):
        self.nba_response = NBAStatsHTTP().send_api_request(
            endpoint=self.endpoint,
            parameters=self.parameters,
            proxy=self.proxy,
            headers=self.headers,
            timeout=self.timeout,
        )
        self.load_response()
        
    def load_response(self):
        data_sets = self.nba_response.get_data_sets()
        self.data_sets = [Endpoint.DataSet(data=data_set) for data_set_name, data_set in data_sets.items()]
        self.league_dash_ptshots = Endpoint.DataSet(data=data_sets['LeagueDashPTShots'])

#save the results for each shot clock range to a df
print('Scraping data from NBA.com....')
Super_Early = LeagueDashTeamPtShot(shot_clock_range_nullable='24-22').get_data_frames()[0]
Very_Early = LeagueDashTeamPtShot(shot_clock_range_nullable='22-18 Very Early').get_data_frames()[0]
Early = LeagueDashTeamPtShot(shot_clock_range_nullable='18-15 Early').get_data_frames()[0]
Average = LeagueDashTeamPtShot(shot_clock_range_nullable='15-7 Average').get_data_frames()[0]
Late = LeagueDashTeamPtShot(shot_clock_range_nullable='7-4 Late').get_data_frames()[0]
Very_Late = LeagueDashTeamPtShot(shot_clock_range_nullable='4-0 Very Late').get_data_frames()[0]
print('Data retrieved successfully!')

#add a column to each df describing which range it corresponds to
Super_Early['GROUP'] = 'Super Early'
Very_Early['GROUP'] = 'Very Early'
Early['GROUP'] = 'Early'
Average['GROUP'] = 'Average'
Late['GROUP'] = 'Late'
Very_Late['GROUP'] = 'Very Late'

#combine the df's and group by team and shot clock time
Shot_Clock = pd.concat([Super_Early,Very_Early,Early,Average,Late,Very_Late])
Shot_Clock = Shot_Clock.groupby(['TEAM_NAME','GROUP'],as_index=False).mean()

#break out each df for each group
SE = Shot_Clock[Shot_Clock['GROUP']=='Super Early']
VE = Shot_Clock[Shot_Clock['GROUP']=='Very Early']
E = Shot_Clock[Shot_Clock['GROUP']=='Early']
A = Shot_Clock[Shot_Clock['GROUP']=='Average']
L = Shot_Clock[Shot_Clock['GROUP']=='Late']
VL = Shot_Clock[Shot_Clock['GROUP']=='Very Late']

#plot the distribution of each team's percentage of shots based on the shot clock time
f, ax = plt.subplots(figsize=(20,10))

plt.barh(y="TEAM_NAME",width='FGA_FREQUENCY', data=SE,
            label="Super Early (24-22)", color="rosybrown")

plt.barh(y="TEAM_NAME",width='FGA_FREQUENCY', data=VE,
            label="Very Early (22-18)", color="lightcoral",left=
         np.array(SE['FGA_FREQUENCY']))

plt.barh(y="TEAM_NAME",width='FGA_FREQUENCY', data=E,
            label="Early (18-15)", color="indianred",left=
         (np.array(VE['FGA_FREQUENCY']) + np.array(SE['FGA_FREQUENCY'])))

plt.barh(y="TEAM_NAME",width='FGA_FREQUENCY', data=A,
            label="Average (15-7)", color="firebrick",left=
         (np.array(VE['FGA_FREQUENCY']) + np.array(SE['FGA_FREQUENCY'])+ np.array(E['FGA_FREQUENCY'])))


plt.barh(y="TEAM_NAME",width='FGA_FREQUENCY', data=L,
            label="Late (7-4)", color="red",left=
         (np.array(VE['FGA_FREQUENCY']) + np.array(SE['FGA_FREQUENCY'])+ np.array(E['FGA_FREQUENCY'])+np.array(A['FGA_FREQUENCY'])))


plt.barh(y="TEAM_NAME",width='FGA_FREQUENCY', data=VL,
            label="Very Late (4-0)", color="darkred",left=
         (np.array(VE['FGA_FREQUENCY']) + np.array(SE['FGA_FREQUENCY'])+ np.array(E['FGA_FREQUENCY'])+np.array(A['FGA_FREQUENCY'])+np.array(L['FGA_FREQUENCY'])))

ax.legend(ncol=1, loc="right", frameon=True)
ax.set(xlim=(0,1.2), ylabel="",
       xlabel="Percentage of Team's Field Goal Attempts")

plt.savefig('Shot Clock Distribution ' + str(date.today()) + '.jpg')
print('Graphic saved successfully!')

#combine the df's and group by team and shot clock time
Shot_Clock_H = pd.concat([Super_Early,Very_Early,Early,Average,Late,Very_Late])
Shot_Clock_H = Shot_Clock_H.groupby(['TEAM_NAME','GROUP'],as_index=False).mean()

#make a pivot table of each team's efg% based on the shot clock time
Shot_Clock_H = Shot_Clock_H.pivot('TEAM_NAME','GROUP','EFG_PCT')

#create the order of columns
column_order = ['Super Early','Very Early','Early','Average','Late','Very Late']

#reindex the pivot table based on column order
Shot_Clock_H = Shot_Clock_H.reindex(column_order, axis=1)

#plot the heat map of efg% for each team and each shot clock time
plt.figure(figsize = (20,12))

cmap = sns.diverging_palette(10, 133, as_cmap=True)

sns.heatmap(Shot_Clock_H,cbar_kws={'label': 'Effective Field Goal Percentage'},cmap=cmap)

plt.ylabel("")
plt.xlabel("Shot Clock Time")

plt.savefig('Shot Clock Heat Map ' + str(date.today()) + '.jpg')
print('Heat map saved successfully!')


