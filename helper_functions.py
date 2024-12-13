import os
import re
import time
import tkinter as tk
from tkinter import filedialog

info_tag = {
    'inovice_number',
    'inovice_date',
    'seller_info',
    'item_name',
    'item_type',
    'item_unit',
    'item_number',
    'item_uniprice',
    'item_price',
    'item_taxrate',
    'item_tax',
    'total_price',
    'total_tax',
    'total_price_and_tax'
}

D_PIX = 2  # increase box boundaries

def page_layout_init():
    page_layout = {}
    for it in info_tag:
        ld_box = it + '_bx'
        page_layout[ld_box] = [None] * 4  # [x0, y0, x1, y1]
    return page_layout

def get_pdf_paths(pdf_dir):
    ls_dir = os.listdir(pdf_dir)
    paths = []
    for f in ls_dir:
        pdf_path = os.path.join(pdf_dir, f)
        if pdf_path.endswith('.pdf'):
            paths.append(pdf_path)
    return paths

def is_valid_date(strdate):
    try:
        time.strptime(strdate, '%Y年%m月%d日')
        return True
    except:
        return False

def is_inside_box(inner_box, outer_box):
    if inner_box[0] >= outer_box[0] and \
        inner_box[1] >= outer_box[1] and\
        inner_box[2] <= outer_box[2] and\
        inner_box[3] <= outer_box[3]:
        return True
    return False

def collect_items_info(inovice_dict, item_start_num):
    items_list = []
    item_count = item_start_num
    for _it_line in inovice_dict['items']:
        _it = {}
        _it['编号'] = item_count
        _it['发票号码'] = inovice_dict['inovice_number']
        _it['开票日期'] = inovice_dict['inovice_date']
        _it['销售方名称'] = inovice_dict['seller_name']
        _it['销售方编号'] = inovice_dict['seller_code']
        _it['项目名称'] = _it_line[0]
        _it['规格型号'] = _it_line[1]
        _it['单位'] = _it_line[2]
        _it['数量'] = _it_line[3]
        _it['单价'] = _it_line[4]
        _it['金额（不含税）'] = _it_line[5]
        _it['税率'] = _it_line[6]
        _it['税额'] = _it_line[7]

        items_list.append(_it)
        item_count += 1
    return items_list


class PopUp():
    def __init__(self) -> None:
        self.folder_path = ''
        self.root = tk.Tk()
        self.folder_label = tk.Label(self.root, text='Please select the folder containing your PDF inovices.')
        self.folder_label.pack(padx=5, pady=5)

    def browse_folder(self):
        self.folder_path = filedialog.askdirectory()
        print(self.folder_path)
        if self.folder_path:
            self.folder_label.config(text=self.folder_path)

    def pop_up(self):
        self.root.title('Upload folder')
        self.root.geometry("300x150")
        browse_button = tk.Button(self.root, text='...', command=self.browse_folder)
        browse_button.pack(padx=5, pady=5)
        upload_button = tk.Button(self.root, text='Confirm', command=self.root.destroy)
        upload_button.pack(padx=5, pady=5)
        self.root.mainloop()
        return self.folder_path