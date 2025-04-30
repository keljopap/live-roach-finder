import pandas as pd
# import numpy as np

# Some scratch code from tutorial: https://www.youtube.com/watch?v=_Eb0utIRdkw
# https://www.kaggle.com/code/robikscube/pandas-introduction-youtube-tutorial/comments?scriptVersionId=94752062

mydata = ['Boat', 'Car', 'Bike', 'Truck']
mydata2 = [1, 55, 99, 43]
mydfdata = [('Boat', 1), ('Car', 55), ('Bike', 99), ('Truck', 43)]

# myseries1 = pd.Series(mydata)
# print(myseries1)
# myseries2 = pd.Series(mydata2)
# print(myseries2)
mydf = pd.DataFrame(mydfdata, columns=['thing', 'count'])
print(mydf)
df = pd.read_csv('./input/MrBeast_youtube_stats.csv')

# print("HEAD: ")
# print(df.head(3))
# print("\n")

# print("COLUMNS: ")
# print(df.columns)
# print("\n")

print("DATA TYPES: ")
print(df.dtypes)
print("\n")

print("DESCRIBE: ")
print(df.describe())
print("\n")

print("VIEW COUNT: ")
print(df['viewCount'])
print("\n")

print("PRINT idx 4: ")
print(df.loc[4])
print("\n")

print("PRINT row with id nM89Wl03Q4g: ")
df = df.set_index('id').drop_duplicates()
print(df.loc['nM89Wl03Q4g'])
print("\n")

print("DESCRIBE: ")
print(df['viewCount'].describe())
print("\n")

print("VIEW SUBSET OF COLUMNS: ")
print(df.shape)
df = df[[
    'title',
    'description',
    'publishTime',
    'duration_seconds',
    'viewCount',
    'likeCount',
    'commentCount'
]]
print(df)
print(df.shape)
print("\n")
# print("INFO: ")
# print(df.info())
# print("\n")

# Clean the DataFrame
df = df.loc[~df['viewCount'].isna()]
df = df.loc[~df['likeCount'].isna()]
df = df.loc[~df['commentCount'].isna()]

# Convert columns to appropriate data types
df['viewCount'] = df['viewCount'].astype('int')
df['likeCount'] = df['likeCount'].astype('int')
df['commentCount'] = df['commentCount'].astype('int')
df['publishTime'] = pd.to_datetime(df['publishTime'])

# Subset the DataFrame and sort it by a column
df_subset1 = df.loc[df['viewCount'] > 1_000_000]
print("SUBSET: ")
print(df_subset1.shape)
print(df.query('viewCount > 1_000_000').sort_values('viewCount', ascending=False)[['title', 'viewCount', 'publishTime']])

# Create a new column from existing columns
df['like_to_view_ratio'] = df['likeCount'] / df['viewCount']
df['comment_to_view_ratio'] = df['commentCount'] / df['viewCount']
print(df[['title', 'like_to_view_ratio']])

# Append a row to the DataFrame
df_to_append = df.tail(1)
df_concat = pd.concat([df, df_to_append])
print(df_concat.tail(3))

# Create a histogram of a column (needs matplotlib)
# print(df['viewCount'].plot(kind='hist'))

# Save output to CSV
df.to_csv('./output/MrBeast_youtube_stats_cleaned.csv', index=False)