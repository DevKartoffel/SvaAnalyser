import pandas as pd
from .sva_basic import SvaBasics
from datetime import date

class Flyover(SvaBasics):

    def __init__(self, data, excel_delimiter) -> None:
        super().__init__(data, excel_delimiter)
        self.df = self.prepare_data(data)
        
    
    def prepare_data(sef, data):
        """
            data: in json format
        """
        
        df = pd.json_normalize(data).drop(columns=['season.picture', 'striker.member.date_of_birth',  'striker.member.picture', 'striker_name', 'striker.member.is_active', 'striker.member.seasons', 'striker.name', 'striker.id'])
        df['striker.full_name'] = df['striker.member.name'] + ' ' + df['striker.member.surename']
        df = super().common_data_preparation(df)
        return df
    
    def analyse(self, current_season, team=None, numGraphs=3):
        """
        data: dict or list[dict]
        """
        # Filter Data
        season_id = current_season['id']
        df = self.df.loc[self.df['season.id'] == season_id]

        # Analys by groups
        grp = df.groupby(['striker.full_name'], as_index=False)
        simple_data = grp['striker.full_name'].value_counts().sort_values('count', ascending=False)
        simple_data.head(10).to_csv('./csv/simple_zaunkoenig.csv', index=False, header=['Name', 'Zaunschüsse'], sep=self.excel_delimiter)

        # Get first players to analyse
        topStrikers = simple_data['striker.full_name'].head(numGraphs)

        # Analyse Nutmeg Kings

        info = {
            'ylabel': '',
            'title': 'Zaunkönig'
        }

        self.plots.append(self.PlotData(self.get_time_series(df, topStrikers.values, 'striker.full_name', ''), info) )
        # self.plots['Flyover']['plot'] = plottData.plot(x='date', xlabel='Zeit', ylabel='Verteilte Tunnler', title='Tunnelkönig')

        return True