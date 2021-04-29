import datetime as dt
import pandas as pd
pd.set_option('display.max_columns', None)

df_ = pd.read_excel("dataset/online_retail_II.xlsx",sheet_name="Year 2010-2011")
df=df_.copy() #df'i yedekliyoruz
df.head()

# essiz urun sayisi:
df["Description"].nunique()
# Bizden ürün alan ülke sayısı:
df["Country"].nunique()

## hangi urunden kacar tane var:
df["Description"].value_counts()

## en cok siparis edilen urun:
df.groupby("Description").agg({"Quantity":"sum"}).sort_values("Quantity",ascending=False).head(3)

## toplam kac fatura kesilmiştir:
df["Invoice"].nunique()

# tek alışverişte en az üründe en çok ödemeyi yapanlar:
df.groupby("Invoice").agg({"Quantity":"sum","Total_Price":"sum"}).sort_values(["Quantity","Total_Price"],ascending=[True,False])

# fatura basina ortalama kac para kazanilmistir?
# İade ürünleri çıkardıktan sonra toplam price hesaplanacak.
df=df[~df["Invoice"].str.contains("C",na=False)]
df["TotalPrice"]=df["Quantity"]*df["Price"]

#en çok alışveriş yapılmış fatura nolar
df.groupby("Invoice").agg({"TotalPrice":"sum"}).sort_values("TotalPrice",ascending=False).head(10)

# en pahalı ürünler hangileri?
df.sort_values("Price",ascending=False).head(50)

# hangi ulkeden kac siparis geldi?
df["Country"].value_counts()

# hangi ulke ne kadar kazandırdı?
df.groupby("Country").agg({"TotalPrice":"sum"})

df.isnull().sum()
df.dropna(inplace=True)

df.describe([0.01, 0.05, 0.10, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99]).T

#   Calculation RFM Metrics

df["InvoiceDate"].max()
today_date=dt.datetime(2011,12,11)

rfm=df.groupby('Customer ID').agg({'InvoiceDate':lambda date:(today_date-date.max()).days,'Invoice':lambda num:len(num),'TotalPrice':lambda TotalPrice: TotalPrice.sum()})

rfm.columns=['Recency','Frequency','Monetary']

rfm=rfm[(rfm["Monetary"]>0) & (rfm["Frequency"]>0)]

## RFM Scores Calculation

rfm["RecencyScore"]=pd.qcut(rfm['Recency'],5,labels=[5,4,3,2,1])
rfm["FrequencyScore"]=pd.qcut(rfm['Frequency'],5,labels=[1,2,3,4,5])
rfm["MonetaryScore"]=pd.qcut(rfm['Monetary'],5,labels=[1,2,3,4,5])

rfm.head()
rfm["RFM_SCORE"]=(rfm['RecencyScore'].astype(str)+rfm['FrequencyScore'].astype(str)+rfm['MonetaryScore'].astype(str))

############################################
# Müşterileri segmentlere ayırıyoruz
############################################

seg_map={
    r'[1-2][1-2]':'Hibernating',
    r'[1-2][3-4]':'At_Risk',
    r'[1-2]5':'Cant_Loose',
    r'3[1-2]':'About_to_Sleep',
    r'33':'Need_Attention',
    r'[3-4][4-5]':'Loyal_Customers',
    r'41':'Promissing',
    r'51':'New_Customers',
    r'[4-5][2-3]':'Potential_Loyalists',
    r'5[4-5]':'Champions'
}
rfm['Segment']=rfm['RecencyScore'].astype(str)+rfm['FrequencyScore'].astype(str)
rfm['Segment']=rfm['Segment'].replace(seg_map,regex=True)
rfm[["Segment","Recency","Frequency","Monetary"]].groupby("Segment").agg(["mean","count"])
rfm["Segment"].value_counts()

rfm.groupby("Segment").agg({"Monetary":"sum"}).sort_values("Monetary",ascending=False)

############################################
# "Loyal Customers" sınıfına ait customer ID'leri seçerek excel çıktısını alarak pazarlama departmanına bir aksiyon kararı almaları için iletebiliriz
############################################

new_df=pd.DataFrame()
new_df["Need_Attention"]=rfm[rfm["Segment"]=="Loyal_Customers"].index
new_df.to_excel("Loyal_Customers.xlsx")


