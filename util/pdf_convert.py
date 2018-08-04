from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTContainer
from pdfminer.pdfpage import PDFPage


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


def read_pdf(file_path):
    # PDFを解析するために必要
    resource_manager = PDFResourceManager()
    layout_params = LAParams(detect_vertical=True)
    device = PDFPageAggregator(resource_manager, laparams=layout_params)

    # PDFファイルを開いてページ単位で読み込み
    with open(file_path, 'rb') as fp:
        interpreter = PDFPageInterpreter(resource_manager, device)

        for page in PDFPage.get_pages(fp, maxpages=0):
            interpreter.process_page(page)
            result = device.get_result()

            text_boxes = find_textbox_recursively(result)
            text_boxes.sort(key=lambda b: (-b.y1, b.x0))

            for text_box in text_boxes:
                print(text_box)

    device.close()


if __name__ == '__main__':
    read_pdf("../PDFData/07.pdf")
