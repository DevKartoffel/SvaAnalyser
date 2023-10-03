import pandas as pd
import matplotlib.pyplot as plt

class SvaPlots():

    class PlotData():
        def __init__(self, data, info={}) -> None:
            self.data = data
            self.info = info

    def __init__(self) -> None:
        self.plots = []

    def get_plots(self):
        return self.plots
    
    def get_player_time_series(self, df, playerName, colName):
        """ Needs a DataFrame sorted by time and index by time
        """
        playerData = df[colName].loc[df[colName] == playerName]

        # Iterrows
        playerTimeSeries = []
        counter = 0
        lastIndex = 0
        for index, value in playerData.items():
            for i in range(lastIndex, index):
                playerTimeSeries.append(counter)
            lastIndex = index
            counter += 1

        # Fill array
        for i in range(lastIndex, len(df)):
            playerTimeSeries.append(counter)

        return playerTimeSeries

    def get_time_series(self, df:pd.DataFrame, playerNames:[], fullNameCol:str, colAttachment:str = 'Strikes ', ):
        """ Returns dataFrame that can be plotted by time
        """

        df = df.sort_values('date').reset_index() 
        for player in playerNames:
            print('Analyse ' + player)
            timeSeries = self.get_player_time_series(df, player, fullNameCol)
            # print(timeSeries)
            df[colAttachment + player] = timeSeries
            
            # print(self.df[['date', 'striker.full_name', 'Strikes ' + player]].head(15))

        dateGroups = df.groupby('date')
        dates = list(dateGroups.groups)

        plottData = pd.DataFrame({'date': dates})

        for player in playerNames:
            values = dateGroups[colAttachment + player].max()
            plottData[player] = values.values

        return plottData
    
    def get_plots(self):
        return self.plots

    @staticmethod
    def set_plot_props(ax, *args):
        ax.set_xticklabels([])  

        # for key, value in args:
        ax.set(args.__dict__())

        return ax

    @staticmethod
    def show_plots():
        plt.show()
    
    @staticmethod
    def subplot(plots:[]):
        nrow = len(plots)
        fig, axes = plt.subplots(nrow, 1)

        counter = 0
        for plotData in plots:
            startTime = plotData.data['date'][0]
            endTime = plotData.data['date'][len(plotData.data)-1]
            ax = plotData.data.plot(
                ax=axes[counter],
                x='date',
                xlabel='',
                xticks=[],
                grid = True,
                ylim= (0),
                xlim= (startTime, endTime),
                **plotData.info
            )
            ax.legend(loc='upper left')

            counter +=1


