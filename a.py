import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
import time

# पेज की सेटिंग
st.set_page_config(page_title="Dev 22 - Live Order Flow Analyzer", layout="wide")

st.markdown("""
    <h1 style='text-align: center; color: #00FFA3;'>🚀 Dev 22 - Live Order Flow & Targets Analyzer</h1>
""", unsafe_allow_html=True)

# बिनेंस से लाइव बिटकॉइन डेटा फेच करने का फंक्शन
@st.cache_data(ttl=5)
def get_crypto_data():
    try:
        url = "https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                "price": float(data['lastPrice']),
                "high": float(data['highPrice']),
                "low": float(data['lowPrice']),
                "volume": float(data['volume']),
                "price_change": float(data['priceChangePercent'])
            }
    except Exception as e:
        pass
    return None

# मुख्य डैशबोर्ड लेआउट
placeholder = st.empty()

with placeholder.container():
    market_data = get_crypto_data()
    
    if market_data:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Live BTC Price", f"${market_data['price']:,.2f}", f"{market_data['price_change']:.2f}%")
        col2.metric("24h High", f"${market_data['high']:,.2f}")
        col3.metric("24h Low", f"${market_data['low']:,.2f}")
        col4.metric("24h Volume", f"{market_data['volume']:,.2f} BTC")
        
        st.success("लाइव डेटा सफलतापूर्वक लोड हो रहा है!")
        
        # सिमुलेटेड आर्डरफ्लो / डेप्थ विजुलाइजेशन चार्ट
        st.subheader("📊 Order Flow Depth & Pressure Analysis")
        
        # कुछ सैंपल आर्डरफ्लो लेवल्स ताकि चार्ट तुरंत शानदार दिखे
        chart_data = pd.DataFrame({
            'Price Level': [market_data['price'] - 100, market_data['price'] - 50, market_data['price'], market_data['price'] + 50, market_data['price'] + 100],
            'Buy Orders (Bid)': [120, 250, 400, 150, 80],
            'Sell Orders (Ask)': [90, 180, 350, 290, 210]
        })
        
        fig = go.Figure()
        fig.add_trace(go.Bar(y=chart_data['Price Level'], x=chart_data['Buy Orders (Bid)'], name='Bid Pressure (Buy)', orientation='h', marker_color='green'))
        fig.add_trace(go.Bar(y=chart_data['Price Level'], x=[-x for x in chart_data['Sell Orders (Ask)']], name='Ask Pressure (Sell)', orientation='h', marker_color='red'))
        
        fig.update_layout(barmode='overlay', title="Bid vs Ask Order Flow Distribution", xaxis_title="Volume", yaxis_title="Price ($)", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
        
    else:
        st.error("डेटा फेच करने में समस्या आ रही है। कृपया कुछ देर बाद रिफ्रेश करें।")

# ऑटो-रिफ्रेश काउंटर (हर 5 सेकंड में स्क्रीन अपडेट होगी)
time.sleep(5)
st.rerun()
