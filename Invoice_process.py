import pandas as pd

from helper_functions import *
from Single_inovice_extract import extract_inovice_info

inovice_folder = 'C:inovices/'

pdf_paths = get_pdf_paths(inovice_folder)

item_count = 0
all_items = []
for _pdf in pdf_paths:
    ino_info = extract_inovice_info(_pdf)
    _items = collect_items_info(ino_info, item_count + 1)
    all_items.extend(_items)
    item_count = all_items[-1]['编号']

data_frame = pd.DataFrame(all_items)
data_frame.to_excel(inovice_folder + '/collective_inovice_info.xlsx', index=False)