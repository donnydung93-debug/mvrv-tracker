import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests

print("正在拉取最新 BTC 链上与价格数据...")
url = "https://community-api.coinmetrics.io/v4/timeseries/asset-metrics?assets=btc&metrics=CapRealUSD,CapMrktCurUSD,PriceUSD&frequency=1d&pretty=true"
response = requests.get(url).json()

data = response['data']
df = pd.DataFrame(data)

df['time'] = pd.to_datetime(df['time'])
df['CapRealUSD'] = df['CapRealUSD'].astype(float)
df['CapMrktCurUSD'] = df['CapMrktCurUSD'].astype(float)
df['PriceUSD'] = df['PriceUSD'].astype(float)

# 计算 MVRV Z-Score
df['MVRV_Diff'] = df['CapMrktCurUSD'] - df['CapRealUSD']
df['MarketCap_Std'] = df['CapMrktCurUSD'].expanding().std() 
df['MVRV_Z_Score'] = df['MVRV_Diff'] / df['MarketCap_Std']

# 绘制双轴交互图表
fig = make_subplots(specs=[[{"secondary_y": True}]])

fig.add_trace(
    go.Scatter(x=df['time'], y=df['MVRV_Z_Score'], name="Bitcoin MVRV Z-Score (L)", line=dict(color='#00A3E0', width=1.5)),
    secondary_y=False,
)

fig.add_trace(
    go.Scatter(x=df['time'], y=df['PriceUSD'], name="Bitcoin / USD (R)", line=dict(color='#F2A900', width=1.5)),
    secondary_y=True,
)

fig.update_layout(
    title_text="Bitcoin - MVRV Z-Score (每日自动更新)",
    template="plotly_white",
    hovermode="x unified",
    legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
)

fig.update_xaxes(title_text="Date")
fig.update_yaxes(title_text="Number (Z-Score)", secondary_y=False, zeroline=True, zerolinedrawcolor='gray')
fig.update_yaxes(title_text="Number, USD", type="log", secondary_y=True)

fig.write_html("index.html")
print("图表更新成功！")
