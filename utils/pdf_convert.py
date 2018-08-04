from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTContainer
from pdfminer.pdfpage import PDFPage
import numpy as np
import re

from utils.check_type import is_float
from utils.format import format_date


class KondateData:
    def __init__(self, date):
        self.date = date
        self.breakfast = []
        self.breakfast_nutritive = []
        self.lunch = []
        self.lunch_nutritive = []
        self.dinner = []
        self.dinner_nutritive = []


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
    raw_data_dict = [[], [], [], [], [], [], []]
    parsed_data_dict = [[], [], [], [], [], [], []]

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
        raw_data_dict[idx].append(text_box)

    # NGワード除外
    for idx, item in enumerate(raw_data_dict):
        for text_box in item:
            text_box_value = text_box.get_text().replace("\n", "")
            if text_box_value not in ng_words:
                parsed_data_dict[idx].append(text_box_value)

    return parsed_data_dict


def get_kondate_from_parsed_data(year, parsed_data):
    # KondateData初期化(日付を文字列にする処理を同時に行う)
    week_kondate_data = {}
    for value in parsed_data:
        week_kondate_data[format_date(year, value[0])] = KondateData(format_date(year, value[0]))

    # 献立を読み込んでいく…
    for value in parsed_data:
        str_date = format_date(year, value[0])
        read_data = [[], [], [], [], [], []]
        now_read_type = 0  # 0, 2, 4 -> 朝食, 昼食, 夕食 : 1, 3, 5 -> それぞれの栄養値

        for item in value:
            # 読み込みデータの種類が変わった時
            if (is_float(item) and now_read_type % 2 == 0) or (not is_float(item) and now_read_type % 2 == 1):
                now_read_type += 1

            read_data[now_read_type].append(item)

        read_data[0] = read_data[0][2:]

        print(read_data)
    print(week_kondate_data)


def get_kondate_from_pdf(file_path):
    # PDFを解析するために必要
    resource_manager = PDFResourceManager()
    layout_params = LAParams()
    layout_params.detect_vertical = True
    device = PDFPageAggregator(resource_manager, laparams=layout_params)

    # PDFファイルを開いてページ単位で読み込み
    with open(file_path, 'rb') as fp:
        interpreter = PDFPageInterpreter(resource_manager, device)

        for page in PDFPage.get_pages(fp, maxpages=1, caching=True, check_extractable=True):
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
    get_kondate_from_pdf("../PDFData/07.pdf")
