from datetime import datetime
from io import BytesIO
from datetime import datetime

from matplotlib.pyplot import legend
from DBConnection import DBConnection
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import gc


def createPicture(values: list, dates: list) -> BytesIO:

    d_dates = list()
    for elem in dates:
        d_dates.append(datetime.strptime(elem, "%Y-%m-%d %H:%M:%S"))

    dates = d_dates    
    border = 1200
    ts = pd.DataFrame({'dates': dates, 'values': values })
    sns.set_theme("notebook")
    fig, ax = plt.subplots(**{"num":0, "dpi":1000, "clear":True, "figsize":[1200/100, 1200/100]})
    sns.lineplot(x=[dates[0], dates[-1]],y=border, color='red', ax=ax)
    sns.lineplot(x="dates", y="values", data=ts, ax=ax)

    border = [border] * len(dates)
    N = len(dates)
    dates = pd.date_range(start=dates[0], periods=N, freq="5min")
    ts = pd.DataFrame({'dates': dates, 'values': values })

    z1 = np.array(border)
    z2 = np.array(values)

    plt.fill_between(x=dates, y1=z2, y2=z1, where=(z1 <= z2), alpha=0.68, color='red', interpolate=True, figure=fig)
    plt.fill_between(x=dates, y1=z2, y2=z1, where=(z2 < z1), alpha=0.68, color='green', interpolate=True, figure=fig)

    # ax.axes.yaxis.set_visible(False)
    ax.set_yticklabels([])
    ax.set_ylabel('quality')

    file_mem_obj = BytesIO()
    fig.savefig(file_mem_obj, format='png', dpi=100)
    file_mem_obj.seek(0)
    plt.close(fig)
    del fig
    gc.collect()
    return file_mem_obj

class GetPictureOfeCO2(object):
    def __init__(self, DB_URL: str):
        self.data_source = DBConnection(DB_URL)
    
    def getPicture(self, start: datetime, end: datetime, sensor_id: int) -> list:
        data = self.data_source.getDataeCO2(start, end, sensor_id)
        
        eCO2 = list()
        timestamp = list()

        for elem in data:
            eCO2.append(elem["eCO2"]),
            timestamp.append(elem["timestamp"])

        return [
            createPicture(eCO2, timestamp )
        ]
