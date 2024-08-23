import pandas as pd
from .sva_basic import SvaBasics
from datetime import date

class Flyover(SvaBasics):

    def __init__(self, data, excelPath) -> None:
        super().__init__(data, excelPath)
        self.df = self.prepare_data(data)
        
    
    def prepare_data(sef, data):
        """
            data: in json format
        """
        
        df = pd.json_normalize(data).drop(columns=['season.picture', 'striker.member.date_of_birth',  'striker.member.picture', 'striker_name', 'striker.member.is_active', 'striker.member.seasons', 'striker.name', 'striker.id'])
        df['striker.full_name'] = df['striker.member.name'] + ' ' + df['striker.member.surename']
        df = super().common_data_preparation(df)
        return df
    
    def analyse(self, current_season=None, team=None):
        """
        data: dict or list[dict]
        """
        # Filter Data
        if current_season:
            df = self.get_season_df(current_season)
        else:
            df = self.df.copy()

        

        # Analys by groups
        grp = df.groupby(['striker.full_name'], as_index=False)
        simple_data = grp['striker.full_name'].value_counts().sort_values(['count', 'striker.full_name'], ascending=[False, True])
        #simple_data.head(self.TABLE_SIZE).to_csv('./csv/zaunkoenig.csv', index=False, header=['Name', 'Zaunschüsse'], sep=self.excel_delimiter)

        if team != None:
            # TODO: Add is Player
            dfTeam = pd.json_normalize(team)

            # Delete inactive members
            dfTeam = dfTeam.drop(dfTeam[~dfTeam['is_active']].index) # TODO: drop all !players

            # create names
            dfTeam['striker.full_name'] = dfTeam['name'] + ' ' + dfTeam['surename']
            dfTeam['count'] = 0
            # Drop rest
            dfTeam = dfTeam.drop( columns=['name', 'is_active', 'surename'])

            # Filter missin players
            missing_strikers = dfTeam[~dfTeam['striker.full_name'].isin(simple_data['striker.full_name'])]

            # Add missing players to data
            simple_data = pd.concat([simple_data, missing_strikers], ignore_index=True).sort_values(['count', 'striker.full_name'], ascending=[False, True])

        
        # For plotting tale
        simple_data.rename(
            columns={"count": "Zaunschüsse", "striker.full_name": "Name"},
            inplace=True,
        )
        info = {}
        self.subplotTables.append(self.PlotData(simple_data.head(self.TABLE_SIZE), info))

        # print to excel
        self.toExcelSheet(simple_data.head(self.TABLE_SIZE), 'Zaunkönig')

        # Get first players to analyse
        topStrikers = simple_data['Name'].head(self.NUM_PLAYERS_GRAPH)

        # Analyse Nutmeg Kings
        info = {
            'ylabel': '',
            'title': 'Zaunkönig'
        }
        self.plots.append(self.PlotData(self.get_time_series(df, topStrikers.values, 'striker.full_name', ''), info) )
        # self.plots['Flyover']['plot'] = plottData.plot(x='date', xlabel='Zeit', ylabel='Verteilte Tunnler', title='Tunnelkönig')

        return True