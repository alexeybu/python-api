from fastapi import FastAPI
import yfinance as yf
import pandas as pd
import numpy as np

def get_recommendation(tck):
    rec = tck.recommendations_summary
    if rec.shape[0] > 0:
        rec.drop(columns=['period'], inplace=True)
        rec.columns = ['Strong Buy', 'Buy', 'Hold', 'Sell', 'Strong Sell']
        rec_perc = rec.div(rec.sum(axis=1), axis=0)
        
        rec_perc['max_value'] = rec_perc.max(axis=1)
        rec_perc['max_column'] = rec_perc.idxmax(axis=1)
    
        return rec_perc.iloc[0]['max_column'], rec_perc.iloc[0]['max_value']
    else:
        return '-', 0

def get_ticker_information(ticker):
    tck = yf.Ticker(ticker)
    if(tck.info['quoteType'] == 'EQUITY'):
        recommendation, recommendation_percent = get_recommendation(tck)
        if (len(tck.calendar['Earnings Date']) != 0):
            earnings_date = str(tck.calendar['Earnings Date'][0]) 
        else:
            earnings_date = '-'
        targets = tck.analyst_price_targets
        price_low = targets['low']
        price_high = targets['high']
        price_mean = targets['mean']
    else:
        recommendation = '-'
        recommendation_percent = 0
        price_low = 0
        price_high = 0
        price_mean = 0
        earnings_date = '-'
    return {"recommendation": recommendation, 
            "recommendation_percent": np.round(recommendation_percent*100, 0),
            "earnings_date": earnings_date, 
            "price_low": price_low,
            "price_high": price_high,
            "price_mean": price_mean}
app = FastAPI()

@app.get("/{ticker}")
def root(ticker: str):
	return get_ticker_information(ticker)
