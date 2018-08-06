import os
import urllib.request
from utils.format import christian_to_japanese


def download_kondate_pdf(year, month):
    url = "http://shirasunaryou.sakura.ne.jp/cgi-bin/shirasuna/kondate/"
    url += christian_to_japanese(year, month) + "/" + str(month).zfill(2) + ".pdf"
    download_path = os.path.dirname(os.path.abspath(__file__).replace("/network_connection", "")) + "/PDFData/"

    urllib.request.urlretrieve(url, download_path + str(year) + "/" + str(month).zfill(2) + ".pdf")
