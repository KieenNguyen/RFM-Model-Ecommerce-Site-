#!/usr/bin/env python
# coding: utf-8

# #Note dataframe: 
# - data: dataset ban đầu 
# - data2: dataset ban đầu có lọc trùng sale
# - promsing: dataset chứa group of promising customer 
# - prominsing_unique: dataset chứa group of promising customer có lọc sale
# - fre,re,mon: dataset chứa frequency, recency, monetary score
# - rfm: dataset frm
# - payment: dataset có cluster + danh sách khách hàng+ sản phẩm,...
# - all_in_one: Dataset có đầy đủ tất cả thông tin

# In[1]:


import numpy as np
import pandas as pd
import collections
import matplotlib.pyplot as plt


# In[2]:


data = pd.read_csv('Ecommerce Dataset.xlsx - Ecommerce Data.csv')
data


# <H2> Data cleaning:

# In[3]:


data.info()


# In[4]:


data['status'].unique()


# In[5]:


#Check unique key: 
data['item_id'].drop_duplicates().count()
#item_id là unique key


# In[6]:


data.drop_duplicates()


# <H3> Group status for easier analysis:

# In[7]:


complete = data['status'].isin(['complete','received','cod','paid','closed','exchange'])
canceled = data['status'].isin(['canceled','order_refunded','refund','fraud'])
pending = data['status'].isin(['payment_review','pending','processing','holded','pending_paypal'])


# In[8]:


def payment_check(row): 
    if row['status'] =='complete': 
        return 'completed'
    elif row['status'] == 'received':
        return 'completed'
    elif row['status'] == 'received':
        return 'completed'
    elif row['status'] == 'paid':
        return 'completed'
    elif row['status'] == 'closed':
        return 'completed'
    elif row['status'] == 'exchange': 
        return 'completed'
    elif row['status'] == 'canceled':
        return 'canceled'
    elif row['status'] == 'order_refunded':
        return 'canceled'
    elif row['status'] == 'refund':
        return 'canceled'
    elif row['status'] == 'fraud': 
        return 'canceled'
    else: return 'pending'


# In[9]:


data.apply(payment_check, axis=1)


# In[10]:


data['new_payment_status'] = data.apply(payment_check, axis=1)
data


# <H1> I. RFM analysis:

# <H3> 1.Recency: 

# In[11]:


data.sort_values( by = 'Customer ID', ascending =True)


# In[12]:


#Day max in this research: 
data['created_at'] = pd.to_datetime(data['created_at'])
day_max = pd.to_datetime(data['created_at'].max())
day_max


# In[13]:


#Day since last order of every customer: 
recen = data.groupby('Customer ID')['created_at'].max().to_frame().reset_index().rename(columns = {'created_at':'last_day'})
recen['last_day'] = pd.to_datetime(recen['last_day']) 
recen['recen_day'] = day_max - recen['last_day']
recen


# In[14]:


#Recency score: 
recen['recency_score'] = recen['recen_day'].rank(pct=True, ascending = True)*10
recen['recency_score'] = recen['recency_score'].astype(int)
recen


# In[15]:


recen.loc[recen['recency_score']==10]


# <H3> 2.Frequency

# In[16]:


data2=data


# In[17]:


data2 = data2[~data2['increment_id'].duplicated()]
data2


# In[18]:


#Điểm frequency đếm trên số lần đặt hàng theo từng customer ID:
fre =data2.groupby('Customer ID')['increment_id'].count().to_frame().reset_index().rename(columns ={'increment_id':'count of others'})
fre


# In[19]:


fre['frequency_score'] = fre['count of others'].rank(pct=True, ascending = True)*10
fre['frequency_score'] = fre['frequency_score'].astype(int)
fre


# In[20]:


fre.loc[fre['frequency_score']==10]


# <H3> 3.Monetary:

# In[21]:


mon = data2.groupby('Customer ID')['grand_total'].sum().to_frame().reset_index()
mon


# In[22]:


mon['monetary_score'] = mon['grand_total'].rank(pct=True)*10
mon['monetary_score'] = mon['monetary_score'].astype(int)
mon


# In[23]:


mon.loc[mon['monetary_score'] == 10]


# In[24]:


data2.sort_values(by='Customer ID', ascending=False)


# <H3> RFM Score and Customer Cluster:

# In[25]:


#merge RFM table together:
rfm = pd.merge(recen, mon, how='inner',on='Customer ID')
rfm = pd.merge(rfm,fre, how='inner', on='Customer ID')
rfm['total_score'] = rfm['recency_score'] +rfm['monetary_score'] + rfm['frequency_score'] 
rfm.drop(columns ={'last_day','recen_day','grand_total','count of others'})


# In[26]:


rfm['cluster'] =" "


# In[27]:


#customer clustering: 
for i in rfm.index: 
    if rfm['total_score'][i] == 27: 
        rfm['cluster'][i] = 'Champion'
    elif rfm['total_score'][i] >= 21: 
        rfm['cluster'][i] ='Loyal Customer'
    elif rfm['total_score'][i] >= 16: 
        rfm['cluster'][i] ='Promising Customer'
    elif rfm['total_score'][i] >= 4: 
        rfm['cluster'][i] = 'At risk'
    else: rfm['cluster'][i] = 'Lost customer'
rfm


# In[28]:


#Save rfm file to excel: 
#rfm.to_excel('rfm.xlsx', index =False)


# <H3> Percantage of each cluster:

# In[29]:


#Count number of customer in each cluster: 
percen = rfm.groupby('cluster')['Customer ID'].count().to_frame().reset_index().rename(columns={'Customer ID':'Count of Customer'})
#Draw chart to have the percantage: 
plt.pie(percen['Count of Customer'],autopct='%1.2f%%', labels = percen['cluster'])
plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15))
plt.title('Percent of each cluster')
plt.show()


# In[30]:


percen


# <H3> RFM score in each cluster:

# In[31]:


#Calculate the score
score = rfm.groupby('cluster')['total_score'].mean().to_frame().reset_index().rename(columns ={'total_score':'average score'})
#Draw table of the score:
plt.bar(score['cluster'],score['average score'], align ='center')
plt.xticks(rotation =60)
plt.show()


# In[32]:


pd.pivot_table(rfm, index='cluster', values = ['total_score','frequency_score','monetary_score','recency_score'])


# <H1> II.Analysis to find Insight: 

# <H3> What is the payment method of each cluster?

# In[33]:


data


# In[34]:


#marge rfm and data to have the cluster and payment method in the same dataset:
payment = pd.merge(data, rfm, how ='inner', on='Customer ID')
payment = payment.drop(['sku','sales_commission_code','last_day','grand_total_y','Working Date','BI Status','Year','Month',
                       'Customer Since','M-Y'],axis=1)
payment


# In[35]:


pivot_payment =pd.pivot_table(payment, values='Customer ID', index ='payment_method', columns = 'cluster', aggfunc='count').reset_index()
pivot_payment


# In[36]:


reve = rfm.groupby('cluster')['grand_total'].sum().to_frame().reset_index()
reve
plt.bar(reve['cluster'],reve['grand_total'])
plt.xticks(rotation =60)
plt.title('revenue from each cluster')
plt.show()


# <H2> Analyse Promising Cluster: 

# In[37]:


rfm


# In[38]:


#count number of promising customers: 
print(percen)
#Visua: 
plt.bar(percen['cluster'],percen['Count of Customer'])
plt.xticks(rotation = 60) 
plt.show()


# In[39]:


#Profit bring to the comapny: 
print(reve)
print('Percent of revenue from Promising customer:',reve['grand_total'].      loc[(reve['cluster'] =='Promising Customer')]/(reve['grand_total'].sum())*100)
#visuli:
reve = rfm.groupby('cluster')['grand_total'].sum().to_frame().reset_index()
plt.bar(reve['cluster'],reve['grand_total'])
plt.xticks(rotation =60)
plt.title('revenue from each cluster')
plt.show()


# <H3> Most favorite categories: 

# In[40]:


#Merge "RFM" and "data" dataframe to have the category and cluster in one dataframe: 
all_in_one = pd.merge(data, rfm, how ='left', on = "Customer ID")
all_in_one = all_in_one.drop(['sales_commission_code','Working Date','BI Status','Year',                            'Customer Since','M-Y','last_day','recen_day','grand_total_y'], axis=1)   
all_in_one


# <H3> Calculate AOV (average order value): 

# In[41]:


all_in_one_uni = all_in_one[~all_in_one['increment_id'].duplicated()]
all_in_one_uni


# In[42]:


#Sale amount: 
all_in_one['sale amount']=all_in_one.price*all_in_one.qty_ordered


# In[43]:


print('revenue của các cluster')
all_in_one_uni.groupby('cluster')['grand_total_x'].sum()


# In[44]:


#save file all_in_one:
#all_in_one.to_excel('all-in_one.xlsx', index =False)


# In[45]:


#Create promising data: 
promising = all_in_one


# In[46]:


#Phần trăm huỷ đơn: 
payment_status = promising.groupby('new_payment_status')['Customer ID'].count().to_frame().reset_index()
print(payment_status)
#Visualize: 
plt.pie(payment_status['Customer ID'], autopct='%1.2f%%', labels = payment_status['new_payment_status'])
plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15))
plt.title('Tỉ lệ huỷ đơn')
plt.show()


# In[47]:


canceled


# In[49]:


#Check lượng đơn huỷ đến từ đâu: 
canceled=promising.loc[promising['new_payment_status'] == 'canceled']
canceled_count=canceled.groupby('category_name_1')['item_id'].count().to_frame().reset_index()
canceled_count
#visualize: 
plt.pie(canceled_count['item_id'], labels = canceled_count['category_name_1'])
plt.show()


# In[50]:


promising


# In[51]:


pd.pivot_table(promising, index='category_name_1', values='new_payment_status', aggfunc='count')


# In[52]:


#payment method: 
method = promising.groupby('payment_method')['Customer ID'].count().to_frame().reset_index()

print(method)
#visualize: 
plt.bar(method['payment_method'],method['Customer ID'])
plt.title('Payment Method')
plt.xticks(rotation = 60)
plt.show()


# In[ ]:


#Save promising file to Excel: 
#promising.to_excel('promising.xlsx')


# In[53]:


#Boxplot of Promising customer: 
re=rfm['recency_score']
fe=rfm['frequency_score']
mo= rfm['monetary_score']
columns = [re,fe,mo]
fig, ax = plt.subplots()
ax.boxplot(columns)
plt.xticks([1,2,3],['recency_score','frequency_score','monetary_score'])
plt.show()


# In[54]:


#Create dataframe contains only promising customer: 
promising = promising.loc[(promising['cluster']=='Promising Customer')]
promising = promising.rename(columns ={'grand_total_x':'grand_total'})
promising = promising.drop(['cluster'],axis =1)
promising  


# In[55]:


promising['category_name_1'].unique()


# In[56]:


#filter missing data:
promising.dropna()
#Drop \\N: 
promising=promising.drop(promising.loc[(promising['category_name_1']=='\\N')].index, axis=0)


# In[57]:


#Create dataframe with no duplicate incremental_id: data2 = data2[~data2['increment_id'].duplicated()]
promising_unique = promising
promising_unique= promising_unique[~promising_unique['increment_id'].duplicated()]
promising_unique


# In[58]:


#What product Promising custermers buy the most?:
pivot_promising = promising.groupby('category_name_1')['item_id'].count().to_frame().reset_index().rename(columns={'item_id':'count item'})
print(pivot_promising)
#Visualize: 
from matplotlib.pyplot import figure
figure(figsize=(8, 6), dpi=80)
plt.bar(pivot_promising['category_name_1'],pivot_promising['count item'])
plt.xticks(rotation =60)
plt.title('Number of Orders')
plt.show()


# In[59]:


#Which category generate the most profit? 
pivot_u_pro = promising_unique.groupby('category_name_1')['grand_total'].sum().to_frame().reset_index()
print(pivot_u_pro)
#Visualize: 
figure(figsize=(8, 6), dpi=80)
plt.bar(pivot_u_pro['category_name_1'],pivot_u_pro['grand_total'])
plt.xticks(rotation =60)
plt.title('Profit')
plt.show()


# In[60]:


#Add Discount amount column into the dataframe: 
pivot_u_pro = pd.merge(promising_unique.groupby('category_name_1')['discount_amount'].sum().to_frame().reset_index(),pivot_u_pro, how ='inner',on='category_name_1')
print(pivot_u_pro)
#Visualize number of discount: 
figure(figsize=(8, 6), dpi=80)
plt.bar(pivot_u_pro['category_name_1'],pivot_u_pro['discount_amount'])
plt.xticks(rotation =60)
plt.title('Discount Amount')
plt.show()


# In[61]:


#Lượng đơn orders theo các tháng: 
order_month = promising_unique.groupby('Month')['increment_id'].count().to_frame().reset_index()
print(order_month)
#visualize: 
plt.plot(order_month['Month'], order_month['increment_id'])
plt.title('Số đơn order qua các tháng')
plt.show()


# In[62]:


#lượng order theo các tháng của cả công ty: 
monthly_order = data2.groupby('Month')['increment_id'].count().to_frame().reset_index()
#visualize: 
plt.plot(monthly_order['Month'], monthly_order['increment_id'])
plt.title('Số đơn order qua các tháng của cả công ty')
plt.show()


# <H1> Loyal Customer: 

# In[63]:


loyal = pd.merge(data, rfm, how ='left', on = "Customer ID")
loyal = loyal.loc[loyal['cluster'] == 'Loyal Customer']
#Lọc trùng:
loyal_unique = loyal
loyal_unique= loyal_unique[~loyal_unique['increment_id'].duplicated()]
loyal_unique
loyal


# In[64]:


#lượng order theo các tháng của Loyal Customer: 
loyal_order = loyal_unique.groupby('Month')['increment_id'].count().to_frame().reset_index()
#visualize: 
plt.plot(loyal_order['Month'], loyal_order['increment_id'])
plt.title('Số đơn order qua các tháng của loyal')
plt.show()


# In[65]:


#Check huỷ đơn: 
number_can_loyal=all_in_one.loc[all_in_one['cluster'] == 'Loyal Customer']
number_can_loyal2 = number_can_loyal.loc[number_can_loyal['new_payment_status'] == 'canceled']
number_can_loyal2 =number_can_loyal2.groupby('qty_ordered')['item_id'].count().to_frame().reset_index().rename(columns={'item_id':'count of canceled'})
#visualize: 
plt.bar(number_can_loyal2['qty_ordered'],number_can_loyal2['count of canceled'], width = 2)
plt.ylabel('count of canceled')
plt.show()


# In[67]:


number_can_loyal2.to_excel('count.xlsx')

