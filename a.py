import streamlit as st
import urllib.request
import json
import time

# पेज की सेटिंग
st.set_page_config(page_title="Dev 22 Live Market Analyzer", page_icon="📈", layout="centered")

st.title("🚀 Dev 22 - Live Order Flow & Targets Analyzer")
st.markdown("---")

# डेटा फेच करने का फंक्शन
def get_market_data():
    depth_url = "https://api.binance.com/api/v3/depth?symbol=BTCUSDT&limit=50"
    price_url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
    
    try:
        # लाइव प्राइस
        req_p = urllib.request.Request(price_url, headers={'User-Agent': 'Mozilla/5.0'})
        price_data = json.loads(urllib.request.urlopen(req_p).read().decode())
        price = float(price_data['price'])
        
        # आर्डर बुक फुटप्रिंट्स (Bids & Asks)
        req_d = urllib.request.Request(depth_url, headers={'User-Agent': 'Mozilla/5.0'})
        depth_data = json.loads(urllib.request.urlopen(req_d).read().decode())
        
        bids = depth_data['bids']
        asks = depth_data['asks']
        
        total_bid_qty = sum([float(item[1]) for item in bids])
        total_ask_qty = sum([float(item[1]) for item in asks])
        
        return price, total_bid_qty, total_ask_qty
    except Exception as e:
        st.error(f"डेटा फेच करने में एरर: {e}")
        return None, None, None

# डैशबोर्ड लेआउट
price, bid_qty, ask_qty = get_market_data()

if price:
    col1, col2 = st.columns(2)
    col1.metric("वर्तमान लाइव प्राइस (BTC)", f"${price:,.2f}")
    
    # फुटप्रिंट और प्रेशर चेक
    if bid_qty > ask_qty * 1.15:
        signal = "STRONG BUY (બाइंग प्रेशर हावी)"
        color = "green"
        entry = price
        sl = price * 0.992
        target = price * 1.018
    elif ask_qty > bid_qty * 1.15:
        signal = "STRONG SELL (सेलिंग दीवार हावी)"
        color = "red"
        entry = price
        sl = price * 1.008
        target = price * 0.982
    else:
        signal = "NEUTRAL / SIDEWAYS (इंतज़ार करें)"
        color = "orange"
        entry = price
        sl = price * 0.995
        target = price * 1.005

    st.markdown(f"### सिग्नल: :{color}[{signal}]")
    
    st.markdown("### 📊 आर्डर बुक फुटप्रिंट्स (Volume)")
    st.info(f"कुल बाइंग वॉल्यूम (Bids): {bid_qty:.2f} BTC | कुल सेलिंग वॉल्यूम (Asks): {ask_qty:.2f} BTC")
    
    st.markdown("### 🎯 ट्रेड सेटअप (एंट्री, स्टॉपलॉस और टारगेट्स)")
    st.success(f"**सजेशन एंट्री:** ${entry:,.2f}")
    st.warning(f"**स्टॉपलॉस (Stop Loss):** ${sl:,.2f}")
    st.error(f"**टारगेट (Target):** ${target:,.2f}")
    
    if st.button("🔄 लाइव डेटा रिफ्रेश करें"):
        st.rerun()
else:
    st.warning("लाइव डेटा लोड हो रहा है...")
