from os import stat
from turtle import st
from django.shortcuts import render
from django.template import RequestContext
from matplotlib.axis import YAxis
from plotly.offline import plot
import plotly.graph_objects as go
from sympy import div
import home.prediction_app.main as predict
import home.prediction_app.vanga_me_core as vanga_core
import home.prediction_app.vanga_configs as cfg
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

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
        table_view=vanga_core.get_data_for_monthly_accuracy_table_view([['Bitcoin','BTC-USD']])
        counter=1
        x1=[]#[1,2,3,4]
        y1=[]#[30,35,25,45]
        for key,values in table_view.items():
            print(key)
            for date,value in values:
                print(date)
                x1.append(counter)
                val=1/counter
                counter+=1
                print(value)
                
                y1.append(val)
       
       
        #TODO ENTER A FUNCTION TO GET DATA FROM DB
        #AND INSERT IT TO THE X& Y
        print()
        # x1=[1,2,3,4]
        # y1=[30,35,25,45]
        yrange=[0,1]
        trace=go.Scatter(
            x=x1,
            y=y1
        )
        layout=dict(
            title='Bitcoin Prediction History Graph',#also create prediction graph
            paper_bgcolor='#27293d',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis=dict(range=[min(x1),max(x1)]),
            yaxis=dict(range=[min(yrange),max(yrange)])
            
        )
        fig=go.Figure(data=[trace],layout=layout)
        plot_div=plot(fig,output_type='div',include_plotlyjs=False)
        return plot_div
    context={
        'plot':scatter(),
        'table_prediction':tabl_prediction(),
    }
   

    return render(requests,'home/welcome.html',context)


@csrf_exempt
def ShowCryptoHistory(request):

    history=request.POST.get('history',None)
   
    switcher = {
            'Bitcoin':['Bitcoin','BTC-USD'],
            'Ethereum':['Ethereum', 'ETH-USD'],
            'BinanceCoin':['BinanceCoin', 'BNB-USD'],
            'Tether':['Tether', 'USDT-USD'],
            'Cardano': ['Cardano', 'ADA-USD'],
            'Solana':['Solana', 'SOL1-USD'],
            'XRP':['XRP', 'XRP-USD'], 
            'Polkadot':['Polkadot', 'DOT1-USD'],
            'USDCoin':['USDCoin', 'USDC-USD'],
             'hex coin':['"hex coin"', 'HEX-USD'],
             'Dogecoin':['Dogecoin', 'DOGE-USD'],
             'Avalanche':['Avalanche', 'AVAX-USD']
        }
    
                                               
    table_view=vanga_core.get_data_for_monthly_accuracy_table_view([switcher[history]])
    def tabl_prediction():
        
        status, predictions=predict.get_future_predictions(term_and_tickers=cfg.basic_search_term_google_and_yf_ticker_name, days_to_subtract=None, check_x_last_hours=24) 
       
       
        if status:
            return predictions
        else:
            print('no dataaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
       
    def scatter():
        
        counter=1
        x1=[]#[1,2,3,4]
        y1=[]#[30,35,25,45]
        for key,values in table_view.items():
            print(key)
            for date,value in values:
                print(date)
                x1.append(counter)
                val=1/counter
                counter+=1
                print(value)
                
                y1.append(val)
        
        trace=go.Scatter(
            x=x1,
            y=y1
        )
        yrange=[0,1]

        layout=dict(
            title=f'{history} History Prediction Graph',#also create prediction graph
            paper_bgcolor='#27293d',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis=dict(range=[min(x1),max(x1)]),
            yaxis=dict(range=[min(yrange),max(yrange)])
            
        )
        fig=go.Figure(data=[trace],layout=layout)
        plot_div=plot(fig,output_type='div',include_plotlyjs=False)
        return plot_div
    context={
         'plot':scatter(),
         'table_prediction':tabl_prediction(),


    }
    return render(request,'home/welcome.html',context)
