from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTContainer
from pdfminer.pdfpage import PDFPage
import numpy as np
import re


class KondateData:
    def __init__(self, date):
        self.date = date
        self.breakfast = []
        self.breakfast_nutritive = []
        self.lunch = []
        self.lunch_nutritive = []
        self.dinner = []
        self.dinner.nutritive = []


# PDF内のTextBoxを再帰で探す
def find_textbox_recursively(layout_obj):
    if isinstance(layout_obj, LTTextBox):
        return [layout_obj]

    if isinstance(layout_obj, LTContainer):
        boxes = []
        for child in layout_obj:
            boxes.extend(find_textbox_recursively(child))

        return boxes

    return []


def parse_textboxes(text_boxes):
    day_of_the_week_name = {
        0: "monday", 1: "tuesday", 2: "wednesday", 3: "thursday", 4: "friday", 5: "saturday", 6: "sunday"
    }
    raw_data_dict = {
        "monday": [],
        "tuesday": [],
        "wednesday": [],
        "thursday": [],
        "friday": [],
        "saturday": [],
        "sunday": []
    }
    parsed_data_dict = {
        "monday": [],
        "tuesday": [],
        "wednesday": [],
        "thursday": [],
        "friday": [],
        "saturday": [],
        "sunday": []
    }

    ng_words = [
        "栄養価 熱量(kcal) 蛋白質(g) 脂質(g) 炭水化物(g) 塩分(g) 熱量(kcal) 蛋白質(g) 脂質(g) 炭水化物(g) 塩分(g) 熱量(kcal) 蛋白質(g) 脂質(g) 炭水化物(g) "
        "塩分(g) 熱量(kcal) 蛋白質(g) 脂質(g) 炭水化物(g) 塩分(g) 熱量(kcal) 蛋白質(g) 脂質(g) 炭水化物(g) 塩分(g) 熱量(kcal) 蛋白質(g) 脂質(g) 炭水化物(g) "
        "塩分(g) 熱量(kcal) 蛋白質(g) 脂質(g) 炭水化物(g) 塩分(g)",
        "栄養価 熱量(kcal) 蛋白質(g) 脂質(g) 炭水化物(g) 塩分(g) 熱量(kcal) 蛋白質(E) 脂質(E) 炭水化物(E) 塩分(E) 熱量(kcaH) 蛋白質(H) 脂質(H) 炭水化物(H) "
        "塩分(H) 熱量(kcal) 蛋白質(g) 脂質(g) 炭水化物(g) 塩分(g) 熱量(kcal) 蛋白質(g) 脂質(g) 炭水化物(g) 塩分(g) 熱量(kcal) 蛋白質(g) 脂質(g) 炭水化物(g) "
        "塩分(g) 熱量(kcal) 蛋白質(g) 脂質(g) 炭水化物(g) 塩分(g)",
        "日 曜",
        "日",
        "朝 食",
        "昼 食",
        "夕 食",
        "　　※ 材料入荷などの都合により、献立が変更になる場合がありますので御了承下さい。",
        "⼤⾬による断⽔，⾷材の⼊荷困難な状況から，メニュー通りの⾷事は提供できません．おにぎりのみといったこともあり得ます．⾮常事態ですので，ご理解，ご協⼒をお願いします．",
        "・"
    ]

    # 座標をもとにTextBoxを7つに分類する(日 月 ... 土)
    search_base_x = np.array([90, 240, 310, 430, 540, 650, 760])
    for text_box in text_boxes:
        idx = np.abs(search_base_x - text_box.x0).argmin()
        raw_data_dict[day_of_the_week_name[idx]].append(text_box)

    # NGワード除外
    for key, item in raw_data_dict.items():
        for text_box in item:
            text_box_value = text_box.get_text().replace("\n", "")
            if text_box_value not in ng_words:
                parsed_data_dict[key].append(text_box_value)

    return parsed_data_dict


def read_pdf(file_path):
    # PDFを解析するために必要
    resource_manager = PDFResourceManager()
    layout_params = LAParams()
    layout_params.detect_vertical = True
    device = PDFPageAggregator(resource_manager, laparams=layout_params)

    # PDFファイルを開いてページ単位で読み込み
    with open(file_path, 'rb') as fp:
        interpreter = PDFPageInterpreter(resource_manager, device)

        for page in PDFPage.get_pages(fp, maxpages=0, caching=True, check_extractable=True):
            interpreter.process_page(page)
            result = device.get_result()

            text_boxes = find_textbox_recursively(result)
            text_boxes.sort(key=lambda b: (-b.y1, b.x0))

            parsed_data = parse_textboxes(text_boxes)
            get_kondate_from_parsed_data(2018, parsed_data)
            # for text_box in text_boxes:
            #     print(text_box)

    device.close()


if __name__ == '__main__':
    read_pdf("../PDFData/07.pdf")
