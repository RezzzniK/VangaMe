from os import stat
from turtle import st
from django.shortcuts import render
from matplotlib.axis import YAxis
from plotly.offline import plot
import plotly.graph_objects as go
from sympy import div
import home.prediction_app.main as predict
import home.prediction_app.vanga_me_core as vanga_core
import home.prediction_app.vanga_configs as cfg
# Create your views here.
def home(requests):
    
    def tabl_prediction():
        
        #TO DO ASYNC RUNNING EVERY MINUTE
        status, predictions=predict.get_future_predictions(term_and_tickers=cfg.basic_search_term_google_and_yf_ticker_name, days_to_subtract=None, check_x_last_hours=24) 
       
        #print(f'=============================================={predict.get_predictions_accuracy(term_and_tickers=cfg.basic_search_term_google_and_yf_ticker_name, days_to_subtract=6)}=========================')
        
        if status:
            return predictions
        else:
            print('no dataaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
        # status,predictions= predict.export_for_tables()
        # if status:
        #     # x = vanga_core.get_future_predictions() 
            
        #     return  x
        # else: 
        #     print(predictions)
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