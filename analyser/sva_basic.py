from .sva_plots import SvaPlots
import pandas as pd

class SvaBasics(SvaPlots):
    TABLE_SIZE = 15
    NUM_PLAYERS_GRAPH = 5


    def __init__(self, data, excel_delimiter) -> None:
        super().__init__()
        self.rawData = data
        self.excel_delimiter = excel_delimiter
        self.seasonDf = None

    
    def common_data_preparation(sef, df:pd.DataFrame):
        """
            data: DataFrame
        """
        df['date'] = pd.to_datetime(df['date'])
        df['weekday'] = df['date'].dt.day_name(locale='de_DE.utf-8')
        df = df.sort_values('date').reset_index()
        return df

    def set_season_df(self, currentSeason):
        season_id = currentSeason['id']
        self.seasonDf = self.df.loc[self.df['season.id'] == season_id]

        return self.seasonDf