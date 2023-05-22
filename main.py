# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press Ctrl+F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

##################################################
# import modules

import os
import pandas as pd
import requests
# from tqdm import tqdm
import geopandas as gpd
from shapely.geometry import Polygon
import matplotlib.pyplot as plt
from pyproj import CRS
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns
from collections import Counter
import re

plt.rcParams['font.family'] = 'NanumGothic'
plt.rcParams['font.size'] = 12

# Set the max_columns option to None
pd.set_option('display.max_columns', None)


##################################################
# set working directory

cwd = os.getcwd()
# print(cwd)

base_path = "/Users/USER/PycharmProjects/genderSortingAcrossElementarySchoolInKorea"
path_engineered_data = os.path.join(base_path, r'engineered_data')

if not os.path.exists(path_engineered_data):
   os.makedirs(path_engineered_data)


# ##################################################
# number of birth, boy/girl ratio of korea
data = {
    'year': ['2010', '2011', '2012', '2013', '2014',
            '2015', '2016', '2017', '2018', '2019', '2020'],
    'sKoreaBirthTotal': [470171, 471265, 484550, 436455, 435435,
                   438420, 406243, 357771, 326822, 302676, 272337],
    'sKoreaBoyGirlRatio': [106.9, 105.7, 105.7, 105.3, 105.3,
                   105.3, 105.0, 106.3, 105.4, 105.5, 104.8]
}

korean_births_df = pd.DataFrame(data)
print(korean_births_df)

# korean_births_df['sKoreaBoy'] = korean_births_df['sKoreaBoyGirlRatio']/100 * korean_births_df['sKoreaBirthTotal']
# print(korean_births_df['sKoreaBoy'])

# korean_births_df['sKoreaBoyGirlRatio'] = [korean_births_df['sKoreaBoyGirlRatio']/(100 + korean_births_df['sKoreaBoyGirlRatio']) ] * 100
korean_births_df['sKoreaBoyGirlRatio'] = (korean_births_df['numberOfBoys'] / korean_births_df['numberOfGirls']) * 100

print(korean_births_df['sKoreaBoyGirlRatio'])


##################################################
# open files: seoul birth data
file_name = "data/seoulBirthData/출산순위별+출생_20230508155221.csv"
file_path = os.path.join(base_path, file_name)
df = pd.read_csv(file_path, encoding='utf-8', header=[0,1,2])

# print(df.head())

# Split the data into df1 and df2
df1 = df.iloc[:, :2]
df2 = df.iloc[:, 2:]

df2.columns = df2.columns.droplevel(level=1)

# Translate lower level headers
df2 = df2.rename(columns={'계': 'total', '남자': 'male', '여자': 'female'})

df2 = df2.drop(index=0)

# Get the upper header
upper_header = df2.columns.get_level_values(0)

# Get the lower header
lower_header = df2.columns.get_level_values(1)

# Get the year information
year_info = upper_header.str.split(" ").str[0]

# Add the year information to the lower header
new_lower_header = year_info + lower_header

# Assign the new header to the DataFrame
df2.columns = [upper_header, new_lower_header]

# drop upper header
df2.columns = df2.columns.droplevel(0)

# drop the first row
df1 = df1.iloc[1:]

# drop the first column
df1 = df1.iloc[:, 1:]
df1.columns = ['bySeoulDistrict']
df2 = df2.set_index(df1['bySeoulDistrict'])
df2.loc['SeoulTotal'] = df2.sum(axis=0)


total_cols = df2.filter(like='total').columns
df2_total = df2[total_cols]
seoul_total = df2.loc['SeoulTotal', total_cols]

male_cols = df2.filter(regex='^(?!.*female).*male$').columns
df2_male = df2[male_cols]
seoul_male = df2.loc['SeoulTotal', male_cols]

female_cols = df2.filter(like='female').columns
df2_female = df2[female_cols]
seoul_female = df2.loc['SeoulTotal', female_cols]

# reset index of each series
total = seoul_total.reset_index(drop=True)
male = seoul_male.reset_index(drop=True)
female = seoul_female.reset_index(drop=True)

# concatenate horizontally
dfSeoulBirth = pd.concat([total, male, female], axis=1)
dfSeoulBirth['year'] = range(2000, 2022)

dfSeoulBirth.columns = ['SeoulTotal', 'SeoulMaleTotal', 'SeoulFemaleTotal', 'year']

dfSeoulBirth = dfSeoulBirth.reindex(columns=['year', 'SeoulBirthTotal', 'SeoulBirthMale', 'SeoulBirthFemale'])

# convert the "year" column to a string type
dfSeoulBirth['year'] = dfSeoulBirth['year'].astype(str)

# remove the "년" string from the "year" column
dfSeoulBirth['year'] = dfSeoulBirth['year'].str.replace('년', '')

print(dfSeoulBirth)
