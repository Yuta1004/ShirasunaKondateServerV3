from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTContainer
from pdfminer.pdfpage import PDFPage
import numpy as np
import re
import os

from Utils.check_type import is_float
from Utils.format import format_date


class KondateData:
    def __init__(self, date):
        self.date = date
        self.breakfast = []
        self.breakfast_nutritive = []
        self.lunch = []
        self.lunch_nutritive = []
        self.dinner = []
        self.dinner_nutritive = []

    def set_kondate_data(self, breakfast, breakfast_nutritive, lunch, lunch_nutritive, dinner, dinner_nutritive):
        self.breakfast.extend(breakfast)
        self.breakfast_nutritive.extend(breakfast_nutritive)
        self.lunch.extend(lunch)
        self.lunch_nutritive.extend(lunch_nutritive)
        self.dinner.extend(dinner)
        self.dinner_nutritive.extend(dinner_nutritive)


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
        "朝食",
        "昼食",
        "夕食",
        "曜日",
        "朝 食",
        "昼 食",
        "夕 食",
        "西洋フード・コンパスグループ㈱",
        "　　※ 材料入荷などの都合により、献立が変更になる場合がありますので御了承下さい。",
        "⼤⾬による断⽔，⾷材の⼊荷困難な状況から，メニュー通りの⾷事は提供できません．おにぎりのみといったこともあり得ます．⾮常事態ですので，ご理解，ご協⼒をお願いします．",
        "・"
    ]

    # 基準となる座標を取得する
    # ファイルによって座標が異なるので特定のワードを含む文字列をヘッダー座標として取得する
    search_base_x = []
    for text_box in text_boxes:
        if re.match(r".*月.*日\n", text_box.get_text()) and len(search_base_x) < 7:
            search_base_x.append(int((text_box.x0+text_box.x1)/2))

    # 特定文字列が存在しない場合は座標をセットする
    if len(search_base_x) == 0:
        search_base_x = [93, 206, 319, 432, 545, 657, 770]

    # 座標をもとにTextBoxを7つに分類する(日 月 ... 土)
    search_base_x = np.array(search_base_x)
    for text_box in text_boxes:
        # 2つのTextBoxを連結して読み込んでいたときは別処理
        if abs(text_box.x1 - text_box.x0) >= 150:
            idx = np.abs(search_base_x - ((text_box.x0+text_box.x1)/2-50)).argmin()
        else:
            idx = np.abs(search_base_x - (text_box.x0+text_box.x1)/2).argmin()

        raw_data_dict[max(0, idx)].append(text_box)

    # NGワード除外
    for idx, item in enumerate(raw_data_dict):
        for text_box in item:
            text_box_value = text_box.get_text().replace("\n", "")
            if text_box_value not in ng_words:
                parsed_data_dict[idx].append(text_box_value)

    return parsed_data_dict


def get_kondate_from_parsed_data(year, parsed_data):
    # KondateData初期化(日付を文字列にする処理を同時に行う)
    week_kondate_data = []
    for value in parsed_data:
        if len(value) != 0:
            week_kondate_data.append(KondateData(format_date(year, value[0])))

    # 献立を読み込んでいく…
    for idx, value in enumerate(parsed_data):
        read_data = [[], [], [], [], [], []]
        now_read_type = 0  # 0, 2, 4 -> 朝食, 昼食, 夕食 : 1, 3, 5 -> それぞれの栄養値

        if len(value) == 0:
            continue

        for item in value:
            # 読み込みデータの種類が変わった時
            if (is_float(item.split(" ")[0]) and now_read_type % 2 == 0) or (not is_float(item.split(" ")[0]) and now_read_type % 2 == 1):
                now_read_type += 1

            # 読み込みに失敗しているデータがあったら
            if len(item.split(" ")) >= 2 and idx < len(week_kondate_data)-1 and now_read_type % 2 == 0:
                if now_read_type == 0:
                    week_kondate_data[idx + 1].breakfast.append(item.split(" ")[1])
                elif now_read_type == 2:
                    week_kondate_data[idx + 1].lunch.append(item.split(" ")[1])
                else:
                    week_kondate_data[idx + 1].dinner.append(item.split(" ")[1])

                read_data[now_read_type].append(item.split(" ")[0])
                continue

            if now_read_type <= 5:
                read_data[now_read_type].append(item)

        # 日付情報が含まれているので除去
        read_data[0] = read_data[0][2:]

        week_kondate_data[idx].set_kondate_data(
            breakfast=read_data[0],
            breakfast_nutritive=read_data[1],
            lunch=read_data[2],
            lunch_nutritive=read_data[3],
            dinner=read_data[4],
            dinner_nutritive=read_data[5]
        )

    return week_kondate_data


def get_kondate_from_pdf(dir, year, month):
    # PDFを解析するために必要
    resource_manager = PDFResourceManager()
    layout_params = LAParams()
    layout_params.detect_vertical = True
    device = PDFPageAggregator(resource_manager, laparams=layout_params)

    # PDFファイルを開いてページ単位で読み込み
    file_path = dir + "/PDFData/" + str(year) + "/" + str(month).zfill(2) + ".pdf"
    if not os.path.exists(file_path):
        raise FileNotFoundError("指定された年月のPDFファイルが存在しません．")

    kondate_data_all = []
    with open(file_path, 'rb') as fp:
        interpreter = PDFPageInterpreter(resource_manager, device)

        for page in PDFPage.get_pages(fp, maxpages=0, caching=True, check_extractable=True):
            interpreter.process_page(page)
            result = device.get_result()

            text_boxes = find_textbox_recursively(result)
            text_boxes.sort(key=lambda b: (-b.y1, b.x0))

            parsed_data = parse_textboxes(text_boxes)
            kondate_data = get_kondate_from_parsed_data(year, parsed_data)
            kondate_data_all.extend(kondate_data)

    device.close()

    return kondate_data_all


if __name__ == '__main__':
    print(len(get_kondate_from_pdf("..", 2018, 7)))
