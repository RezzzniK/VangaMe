from django.shortcuts import render
from matplotlib.axis import YAxis
from plotly.offline import plot
import plotly.graph_objects as go
from sympy import div
 
# Create your views here.
def home(requests):
    def tabl_prediction():
      return [['Bitcoin', 'Negative', -0.5874603174603177], ['Ethereum', 'Positive', 4.793968253968254], ['BinanceCoin', 'Positive', 14.990434782608697], ['Tether', 'Positive', 3.1046153846153848], ['Cardano ', 'Positive', 7.986666666666667], ['Solana', 'Positive', 4.785087719298245], ['XRP', 'Positive', 1.1396551724137938], ['Polkadot', 'Positive', 14.475294117647062], ['USDCoin', 'Positive', 8.722000000000001], ['Dogecoin', 'Positive', 0.8961403508771918], ['Avalanche', 'Positive', 19.9252380952381]]
    def scatter():
        #TODO ENTER A FUNCTION TO GET DATA FROM DB
        #AND INSERT IT TO THE X& Y
        x1=[1,2,3,4]
        y1=[30,35,25,45]
        trace=go.Scatter(
            x=x1,
            y=y1
        )
        layout=dict(
            title='History Graph',#also create prediction graph
            paper_bgcolor='#27293d',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis=dict(range=[min(x1),max(x1)]),
            yaxis=dict(range=[min(y1),max(y1)])
            
        )
        fig=go.Figure(data=[trace],layout=layout)
        plot_div=plot(fig,output_type='div',include_plotlyjs=False)
        return plot_div
    context={
        'plot':scatter(),
        'table_prediction':tabl_prediction(),
    }
   

    return render(requests,'home/welcome.html',context)