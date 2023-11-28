#pip install -r requirements.txt
import pandas as pd 
import numpy as np
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go

forecasts_database = pd.read_csv('forecasts_database.csv', index_col=0)
forecasts_database.index = pd.to_datetime(forecasts_database.index)
expected_irr = pd.read_csv('expected_irr.csv', index_col=0)
expected_irr['date_forecast'] = pd.to_datetime(expected_irr['date_forecast'])
irr_real = pd.read_csv('irr_real.csv', index_col=0)
irr_real['date'] = pd.to_datetime(irr_real['date'])
complete_irr = pd.read_csv('complete_irr.csv', index_col=0)
complete_irr[['cur_date', 'end_date', 'start_date']] = complete_irr[['cur_date', 'end_date', 'start_date']].apply(pd.to_datetime)
conjunto_geo_slice = complete_irr['geo_slice'].unique().tolist()
data_2 = pd.read_csv('data_2.csv', index_col=0).query('geo_slice in  @conjunto_geo_slice')
data_2['period'] = pd.to_datetime(data_2['period'])
data_model = pd.read_csv('data_model.csv', index_col=0).query('geo_slice in  @conjunto_geo_slice')
data_model['period'] = pd.to_datetime(data_model['period'])


################################################################################################################################
categories_options = [{'label': x, 'value': x} for x in conjunto_geo_slice]
################################################################################################################################
fig = go.Figure()
fig.update_layout(    
    xaxis_title="Date", 
    xaxis = dict(   
        
        domain=[0.15, 0.98],
        title="Date",
        titlefont=dict(
            color="black"),
        tickfont=dict(
            color="black"),
        showgrid=False,
        dtick='M12', )
        #range=[])
    ,
    yaxis=dict(

        title="Price - USD",
        titlefont=dict(
            color="purple", 
            size = 20),
        tickfont=dict(
            color="purple"),
        tickformat = '$,.0f', 
        showgrid=True,
        position=0.0,
        #range=[0,(int(forecasts_database['fc_upper'].max() / 10000) + 1)*10000 ],
        zeroline=True,
        #dtick=(int(forecasts_database['fc_upper'].max() / 10000) + 1)*500 ,
        #gridcolor='white',
        #gridwidth=0.5,
    ),
    yaxis2=dict(
        title="% - IRR Current Vs Forecast",
        titlefont=dict(
            color="black", 
            size = 20),
        tickfont=dict(
            color="black"),
        anchor="free",
        overlaying="y",
        side="left",
        position=0.14,
        showgrid=True,
        tickformat =',.1%',# ',.0%',
        #zeroline=True,
        #range=[-0.2, 3.8],
        #dtick=0.2,
    ),
    yaxis3=dict(
        title="Rent - USD", # % IRR RATE YTD
        titlefont=dict(
            color="#204a01", 
            size = 20           
            ),
        tickfont=dict(
            color="#204a01"),
        anchor="free",
        overlaying="y",
        side="left",
        position=0.07,
        showgrid=False,
        tickformat ='$,.0f',# ',.0%',
        zeroline=False,
        #range=[0,2000 ],
        #dtick=200,
        ## hide axis
        showticklabels=True,
        
    )
    ,
    legend=dict(
        x=0,
        y=1.15,
        traceorder="normal",
        font=dict(
            family="sans-serif",
            size=12,
            color="black"
        ),
        bgcolor="white",
        bordercolor="black",
        borderwidth=1),

    autosize=False,
    legend_orientation="h",
    margin=dict(
        l=50,
        r=50,
        b=100,
        t=100,
        pad=4,
    ),

)
fig.update_layout(width = 1500, height = 700)

app = dash.Dash(__name__)
app.layout = html.Div([
    # Dropdown for selecting category
    dcc.Dropdown(
        id='category-dropdown',
        options=categories_options,
        value= categories_options[0]['value'],
        # Set default value to the first category
        multi=False,
    ), 

    # Plotly chart
    dcc.Graph(
        id='my-chart',
        figure={}  # Use the figure you created earlier
    )
])

# Callback to update the chart based on the selected category
@app.callback(
    Output('my-chart', 'figure'),
    [Input('category-dropdown', 'value')]
)
def update_chart(category):
    #category = categories_options[5]['value']
    # Filter the data
    data_model_f = data_model.query('geo_slice == @category').copy()
    forecast_database_f = forecasts_database.query('geo_slice == @category').copy()
    price_f = forecast_database_f.query('yy == "price"').copy()
    rent_f = forecast_database_f.query('yy == "ef_r"').copy()
    expected_irr_f = expected_irr.query('geo_slice == @category').copy()
    irr_real_f = irr_real.query('geo_slice == @category').copy()
    data_costar_f = data_2.query('geo_slice == @category').copy()
    irr_m_f = complete_irr.query('geo_slice == @category').copy()
    costar_f = data_costar_f.query('period >= "2023-10-01"')[:21].copy()
    # Create the plot
    fig = go.Figure()
    fig.update_layout(xaxis_title="Date",xaxis = dict(  domain=[0.15, 0.98],
                                                        title="Date",
                                                        titlefont=dict(color="black"),
                                                        tickfont=dict(color="black"),
                                                        showgrid=False,dtick='M12')
        ,
        yaxis=dict(title="Price - USD",titlefont=dict(color="purple",size = 20),
                                        tickfont=dict(color="purple"), tickformat = '$,.0f', 
                                        showgrid=True,position=0.0,
                                        range=[0,(int(costar_f['price'].max() / 10000) + 2)*12000 ],
                                        zeroline=True,
                                        dtick=(int(costar_f['price'].max() / 10000) + 2)*600 ,
                                        gridcolor='white',
                                        gridwidth=0.5)
        ,
        yaxis2=dict(title="% - IRR Current Vs Forecast",titlefont=dict(color="black", size = 20),                    
                                                        tickfont=dict(color="black"), anchor="free",
                                                        overlaying="y",side="left",position=0.14,
                                                        showgrid=True,tickformat =',.1%',# ',.0%',
                                                        zeroline=True,range=[-0.2, 3.8], dtick=0.2)
        ,
        yaxis3=dict(title="Rent - USD", titlefont=dict(color="#204a01", size = 20),
                                        tickfont=dict(color="#204a01"),anchor="free",
                                        overlaying="y",side="left",position=0.07,
                                        showgrid=False,tickformat ='$,.0f',# ',.0%',
                                        zeroline=False,
                                        range = [0 ,int(((costar_f['ef_r'].max() /1000) + 1)*1000) * 1.2 ],
                                        #range=[0,2000 ], #dtick=200,
                                        showticklabels=True)
        ,
        legend=dict(x=0,y=1.06, traceorder="normal", font=dict(family="sans-serif",size=12, color="black"), bgcolor="white", bordercolor="black", borderwidth=1)
        ,
        autosize=False,  legend_orientation="h",margin=dict(l=50,r=50,b=100,t=100,pad=4)
        ,
        )   
    fig.update_layout(width = 1750, height = 900, title = category)
    ## PRECIO DE LA VIVIENDA
    fig.add_trace(go.Scatter(x=data_model_f['period'], y=data_model_f['price'], name='Market Sale Price per Unit +  Forecasts', line_color='purple', mode='lines+markers', line = dict(color = 'blue', width = 1), marker= dict(size = 2), showlegend= True ))
    fig.add_trace(go.Scatter(x=price_f.index, y=price_f['fc'], mode='lines+markers', marker=dict(size = 2 ), line = dict( width = 1), showlegend= False ))
    fig.add_trace(go.Scatter(x=price_f.index, y=price_f['fc_lower'], fill= 'tonexty', mode= 'markers', marker=dict(color='white', size=1), fillcolor= 'rgba(111, 242, 168,0.2)',  showlegend= False ))
    fig.add_trace(go.Scatter(x=price_f.index, y=price_f['fc_upper'], fill= 'tonexty', mode= 'markers', marker=dict(color='white', size=1), fillcolor= 'rgba(111, 242, 168,0.5)',  showlegend= False ))
    fig.add_trace(go.Scatter(x=costar_f['period'], y=costar_f['price'], name='Costar Price' , mode='lines+markers', marker=dict (size = 2), line = dict( width = 1), showlegend= True ))

    ## RENTA
    fig.add_trace(go.Scatter(x=data_model_f['period'], y=data_model_f['ef_r'], name='Market Rent per Unit + Forecasts', line_color='#204a01', mode='lines+markers', line = dict(color = '#204a01', width = 1), marker= dict(size = 2), showlegend= True,  yaxis='y3' ))                         
    fig.add_trace(go.Scatter(x=rent_f.index, y=rent_f['fc'], mode='lines+markers', marker=dict(size = 2 ), line = dict( width = 1), showlegend= False, yaxis='y3' ))
    fig.add_trace(go.Scatter(x=rent_f.index, y=rent_f['fc_lower'], fill= 'tonexty', mode= 'markers', marker=dict(color='white', size=1), fillcolor= 'rgba(111, 242, 168,0.2)',  showlegend= False, yaxis='y3' ))
    fig.add_trace(go.Scatter(x=rent_f.index, y=rent_f['fc_upper'], fill= 'tonexty', mode= 'markers', marker=dict(color='white', size=1), fillcolor= 'rgba(111, 242, 168,0.5)',  showlegend= False, yaxis='y3' ))
    fig.add_trace(go.Scatter(x=costar_f['period'], y=costar_f['ef_r'], name='Costar Rent' , mode='lines+markers', marker=dict (size = 2), line = dict( width = 1), showlegend= True, yaxis='y3' ))

    ## IRR
    fig.add_trace(go.Scatter( x = expected_irr_f['date_forecast'], y = expected_irr_f['upper'], mode='lines', line = dict(color = 'white', width = 1), yaxis='y2', showlegend= False  ))
    fig.add_trace(go.Scatter( x = expected_irr_f['date_forecast'], y = expected_irr_f['lower'], name='Forecast IRR (Bands)', mode='lines', line = dict(color = 'white', width = 1), yaxis='y2', fill='tonexty', fillcolor= 'rgba(62, 222, 203, 0.3)'  ))
    fig.add_trace(go.Scatter( x = expected_irr_f['date_forecast'], y = expected_irr_f['mean'], name='Forecast IRR (Mean)', mode='lines', line = dict(color = 'black', width = 1), yaxis='y2'  ))
    fig.add_trace(go.Bar( x = irr_real_f['date'], y = irr_real_f['irr'],  name="IRR Current", opacity=0.2, yaxis='y2' , marker_color = 'Royalblue'))

    ## Points, stars and annotations

    ## IRR
    fig.add_shape( type= 'line' , x0= '2023-10-01', y0= 0, x1= '2023-10-01', y1= 1, line=dict(color='rgba(100,100,100,0.3)',width=1, dash="dot"), xref='x', yref='paper', layer="below")
    fig.add_shape( type= 'line' , x0= '2022-04-01', y0= 0, x1= '2022-04-01', y1= 1, line=dict(color='rgba(100,100,100,0.3)',width=1, dash="dot"), xref='x', yref='paper', layer="below")
    fig.add_shape( type= 'line' , x0= '2009-07-01', y0= 0, x1= '2009-07-01', y1= 1, line=dict(color='rgba(100,100,100,0.3)',width=1, dash="dot"), xref='x', yref='paper', layer="below")

    # OTHERS

    fig.add_annotation(x=-0.05, y= -0.13, text="** Assumptions:    1- Expenses at 50% of the net operating income. 2- Spread over the 10 Years Yield of 300 Basis Points.", showarrow=False, arrowhead=1, ax=0, ay=-40, bgcolor="white", bordercolor="black", borderwidth=1,  yref='paper',xref = 'paper', font=dict(size=11, color='black')  )
    ################################################################################################################################
    current_price = data_model_f['price'].iloc[-1]
    current_rent = data_model_f['ef_r'].iloc[-1]
    current_irr = irr_real_f.dropna()['irr'].iloc[-1]

    current_price_string = format(current_price, ',.0f')
    current_rent_string = format(current_rent, ',.0f')
    current_irr_string = format(current_irr, ',.1%')
    ################################################################################################################################
    fc_price = price_f['fc'].iloc[-1]
    fc_rent = rent_f['fc'].iloc[-1]
    fc_irr = expected_irr_f['mean'].iloc[-1]

    fc_price_string = format(fc_price, ',.0f')
    fc_rent_string = format(fc_rent, ',.0f')
    fc_irr_string = format(fc_irr, ',.1%')
    ################################################################################################################################
    costar_price = costar_f['price'].iloc[-1]
    costar_rent = costar_f['ef_r'].iloc[-1]
    costar_irr = irr_m_f['irr'].iloc[-1]

    costar_price_string = format(costar_price, ',.0f')
    costar_rent_string = format(costar_rent, ',.0f')
    costar_irr_string = format(costar_irr, ',.1%')
    ################################################################################################################################
    date_current = data_model_f['period'].iloc[-1]
    date_forecast = price_f.index[-1]
    date_current_irr = irr_real_f.dropna()['date'].iloc[-1]
    ################################################################################################################################
    current_debt_rate = costar_f['rate'].iloc[0]
    current_debt_rate_str = str(round(current_debt_rate * 100, 2)) + '%'
    ################################################################################################################################
    current_noi = costar_f['ef_r'].iloc[0] * 12 * 0.5
    current_noi_p = current_noi / costar_f['price'].iloc[0]
    current_noi_p_str = str(round(current_noi_p * 100, 2)) + '%'
    ################################################################################################################################
    current_rent_less_interest = current_noi_p - current_debt_rate
    current_rent_less_interest_str = str(round(current_rent_less_interest * 100, 2)) + '%'
    ################################################################################################################################
    # PRICE
    fig.add_annotation(x= date_current , y = current_price, text= 'Cnt:$' + current_price_string, showarrow=True, arrowhead=1, ax=0, ay=0, bgcolor="white", bordercolor="black", borderwidth=1,  yref='y1')
    fig.add_annotation(x= date_forecast, y = fc_price, text= 'Fcst:$' + fc_price_string, showarrow=True, arrowhead=1, ax=0, ay=0, bgcolor="#34ebdb", bordercolor="black", borderwidth=1,  yref='y1')
    fig.add_annotation(x= date_forecast, y = costar_price, text= 'Cstr:$' + costar_price_string, showarrow=True, arrowhead=1, ax=0, ay=-15, bgcolor="orange", bordercolor="black", borderwidth=1,  yref='y1')
    # RENT
    fig.add_annotation(x= date_current , y = current_rent, text= 'Cnt:$' + current_rent_string, showarrow=True, arrowhead=1, ax=0, ay=0, bgcolor="white", bordercolor="black", borderwidth=1,  yref='y3')
    fig.add_annotation(x= date_forecast, y = fc_rent, text= 'Fcst:$' + fc_rent_string, showarrow=True, arrowhead=1, ax=0, ay=0, bgcolor="#34ebdb", bordercolor="black", borderwidth=1,  yref='y3')
    fig.add_annotation(x= date_forecast, y = costar_rent, text= 'Cstr:$' + costar_rent_string, showarrow=True, arrowhead=1, ax=0, ay=5, bgcolor="orange", bordercolor="black", borderwidth=1,  yref='y3')
    # IRR
    fig.add_annotation(x= date_current_irr , y = current_irr, text=  'Latest 5y IRR:' +current_irr_string, showarrow=True, arrowhead=1, ax=0, ay=0, bgcolor="white", bordercolor="black", borderwidth=1,  yref='y2')
    fig.add_annotation(x= date_current, y = fc_irr, text= 'Current Forecast:' +fc_irr_string, showarrow=True, arrowhead=1, ax=0, ay=0, bgcolor="#34ebdb", bordercolor="black", borderwidth=1,  yref='y2')
    fig.add_annotation(x= date_current, y = costar_irr, text='Costar Forecast:' + costar_irr_string, showarrow=True, arrowhead=1, ax=0, ay=-5, bgcolor="orange", bordercolor="black", borderwidth=1,  yref='y2')

    # Assumpitons chart upper 
    fig.add_annotation(x= date_current, y = 0.965 , text= 'Current Assumed Debt Rate  SOFR 10Y + 300 b.p.:  ' + current_debt_rate_str, showarrow=True, arrowhead=1, ax=-174, ay=0, bgcolor="#eb6e74", bordercolor="black", borderwidth=1,  yref='paper')
    fig.add_annotation(x= date_current, y = 0.993 , text= 'Current Assumed NOI Margin:  ' + current_noi_p_str, showarrow=True, arrowhead=1, ax=-110, ay=0, bgcolor="#86e394", bordercolor="black", borderwidth=1,  yref='paper')
    fig.add_annotation(x= date_current, y = 0.937 , text= 'Current Assumed Profit from Holding: ' + current_rent_less_interest_str, showarrow=True, arrowhead=1, ax=-131, ay=0, bgcolor="#d9b0eb", bordercolor="black", borderwidth=1,  yref='paper')

    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
