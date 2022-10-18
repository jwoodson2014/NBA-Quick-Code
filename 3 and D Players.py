#Name: Jason Woodson
#Date: 12/27/2021
#Purpose: Plotting the 3P% against DFG DIFF% for players between 6'4-6'9 who have a spot up rate that is in the 25th percentile or higher and have played in a total number of games that is in the 25th percentile or higher



#import applicable modules
import pandas as pd
import numpy as np
import requests
import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.cbook import get_sample_data
from PIL import Image, ImageChops
from datetime import date
from io import BytesIO
from nba_api.stats.endpoints._base import Endpoint
from nba_api.stats.library.http import NBAStatsHTTP
from nba_api.stats.library.parameters import LeagueID, Season, LeagueIDNullable, PlayTypeNullable, TypeGroupingNullable, PerModeSimple, PlayerOrTeamAbbreviation, SeasonTypeAllStar
from nba_api.stats.library.parameters import LastNGames, MeasureTypeDetailedDefense, Month, PaceAdjust, PerModeDetailed, Period, PlusMinus, Rank, Season, SeasonTypeAllStar, ConferenceNullable, DivisionSimpleNullable, GameScopeSimpleNullable, GameSegmentNullable, LeagueIDNullable, LocationNullable, OutcomeNullable, PlayerExperienceNullable, PlayerPositionAbbreviationNullable, SeasonSegmentNullable, ShotClockRangeNullable, StarterBenchNullable, DivisionNullable
from nba_api.stats.library.parameters import DefenseCategory, LeagueID, PerModeSimple, Season, SeasonTypeAllStar, ConferenceNullable, DivisionNullable, GameSegmentNullable, LastNGamesNullable, LocationNullable, MonthNullable, OutcomeNullable, PeriodNullable, PlayerExperienceNullable, PlayerPositionNullable, SeasonSegmentNullable, StarterBenchNullable
from nba_api.stats.library.parameters import LeagueID, PerModeSimple, PlayerOrTeamAbbreviation, SeasonTypeAllStar, Season, PlayTypeNullable, TypeGroupingNullable




#scrape information from nba.com for general info on all NBA players both current and past(Team, Height, Age, etc.)
url = 'https://stats.nba.com/stats/playerindex?College=&Country=&DraftPick=&DraftRound=&DraftYear=&Height=&Historical=1&LeagueID=00&Season=2021-22&SeasonType=Regular%20Season&TeamID=0&Weight='
header_dict = {
'Accept': '*/*',
'Accept-Encoding': 'gzip, deflate, br',
'Accept-Language': 'en-US,en;q=0.9',
'Connection': 'keep-alive',
'Host': 'stats.nba.com',
'Origin': 'https://www.nba.com',
'Referer': 'https://www.nba.com/',
'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
'sec-ch-ua-mobile': '?0',
'sec-ch-ua-platform': '"Windows"',
'Sec-Fetch-Dest': 'empty',
'Sec-Fetch-Mode': 'cors',
'Sec-Fetch-Site': 'same-site',
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
}

print('Getting information on all NBA players.....')
res = requests.get(url, headers=header_dict)
json_set = res.json()
headers = json_set['resultSets'][0]['headers']
data_set = json_set['resultSets'][0]['rowSet']
All_Player_Info = pd.DataFrame(data_set, columns=headers)
print('Information retreived successfully!')


#filter the information for players that play in the current season
All_Player_Info = All_Player_Info[All_Player_Info['TO_YEAR']=='2021'].reset_index(drop=True)


#create a list of player heights for which we want to include in our analysis
Player_Heights = ['6-4','6-5','6-6','6-7','6-8','6-9']
Get_Heights = All_Player_Info['HEIGHT'].isin(Player_Heights)


#filter the df for players matching those heights
All_Player_Info = All_Player_Info[Get_Heights]


#Using the nba_api, get information regarding spot up shooting rates for the current season
class SynergyPlayTypes(Endpoint):
    endpoint = 'synergyplaytypes'
    expected_data = {'SynergyPlayType': ['SEASON_ID', 'TEAM_ID', 'TEAM_ABBREVIATION', 'TEAM_NAME', 'PLAY_TYPE', 'TYPE_GROUPING', 'PERCENTILE', 'GP', 'POSS_PCT', 'PPP', 'FG_PCT', 'FT_POSS_PCT', 'TOV_POSS_PCT', 'SF_POSS_PCT', 'PLUSONE_POSS_PCT', 'SCORE_POSS_PCT', 'EFG_PCT', 'POSS', 'PTS', 'FGM', 'FGA', 'FGMX']}

    nba_response = None
    data_sets = None
    player_stats = None
    team_stats = None
    headers = None

    def __init__(self,
                 league_id=LeagueID.default,
                 per_mode_simple='Totals',
                 player_or_team_abbreviation='P',
                 season_type_all_star=SeasonTypeAllStar.default,
                 season=Season.default,
                 play_type_nullable='Spotup',
                 type_grouping_nullable='offensive',
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
                'PlayerOrTeam': player_or_team_abbreviation,
                'SeasonType': season_type_all_star,
                'SeasonYear': season,
                'PlayType': play_type_nullable,
                'TypeGrouping': type_grouping_nullable
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
        self.synergy_play_type = Endpoint.DataSet(data=data_sets['SynergyPlayType'])




print('Getting play type information.....')
Spot_Up_Rate = SynergyPlayTypes().get_data_frames()[0]
column_map = {'PLAYER_ID':'PERSON_ID'}
Spot_Up_Rate = Spot_Up_Rate.rename(columns=column_map)
print('Information retreived successfully!')


#Using the nba_api, get information regarding traditional stats for the current season
class LeagueDashPlayerStats(Endpoint):
    endpoint = 'leaguedashplayerstats'
    expected_data = {'LeagueDashPlayerStats': ['PLAYER_ID', 'PLAYER_NAME', 'TEAM_ID', 'TEAM_ABBREVIATION', 'AGE', 'GP', 'W', 'L', 'W_PCT', 'MIN', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA', 'FT_PCT', 'OREB', 'DREB', 'REB', 'AST', 'TOV', 'STL', 'BLK', 'BLKA', 'PF', 'PFD', 'PTS', 'PLUS_MINUS', 'NBA_FANTASY_PTS', 'DD2', 'TD3', 'GP_RANK', 'W_RANK', 'L_RANK', 'W_PCT_RANK', 'MIN_RANK', 'FGM_RANK', 'FGA_RANK', 'FG_PCT_RANK', 'FG3M_RANK', 'FG3A_RANK', 'FG3_PCT_RANK', 'FTM_RANK', 'FTA_RANK', 'FT_PCT_RANK', 'OREB_RANK', 'DREB_RANK', 'REB_RANK', 'AST_RANK', 'TOV_RANK', 'STL_RANK', 'BLK_RANK', 'BLKA_RANK', 'PF_RANK', 'PFD_RANK', 'PTS_RANK', 'PLUS_MINUS_RANK', 'NBA_FANTASY_PTS_RANK', 'DD2_RANK', 'TD3_RANK', 'CFID', 'CFPARAMS']}

    nba_response = None
    data_sets = None
    player_stats = None
    team_stats = None
    headers = None

    def __init__(self,
                 last_n_games=LastNGames.default,
                 measure_type_detailed_defense='Base',
                 month=Month.default,
                 opponent_team_id=0,
                 pace_adjust=PaceAdjust.default,
                 per_mode_detailed='Totals',
                 period=Period.default,
                 plus_minus=PlusMinus.default,
                 rank=Rank.default,
                 season=Season.default,
                 season_type_all_star=SeasonTypeAllStar.default,
                 college_nullable='',
                 conference_nullable=ConferenceNullable.default,
                 country_nullable='',
                 date_from_nullable='',
                 date_to_nullable='',
                 division_simple_nullable=DivisionSimpleNullable.default,
                 draft_pick_nullable='',
                 draft_year_nullable='',
                 game_scope_simple_nullable=GameScopeSimpleNullable.default,
                 game_segment_nullable=GameSegmentNullable.default,
                 height_nullable='',
                 league_id_nullable=LeagueIDNullable.default,
                 location_nullable=LocationNullable.default,
                 outcome_nullable=OutcomeNullable.default,
                 po_round_nullable='',
                 player_experience_nullable=PlayerExperienceNullable.default,
                 player_position_abbreviation_nullable=PlayerPositionAbbreviationNullable.default,
                 season_segment_nullable=SeasonSegmentNullable.default,
                 shot_clock_range_nullable=ShotClockRangeNullable.default,
                 starter_bench_nullable=StarterBenchNullable.default,
                 team_id_nullable='',
                 two_way_nullable='',
                 vs_conference_nullable=ConferenceNullable.default,
                 vs_division_nullable=DivisionNullable.default,
                 weight_nullable='',
                 proxy=None,
                 headers=None,
                 timeout=30,
                 get_request=True):
        self.proxy = proxy
        if headers is not None:
            self.headers = headers
        self.timeout = timeout
        self.parameters = {
                'LastNGames': last_n_games,
                'MeasureType': measure_type_detailed_defense,
                'Month': month,
                'OpponentTeamID': opponent_team_id,
                'PaceAdjust': pace_adjust,
                'PerMode': per_mode_detailed,
                'Period': period,
                'PlusMinus': plus_minus,
                'Rank': rank,
                'Season': season,
                'SeasonType': season_type_all_star,
                'College': college_nullable,
                'Conference': conference_nullable,
                'Country': country_nullable,
                'DateFrom': date_from_nullable,
                'DateTo': date_to_nullable,
                'Division': division_simple_nullable,
                'DraftPick': draft_pick_nullable,
                'DraftYear': draft_year_nullable,
                'GameScope': game_scope_simple_nullable,
                'GameSegment': game_segment_nullable,
                'Height': height_nullable,
                'LeagueID': league_id_nullable,
                'Location': location_nullable,
                'Outcome': outcome_nullable,
                'PORound': po_round_nullable,
                'PlayerExperience': player_experience_nullable,
                'PlayerPosition': player_position_abbreviation_nullable,
                'SeasonSegment': season_segment_nullable,
                'ShotClockRange': shot_clock_range_nullable,
                'StarterBench': starter_bench_nullable,
                'TeamID': team_id_nullable,
                'TwoWay': two_way_nullable,
                'VsConference': vs_conference_nullable,
                'VsDivision': vs_division_nullable,
                'Weight': weight_nullable
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
        self.league_dash_player_stats = Endpoint.DataSet(data=data_sets['LeagueDashPlayerStats'])

print('Getting traditional stats information.....')
Player_Stats_Trad = LeagueDashPlayerStats().get_data_frames()[0]
Player_Stats_Trad = Player_Stats_Trad.rename(columns=column_map)
print('Information retreived successfully!')


#Using the nba_api, get information regarding opponent defensive metrics for the current season
class LeagueDashPtDefend(Endpoint):
    endpoint = 'leaguedashptdefend'
    expected_data = {'LeagueDashPTDefend': ['CLOSE_DEF_PERSON_ID', 'PLAYER_NAME', 'PLAYER_LAST_TEAM_ID', 'PLAYER_LAST_TEAM_ABBREVIATION', 'PLAYER_POSITION', 'AGE', 'GP', 'G', 'FREQ', 'D_FGM', 'D_FGA', 'D_FG_PCT', 'NORMAL_FG_PCT', 'PCT_PLUSMINUS']}

    nba_response = None
    data_sets = None
    player_stats = None
    team_stats = None
    headers = None

    def __init__(self,
                 defense_category='Overall',
                 league_id=LeagueID.default,
                 per_mode_simple='Totals',
                 season=Season.default,
                 season_type_all_star=SeasonTypeAllStar.default,
                 college_nullable='',
                 conference_nullable=ConferenceNullable.default,
                 country_nullable='',
                 date_from_nullable='',
                 date_to_nullable='',
                 division_nullable=DivisionNullable.default,
                 draft_pick_nullable='',
                 draft_year_nullable='',
                 game_segment_nullable=GameSegmentNullable.default,
                 height_nullable='',
                 last_n_games_nullable=LastNGamesNullable.default,
                 location_nullable=LocationNullable.default,
                 month_nullable=MonthNullable.default,
                 opponent_team_id_nullable='',
                 outcome_nullable=OutcomeNullable.default,
                 po_round_nullable='',
                 period_nullable=PeriodNullable.default,
                 player_experience_nullable=PlayerExperienceNullable.default,
                 player_id_nullable='',
                 player_position_nullable=PlayerPositionNullable.default,
                 season_segment_nullable=SeasonSegmentNullable.default,
                 starter_bench_nullable=StarterBenchNullable.default,
                 team_id_nullable='',
                 vs_conference_nullable=ConferenceNullable.default,
                 vs_division_nullable=DivisionNullable.default,
                 weight_nullable='',
                 proxy=None,
                 headers=None,
                 timeout=30,
                 get_request=True):
        self.proxy = proxy
        if headers is not None:
            self.headers = headers
        self.timeout = timeout
        self.parameters = {
                'DefenseCategory': defense_category,
                'LeagueID': league_id,
                'PerMode': per_mode_simple,
                'Season': season,
                'SeasonType': season_type_all_star,
                'College': college_nullable,
                'Conference': conference_nullable,
                'Country': country_nullable,
                'DateFrom': date_from_nullable,
                'DateTo': date_to_nullable,
                'Division': division_nullable,
                'DraftPick': draft_pick_nullable,
                'DraftYear': draft_year_nullable,
                'GameSegment': game_segment_nullable,
                'Height': height_nullable,
                'LastNGames': last_n_games_nullable,
                'Location': location_nullable,
                'Month': month_nullable,
                'OpponentTeamID': opponent_team_id_nullable,
                'Outcome': outcome_nullable,
                'PORound': po_round_nullable,
                'Period': period_nullable,
                'PlayerExperience': player_experience_nullable,
                'PlayerID': player_id_nullable,
                'PlayerPosition': player_position_nullable,
                'SeasonSegment': season_segment_nullable,
                'StarterBench': starter_bench_nullable,
                'TeamID': team_id_nullable,
                'VsConference': vs_conference_nullable,
                'VsDivision': vs_division_nullable,
                'Weight': weight_nullable
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
        self.league_dash_p_tdefend = Endpoint.DataSet(data=data_sets['LeagueDashPTDefend'])

print('Getting defensive stats information.....')
Player_Stats_Def = LeagueDashPtDefend().get_data_frames()[0]
Player_Stats_Def = Player_Stats_Def.rename(columns={'CLOSE_DEF_PERSON_ID':'PERSON_ID'})
print('Information retreived successfully!')


#merge the dfs into on on person_id from the All_Player_Info df
All_Player_Info = pd.merge(All_Player_Info,Spot_Up_Rate,on='PERSON_ID',how='left')

All_Player_Info = pd.merge(All_Player_Info,Player_Stats_Trad,on='PERSON_ID',how='left')

All_Player_Info = pd.merge(All_Player_Info,Player_Stats_Def,on='PERSON_ID',how='left')


#remove rows of the df where percentile is NA
    #this removes players who do not meet the minimum qualification to be included in spot up rate shooting statistics
All_Player_Info = All_Player_Info[All_Player_Info['PERCENTILE'].notna()]


#establish thresholds for players we want to deem "3 & D Players"
    #>25% quartile for percentage of possession that result in a spot up shot
    #>25% quartile for games played
min_quantile = All_Player_Info['POSS_PCT'].quantile(.25)
print(f'Players included have a minimum spot up rate of {min_quantile}')
min_games = All_Player_Info['GP'].quantile(.25)
print(f'Players included have played in at least {min_games} games')


#filter the df based on the treshold values established above
All_Player_Info = All_Player_Info[(All_Player_Info['POSS_PCT']>min_quantile) & (All_Player_Info['GP']>min_games)]


#plot the data for 3 & D Players
plt.style.use('fivethirtyeight')
fig, ax = plt.subplots(figsize=(30,25))
x = All_Player_Info['FG3_PCT']
y = All_Player_Info['PCT_PLUSMINUS']
ax.scatter(x,y,s=All_Player_Info['FG3A']*10,c=All_Player_Info['FG3A'])
plt.axvline(x=np.median(list(ax.get_xlim())),linestyle='--',color='black')
plt.axhline(y=0,linestyle='--',color='black')
plt.xlabel('3 Point %',size=20)
plt.ylabel('Defended FG Diff %',size=20)
plt.title("Tracking NBA's 3 & D Players",size=40)
plt.xticks(size=20)
plt.yticks(size=20)


#for each point plot the approporiate headshot of the player
for i, name in enumerate(All_Player_Info['PLAYER_SLUG']):
        
    plt.annotate(name, (All_Player_Info['FG3_PCT'].iat[i]+.003,All_Player_Info['PCT_PLUSMINUS'].iat[i]))

#save the plot    
plt.savefig('3&D Players' + str(date.today()) + '.png')




