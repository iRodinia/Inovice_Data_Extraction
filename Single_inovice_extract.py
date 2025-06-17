from helper_functions import *

from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar

def fix_unstructured_layout(layout_dict):  # here we deal with unstructured pdfs
    if layout_dict['total_price_bx'][0] == None:
        layout_dict['total_price_bx'][0] = layout_dict['item_price_bx'][0]
    if layout_dict['total_price_bx'][1] == None:
        layout_dict['total_price_bx'][1] = layout_dict['item_price_bx'][1] - 12*D_PIX
    if layout_dict['total_price_bx'][3] == None:
        layout_dict['total_price_bx'][3] = layout_dict['item_taxrate_bx'][1] + D_PIX
    
    if layout_dict['total_tax_bx'][1] == None:
        layout_dict['total_tax_bx'][1] = layout_dict['item_price_bx'][1] - 12*D_PIX
    if layout_dict['total_tax_bx'][2] == None:
        layout_dict['total_tax_bx'][2] = layout_dict['item_tax_bx'][1]
    if layout_dict['total_tax_bx'][3] == None:
        layout_dict['total_tax_bx'][3] = layout_dict['item_tax_bx'][1] + D_PIX
    
    if layout_dict['total_price_and_tax_bx'][3] == None and layout_dict['total_price_and_tax_bx'][1] != None:
        layout_dict['total_price_and_tax_bx'][3] = layout_dict['total_price_and_tax_bx'][1] + 12*D_PIX


def extract_inovice_info(fpath):
    if not os.path.exists(fpath):
        print('Invalid inovice path: ' + fpath)
        exit(-1)

    pdf_file = extract_pages(fpath)

    pages_layout = []
    for page in pdf_file:
        _layout = page_layout_init()
        multi_pages = False
        for element in page:
            if isinstance(element, LTTextContainer):
                ele_text = element.get_text()
                ele_text_no_space = ele_text.replace(' ', '')

                if '发票号码' in ele_text_no_space or '发票号码' in ele_text_no_space:
                    _layout['inovice_number_bx'] = [element.x0, element.y0-D_PIX, page.x1, element.y1+D_PIX]
                    continue

                if '开票日期' in ele_text_no_space or '开票日期' in ele_text_no_space:
                    _layout['inovice_date_bx'] = [element.x0, element.y0-D_PIX, page.x1, element.y1+D_PIX]
                    continue

                if '销\n售\n方\n信\n息' in ele_text:
                    _layout['seller_info_bx'] = [element.x0, element.y0-D_PIX, page.x1, element.y1+D_PIX]
                    continue

                if '规格型号' in ele_text or '规格型号' in ele_text_no_space:
                    for text_line in element:
                        lin_text = text_line.get_text()
                        if '规格型号' in lin_text:
                            _layout['item_name_bx'][0] = page.x0
                            _layout['item_name_bx'][2:4] = [text_line.x0, text_line.y0+D_PIX]
                            _layout['item_type_bx'][0] = text_line.x0-D_PIX
                            break

                if '单  位' in ele_text or '单位\n' in ele_text_no_space:
                    for text_line in element:
                        lin_text = text_line.get_text()
                        lin_text_no_space = lin_text.replace(' ', '')
                        if '单  位' in lin_text or '单位\n' in lin_text_no_space:
                            _layout['item_type_bx'][2:4] = [text_line.x0, text_line.y0+D_PIX]
                            _layout['item_unit_bx'][0] = text_line.x0-D_PIX
                            _layout['item_number_bx'][0] = text_line.x1+D_PIX
                            break

                if '数  量' in ele_text or '数量\n' in ele_text_no_space:
                    for text_line in element:
                        lin_text = text_line.get_text()
                        lin_text_no_space = lin_text.replace(' ', '')
                        if '数  量' in lin_text or '数量\n' in lin_text_no_space:
                            _layout['item_unit_bx'][2:4] = [text_line.x0, text_line.y0+D_PIX]
                            _layout['item_number_bx'][2:4] = [text_line.x1+D_PIX, text_line.y0+D_PIX]
                            _layout['item_uniprice_bx'][0] = text_line.x1
                            break

                if '单  价' in ele_text or '单价\n' in ele_text_no_space:
                    for text_line in element:
                        lin_text = text_line.get_text()
                        lin_text_no_space = lin_text.replace(' ', '')
                        if '单  价' in lin_text or '单价\n' in lin_text_no_space:
                            _layout['item_uniprice_bx'][2:4] = [text_line.x1+D_PIX, text_line.y0+D_PIX]
                            _layout['item_price_bx'][0] = text_line.x1
                            break

                if '金  额' in ele_text or '金额\n' in ele_text_no_space or '金额税率/征收率' in ele_text_no_space:
                    for text_line in element:
                        lin_text = text_line.get_text()
                        lin_text_no_space = lin_text.replace(' ', '')
                        if '金  额' in lin_text or '金额' in lin_text_no_space:
                            for character in text_line:
                                if isinstance(character, LTChar) and character.get_text() == '额':
                                    _layout['item_price_bx'][2:4] = [character.x1+D_PIX, character.y0+D_PIX]
                                    _layout['item_taxrate_bx'][0] = character.x1
                                    _layout['total_price_bx'][2] = character.x1+D_PIX
                            break
                
                if '税率/征收率' in ele_text:
                    for text_line in element:
                        lin_text = text_line.get_text()
                        if '税率/征收率' in lin_text:
                            for character in text_line:
                                if isinstance(character, LTChar) and character.get_text() == '率':
                                    _layout['item_taxrate_bx'][2:4] = [character.x1+D_PIX, character.y0+D_PIX]
                                    _layout['item_tax_bx'][0] = character.x1
                                    _layout['total_tax_bx'][0] = character.x1
                            break

                if '税  额' in ele_text or '税额\n' in ele_text_no_space:
                    for text_line in element:
                        lin_text = text_line.get_text()
                        lin_text_no_space = lin_text.replace(' ', '')
                        if '税  额' in lin_text or '税额\n' in lin_text_no_space:
                            _layout['item_tax_bx'][2:4] = [page.x1, text_line.y0+D_PIX]
                            break
                
                if '小        计' in ele_text or '小计\n' in ele_text_no_space:
                    multi_pages = True
                    for text_line in element:
                        lin_text = text_line.get_text()
                        lin_text_no_space = lin_text.replace(' ', '')
                        if '小        计' in lin_text or '小计\n' in lin_text_no_space:
                            _layout['item_name_bx'][1] = text_line.y1
                            _layout['item_type_bx'][1] = text_line.y1
                            _layout['item_unit_bx'][1] = text_line.y1
                            _layout['item_number_bx'][1] = text_line.y1
                            _layout['item_uniprice_bx'][1] = text_line.y1
                            _layout['item_price_bx'][1] = text_line.y1
                            _layout['item_taxrate_bx'][1] = text_line.y1
                            _layout['item_tax_bx'][1] = text_line.y1
                            break
                
                if '合        计' in ele_text or '合计\n' in ele_text_no_space:
                    for text_line in element:
                        lin_text = text_line.get_text()
                        lin_text_no_space = lin_text.replace(' ', '')
                        if '合        计' in lin_text or '合计\n' in lin_text_no_space:
                            if not multi_pages:
                                _layout['item_name_bx'][1] = text_line.y1
                                _layout['item_type_bx'][1] = text_line.y1
                                _layout['item_unit_bx'][1] = text_line.y1
                                _layout['item_number_bx'][1] = text_line.y1
                                _layout['item_uniprice_bx'][1] = text_line.y1
                                _layout['item_price_bx'][1] = text_line.y1
                                _layout['item_taxrate_bx'][1] = text_line.y1
                                _layout['item_tax_bx'][1] = text_line.y1

                            _layout['total_price_bx'][0:2] = [text_line.x1, text_line.y0-D_PIX]
                            _layout['total_price_bx'][3] = text_line.y1+D_PIX
                            _layout['total_tax_bx'][1] = text_line.y0-D_PIX
                            _layout['total_tax_bx'][2:4] = [page.x1, text_line.y1+D_PIX]
                            _layout['total_price_and_tax_bx'][3] = text_line.y0
                            break

                if '¥' in ele_text:
                    for text_line in element:
                        lin_text = text_line.get_text()
                        if '¥' in lin_text:
                            if _layout['item_name_bx'][1] == None:
                                _layout['item_name_bx'][1] = text_line.y1
                                _layout['item_type_bx'][1] = text_line.y1
                                _layout['item_unit_bx'][1] = text_line.y1
                                _layout['item_number_bx'][1] = text_line.y1
                                _layout['item_uniprice_bx'][1] = text_line.y1
                                _layout['item_price_bx'][1] = text_line.y1
                                _layout['item_taxrate_bx'][1] = text_line.y1
                                _layout['item_tax_bx'][1] = text_line.y1
                            else:
                                _layout['item_name_bx'][1] = max(_layout['item_name_bx'][1], text_line.y1)
                                _layout['item_type_bx'][1] = max(_layout['item_type_bx'][1], text_line.y1)
                                _layout['item_unit_bx'][1] = max(_layout['item_unit_bx'][1], text_line.y1)
                                _layout['item_number_bx'][1] = max(_layout['item_number_bx'][1], text_line.y1)
                                _layout['item_uniprice_bx'][1] = max(_layout['item_uniprice_bx'][1], text_line.y1)
                                _layout['item_price_bx'][1] = max(_layout['item_price_bx'][1], text_line.y1)
                                _layout['item_taxrate_bx'][1] = max(_layout['item_taxrate_bx'][1], text_line.y1)
                                _layout['item_tax_bx'][1] = max(_layout['item_tax_bx'][1], text_line.y1)
                
                if '（小写）' in ele_text:
                    for text_line in element:
                        lin_text = text_line.get_text()
                        if '（小写）' in lin_text:
                            _layout['total_price_and_tax_bx'][0:3] = [text_line.x0+D_PIX, text_line.y0-2*D_PIX, page.x1]  # potential error here

        fix_unstructured_layout(_layout)

        items_divide = []
        for element in page:
            if isinstance(element, LTTextContainer):
                for text_line in element:
                        lin_text = text_line.get_text()
                        if '%' in lin_text and lin_text[-1] == '\n':
                            items_divide.append(text_line.y1+D_PIX)
        items_divide.sort(reverse=True)
        _layout['items_divline'] = items_divide
        _layout['num_items'] = len(items_divide)  # number of product items
        _layout['items_divline'].append(_layout['item_name_bx'][1])

        pages_layout.append(_layout)


    pdf_file = extract_pages(fpath)
    inovice_info_dict = {}
    inovice_items_mat = []

    item_bias = 0
    for pg, lyt in zip(pdf_file, pages_layout):
        for _ in range(int(lyt['num_items'])):
            inovice_items_mat.append([str()] * 8)

        for em in pg:
            if isinstance(em, LTTextContainer):
                for txl in em:
                    if not hasattr(txl, 'x0'):
                        continue

                    if item_bias == 0:  # extract general information on the first page
                        lin_text = txl.get_text()
                        lin_pos = [txl.x0, txl.y0, txl.x1, txl.y1]
                        if lin_text[-1] == '\n':
                            lin_text = lin_text[:-1]

                        if is_inside_box(lin_pos, lyt['inovice_number_bx']):
                            if lin_text.isdigit() and len(lin_text) == 20:
                                inovice_info_dict['inovice_number'] = lin_text
                            continue
                        
                        if is_inside_box(lin_pos, lyt['inovice_date_bx']):
                            if is_valid_date(lin_text):
                                inovice_info_dict['inovice_date'] = lin_text
                            continue
                        
                        if is_inside_box(lin_pos, lyt['seller_info_bx']):
                            if ':\n' in lin_text or '：\n' in lin_text or len(lin_text) <= 2:
                                continue
                            if lin_pos[1] >= 0.5 * (lyt['seller_info_bx'][1] + lyt['seller_info_bx'][3]):
                                inovice_info_dict['seller_name'] = lin_text
                            else:
                                inovice_info_dict['seller_code'] = lin_text
                            continue

                        if is_inside_box(lin_pos, lyt['total_price_bx']):
                            if '¥' in lin_text:
                                _idx = lin_text.find('¥')
                                inovice_info_dict['total_price_without_tax'] = lin_text[_idx+1:]
                            else:
                                inovice_info_dict['total_price_without_tax'] = lin_text
                            continue

                        if is_inside_box(lin_pos, lyt['total_tax_bx']):
                            if '¥' in lin_text:
                                _idx = lin_text.find('¥')
                                inovice_info_dict['total_tax'] = lin_text[_idx+1:]
                            else:
                                inovice_info_dict['total_tax'] = lin_text
                            continue


                    if not hasattr(txl, '__iter__'):
                        txl = [txl]

                    for ch in txl:
                        if isinstance(ch, LTChar):
                            ch_text = ch.get_text()
                            if ch_text == '\n':
                                continue
                            ch_pos = [ch.x0, ch.y0, ch.x1, ch.y1]

                            for i in range(lyt['num_items']):
                                it_name_bx = [lyt['item_name_bx'][0], lyt['items_divline'][i+1], lyt['item_name_bx'][2], lyt['items_divline'][i]]
                                it_type_bx = [lyt['item_type_bx'][0], lyt['items_divline'][i+1], lyt['item_type_bx'][2], lyt['items_divline'][i]]
                                it_unit_bx = [lyt['item_unit_bx'][0], lyt['items_divline'][i+1], lyt['item_unit_bx'][2], lyt['items_divline'][i]]
                                it_num_bx = [lyt['item_number_bx'][0], lyt['items_divline'][i+1], lyt['item_number_bx'][2], lyt['items_divline'][i]]
                                it_uniprice_bx = [lyt['item_uniprice_bx'][0], lyt['items_divline'][i+1], lyt['item_uniprice_bx'][2], lyt['items_divline'][i]]
                                it_price_bx = [lyt['item_price_bx'][0], lyt['items_divline'][i+1], lyt['item_price_bx'][2], lyt['items_divline'][i]]
                                it_taxrt_bx = [lyt['item_taxrate_bx'][0], lyt['items_divline'][i+1], lyt['item_taxrate_bx'][2], lyt['items_divline'][i]]
                                it_tax_bx = [lyt['item_tax_bx'][0], lyt['items_divline'][i+1], lyt['item_tax_bx'][2], lyt['items_divline'][i]]

                                if is_inside_box(ch_pos, it_name_bx):
                                    inovice_items_mat[i+item_bias][0] += ch_text
                                    continue

                                if is_inside_box(ch_pos, it_type_bx):
                                    inovice_items_mat[i+item_bias][1] += ch_text
                                    continue

                                if is_inside_box(ch_pos, it_unit_bx):
                                    inovice_items_mat[i+item_bias][2] += ch_text
                                    continue

                                if is_inside_box(ch_pos, it_num_bx):
                                    inovice_items_mat[i+item_bias][3] += ch_text
                                    continue

                                if is_inside_box(ch_pos, it_uniprice_bx):
                                    inovice_items_mat[i+item_bias][4] += ch_text
                                    continue

                                if is_inside_box(ch_pos, it_price_bx):
                                    inovice_items_mat[i+item_bias][5] += ch_text
                                    continue

                                if is_inside_box(ch_pos, it_taxrt_bx):
                                    inovice_items_mat[i+item_bias][6] += ch_text
                                    continue

                                if is_inside_box(ch_pos, it_tax_bx):
                                    inovice_items_mat[i+item_bias][7] += ch_text
                                    continue
                    
                    if lyt['total_price_and_tax_bx'][0] != None:  # extract total price and tax on the last page
                        if isinstance(txl, list):
                            txl = txl[0]
                            
                        lin_text = txl.get_text()
                        lin_pos = [txl.x0, txl.y0, txl.x1, txl.y1]
                        if lin_text[-1] == '\n':
                            lin_text = lin_text[:-1]

                        if is_inside_box(lin_pos, lyt['total_price_and_tax_bx']):
                            if '¥' in lin_text:
                                _idx = lin_text.find('¥')
                                inovice_info_dict['total_price_and_tax'] = lin_text[_idx+1:]
                            else:
                                inovice_info_dict['total_price_and_tax'] = lin_text
                            continue
        
        item_bias += int(lyt['num_items'])
    
    inovice_info_dict['items'] = inovice_items_mat
    inovice_info_dict['items_num'] = item_bias

    return inovice_info_dict