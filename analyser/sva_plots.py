import pandas as pd
import matplotlib.pyplot as plt
import os

class SvaPlots():

    class PlotData():
        def __init__(self, data, info={}) -> None:
            self.data = data
            self.info = info

    def __init__(self) -> None:
        self.plots = []
        self.subplotTables = []

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
        # print(df[['date', fullNameCol]].head(10))
        
        for player in playerNames:
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

        # print(plottData.head(10))

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
    def subplot(plots:[], fileName=None):

        # set number of graph and figure size
        nPLots = len(plots)
        cm = 1/2.54
        ratio = 45/120
        width = 10
        fig, axes = plt.subplots(nPLots, 1, figsize=(20*cm, 20*cm))
        #fig, axes = plt.subplots(nPLots, 1)
        #fig, axes = plt.subplots(nPLots, 1, figsize=(width, width * ratio))
        # fig, axes = plt.subplots(1, nPLots, figsize=(12*cm, 4.5*cm))

        counter = 0
        for plotData in plots:
            # print(plotData.data.head(10))
            startTime = plotData.data['date'].min()
            endTime = plotData.data['date'].max()
            ax = plotData.data.plot(
                ax=axes[counter],
                x='date',
                xlabel='',
                xticks=[],
                grid = True,
                ylim= (0),
                xlim= (startTime, endTime),
                legend=True,
                lw=2,
                **plotData.info
            )
            # plt.subplots_adjust(right=0.5)
            # ax.legend(loc='upper left',fontsize=8)
            plt.tight_layout(h_pad=0, w_pad=2)
            ax.set_title(plotData.info['title'], pad=2, fontdict={'fontsize':12})
            ax.set_ylabel(plotData.info['ylabel'], fontdict={'fontsize':8})
            ax.legend(bbox_to_anchor=(1.05, 1.05), fontsize= 12)

            counter +=1
        
        if fileName != None:
            plotDir = 'plots\\'

            if not os.path.exists(plotDir):
                os.mkdir(plotDir)
            
            fig.savefig(plotDir + fileName + '.svg', format='svg', transparent=True)
            fig.savefig(plotDir + fileName + '.png', format='png', transparent=True)
        
        # plt.show()
        return fig, axes

