import streamlit as st
import plotly.express as px
import pandas as pd
import requests
from streamlit_autorefresh import st_autorefresh

# पेज की सेटिंग (चौड़ा लेआउट)
st.set_page_config(
    page_title="Order Flow Terminal - Dev 22",
    page_icon="📈",
    layout="wide"
)

# ---------------------------------------------------------
# ऑटो-रिफ्रेश सेटअप (हर 5 सेकंड यानी 5000 मिलीसेकंड में पेज रिफ्रेश होगा)
# ---------------------------------------------------------
st_autorefresh(interval=5000, limit=None, key="orderflow_autorefresh")

# ---------------------------------------------------------
# डेटा फेचिंग फंक्शन (बाइनेंस से लाइव डेटा लाने के लिए)
# ---------------------------------------------------------
@st.cache_data(ttl=3) # हर 3 सेकंड में नया डेटा कैश क्लियर करेगा
def fetch_binance_data():
    try:
        # बाइनेंस से बीटीसी टिकर प्राइस लेना
        ticker_res = requests.get("https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT", timeout=5).json()
        current_price = float(ticker_res.get('lastPrice', 67200))
        high_price = float(ticker_res.get('highPrice', 68100))
        low_price = float(ticker_res.get('lowPrice', 66500))
        volume = float(ticker_res.get('volume', 35420.50))
        
        # बाइनेंस से ऑर्डर बुक डेप्थ (Orderbook Depth) लेना
        depth_res = requests.get("https://api.binance.com/api/v3/depth?symbol=BTCUSDT&limit=7", timeout=5).json()
        bids = depth_res.get('bids', [])
        asks = depth_res.get('asks', [])
        
        return current_price, high_price, low_price, volume, bids, asks
    except Exception as e:
        # अगर इंटरनेट या API में दिक्कत हो, तो डिफ़ॉल्ट वैल्यू दिखाएगा ताकि ऐप क्रैश न हो
        return 67200.0, 68100.0, 66500.0, 35420.50, [], []

# डेटा लोड करें
price, high, low, vol, bids, asks = fetch_binance_data()

# ---------------------------------------------------------
# टॉप मेट्रिक्स (Top Metrics Header)
# ---------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="BTC Live Price", value=f"${price:,.2f}")
with col2:
    st.metric(label="24h High", value=f"${high:,.2f}")
with col3:
    st.metric(label="24h Low", value=f"${low:,.2f}")
with col4:
    st.metric(label="24h Volume", value=f"{vol:,.2f} BTC")

st.markdown("---")

# ---------------------------------------------------------
# चार्ट और ऑर्डर फ्लो सेक्शन
# ---------------------------------------------------------
st.subheader("📊 Order Flow Depth & Pressure Analysis")

# यदि बाइनेंस से बिड/आस्क का डेटा मिल गया है, तो उसे चार्ट में बदलें
if bids and asks:
    # डेटा को पांडास DataFrame में बदलना
    bids_df = pd.DataFrame(bids, columns=['Price', 'Volume'])
    bids_df['Price'] = bids_df['Price'].astype(float)
    bids_df['Volume'] = bids_df['Volume'].astype(float)
    bids_df['Type'] = 'Bid (Buy Pressure)'
    
    asks_df = pd.DataFrame(asks, columns=['Price', 'Volume'])
    asks_df['Price'] = asks_df['Price'].astype(float)
    asks_df['Volume'] = asks_df['Volume'].astype(float)
    asks_df['Type'] = 'Ask (Sell Pressure)'
    # सेल वॉल्यूम को नेगेटिव कर देते हैं ताकि दोनों तरफ बार चार्ट बंस सके
    asks_df['Volume'] = -asks_df['Volume'] 

    # दोनों को मर्ज करना
    chart_df = pd.concat([bids_df, asks_df])

    # Plotly से हॉरिजॉन्टल बार चार्ट बनाना
    fig = px.bar(
        chart_df,
        x='Volume',
        y='Price',
        color='Type',
        orientation='h',
        title='Bid vs Ask Order Flow Distribution',
        color_discrete_map={'Bid (Buy Pressure)': '#00CC96', 'Ask (Sell Pressure)': '#EF553B'}
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        xaxis_title="Volume",
        yaxis_title="Price ($)",
        yaxis=dict(autorange="reversed") # ऑर्डर बुक की तरह प्राइस ऊपर से नीचे अरेंज हो
    )

    st.plotly_chart(fig, use_container_width=True)
else:
    # डमी चार्ट यदि API से तुरंत डेटा न मिले
    st.warning("लाइव डेटा लोड हो रहा है...")
