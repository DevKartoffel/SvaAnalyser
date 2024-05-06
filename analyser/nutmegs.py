import pandas as pd
import matplotlib.pyplot as plt
import os
import json
from dotenv import load_dotenv
import locale
from datetime import date
from .sva_basic import SvaBasics

class Nutmeg(SvaBasics):
    

    def __init__(self, data, excelPath) -> None:
        super().__init__(data, excelPath)
        self.df = self.prepare_data(data)
    
    def prepare_data(sef, data):
        """
            data: in json format
        """

        df = pd.json_normalize(data).drop(
        columns=[
            'season.picture', 'striker.member.date_of_birth',  'striker.member.picture', 'striker_name', 'striker.member.is_active', 'striker.member.seasons', 'striker.name', 'striker.id',
            'victom.member.date_of_birth',  'victom.member.picture', 'victom_name', 'victom.member.is_active', 'victom.member.seasons', 'victom.name', 'victom.id'
            ]
        )
        df['striker.full_name'] = df['striker.member.name'] + ' ' + df['striker.member.surename']
        df['victom.full_name'] = df['victom.member.name'] + ' ' + df['victom.member.surename']
        df = super().common_data_preparation(df)
        return df
    
    
    def analyse(self, current_season=None, team=None, numGraphs=3):
        """
        """
        # Filter Data
        if current_season:
            df = self.get_season_df(current_season)
        else:
            df = self.df.copy()
        
        # Write data to csv
        # df.to_csv('./csv/tunnler_all.csv')

        # group data 
        striker = df.groupby(['striker.full_name'], as_index=False)['striker.full_name'].value_counts().sort_values('count', ascending=False)
        victoms = df.groupby(['victom.full_name'], as_index=False)['victom.full_name'].value_counts().sort_values('count', ascending=False)
        striker_weekday = pd.crosstab(index=df['striker.full_name'],columns=df['weekday'], margins=True, margins_name='Summe')
        victom_weekday = pd.crosstab(index=df['victom.full_name'],columns=df['weekday'], margins=True, margins_name='Summe')
        crosstab = pd.crosstab(index=df['striker.full_name'],columns=df['victom.full_name'], margins=True, margins_name='Summe') # cross tabele
        
        # Create a suqare matrix
        i = crosstab.index.union(df.columns)
        crosstabSquared = crosstab.reindex(index=i, columns=i, fill_value=0)

        # Find nemesis
        temp = crosstabSquared.add(crosstabSquared.transpose(copy=True)).drop('Summe')
        # print(crosstab)
        # print(temp)
        nemesisMax = temp.max()
        nemesisIndex = temp.idxmax()
        nemesisStrikes = []
        nemesisGotStriked = []

        nemesis = pd.DataFrame({'Spieler': nemesisIndex.index, 'Nemesis': nemesisIndex.values, 'Treffer': nemesisMax.values})
        
        for i, row in nemesis.iterrows():
            nemesisName = row['Nemesis']
            playerName = row['Spieler']
            nemesisStrikes.append(crosstabSquared.loc[playerName, nemesisName])
            nemesisGotStriked.append(crosstabSquared.loc[nemesisName, playerName])
        
        nemesis['Verteilt'] = nemesisStrikes
        nemesis['Bekommen'] = nemesisGotStriked
        nemesis = nemesis.set_index('Spieler')   

        
        # print(nemesis)
        
        
        if team != None:
            # TODO: Add is Player
            dfTeam = pd.json_normalize(team)

            # Delete inactive members
            dfTeam = dfTeam.drop(dfTeam[~dfTeam['is_active']].index) # TODO: drop all !players

            # create names
            dfTeam['striker.full_name'] = dfTeam['name'] + ' ' + dfTeam['surename']
            dfTeam['victom.full_name'] = dfTeam['name'] + ' ' + dfTeam['surename']
            dfTeam['count'] = 0
            # Drop rest
            dfTeam = dfTeam.drop( columns=['name', 'is_active', 'surename'])

            # Filter missin players
            missing_strikers = dfTeam[~dfTeam['striker.full_name'].isin(striker['striker.full_name'])]
            missing_victoms = dfTeam[~dfTeam['victom.full_name'].isin(victoms['victom.full_name'])]

            # Add missing players to data
            striker = pd.concat([striker, missing_strikers], ignore_index=True).drop(columns=['victom.full_name']).sort_values(['count', 'striker.full_name'], ascending=[False, True])
            victoms = pd.concat([victoms, missing_victoms], ignore_index=True).drop(columns=['striker.full_name']).sort_values(['count', 'victom.full_name'], ascending=[False, True])

        # Rename cols
        striker.rename(
            columns={"count": "Tunnler", "striker.full_name": "Name"},
            inplace=True,
        )
        victoms.rename(
            columns={"count": "Tunnler", "victom.full_name": "Name"},
            inplace=True,
        )

        # write final csvs
        # striker.head(self.TABLE_SIZE).to_csv('./csv/tunnelkoenig.csv', index=False, sep=self.excel_delimiter)
        # victoms.head(self.TABLE_SIZE).to_csv('./csv/elbtunnel.csv', index=False, sep=self.excel_delimiter)
        self.toExcelSheet(striker.head(self.TABLE_SIZE), 'Tunnelkönig')
        self.toExcelSheet(victoms.head(self.TABLE_SIZE), 'Elbtunnel')

        # special tables
        self.toExcelSheet(crosstab, 'Kreuztabelle', True)
        self.toExcelSheet(crosstabSquared.set_index('striker.full_name'), 'KreuztabelleQuad', True)
        self.toExcelSheet(nemesis, 'Nemesis', True)
        
        self.toExcelSheet(striker_weekday.head(self.TABLE_SIZE), 'Tunnelkönig Wochentage', True)
        self.toExcelSheet(victom_weekday.head(self.TABLE_SIZE), 'Elbtunnel Wochentage', True)
        # crosstab.to_csv('./csv/tunnler_kreuztabelle.csv',index_label="Verteiler", sep=self.excel_delimiter)
        # striker_weekday.to_csv('./csv/tunnelkoenig_wochentag_verteiler.csv', index_label="Verteiler", sep=self.excel_delimiter)
        # victom_weekday.to_csv('./csv/tunnelkoenig_wochetntag_opfer.csv', index_label="Opfer", sep=self.excel_delimiter)
        
        

        info = {}
        self.subplotTables.append(self.PlotData(striker.head(self.TABLE_SIZE), info))
        self.subplotTables.append(self.PlotData(victoms.head(self.TABLE_SIZE), info))

        # Get first players to analyse
        topStrikers = striker['Name'].head(self.NUM_PLAYERS_GRAPH)
        topVictoms = victoms['Name'].head(self.NUM_PLAYERS_GRAPH)

        # Analyse Nutmeg Kings
        info = {
            'ylabel': '',
            'title': 'Tunnelkönig'
        }
        self.plots.append(self.PlotData(self.get_time_series(df, topStrikers.values, 'striker.full_name', 'Strikes '), info))
        # self.plots['nutmegKing'] = plottData.plot(x='date', xlabel='Zeit', ylabel='Verteilte Tunnler', title='Tunnelkönig')
        # self.plots['nutmegKing'].set_xticklabels([])

        # Analyse Nutmeg Kings
        info = {
            'ylabel': '',
            'title': 'Elbtunnel'
        }
        self.plots.append(self.PlotData(self.get_time_series(df, topVictoms.values, 'victom.full_name', 'Victom '), info))
        # self.plots['elbNutmeg'] = plottData.plot(x='date', xlabel='Zeit', ylabel='Erhaltene Tunnler', title='Elbtunnel')
        # self.plots['elbNutmeg'].set_xticklabels([])      

        
    def test(self):
        
        return True