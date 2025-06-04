import os
import ast
import pandas as pd

from Invoice_process import inovice_folder

inovice_excel_folder = inovice_folder
excel_file_path = inovice_folder + '/collective_inovice_info.xlsx'

if not excel_file_path:
    print('Inovice not preprocessed! End now.')
    exit(0)

inovice_data = pd.read_excel(excel_file_path)
info_needed = inovice_data[['编号', '销售方名称', '项目名称', '单价', '数量', '金额（不含税）', '税额']]

data_list = []
for _, it in info_needed.iterrows():
    one_it = {}
    one_it['编号'] = it['编号']
    one_it['物品名称'] = it['项目名称']
    one_it['品牌'] = it['销售方名称']
    if pd.isna(it['数量']):
        it['数量'] = 1
    one_it['数量'] = str(int(it['数量']))
    if pd.isna(it['单价']):
        it['单价'] = it['数量'] * round(it['金额（不含税）'] + it['税额'], 2)
    one_it['单价'] = str(it['单价'])
    one_it['总价'] = '{:.2f}'.format(round(it['金额（不含税）'] + it['税额'], 2))

    if eval(one_it['总价']) > 0:
        if eval(one_it['总价']) < eval(one_it['单价']) * eval(one_it['数量']):
            print('Inovice item data may be wrong!')
    
    data_list.append(one_it)

df = pd.DataFrame(data_list)
df.to_excel(inovice_folder + '/hkust_output_excel.xlsx', index=False)
