# -*- coding: utf-8 -*-

# import csv
import xlwt
import itertools
import datetime

# Style
STYLE = xlwt.Style.easyxf(
    "font: colour white, bold on; align: wrap on, vert centre, horiz center; pattern: pattern solid, fore-colour ocean_blue;"
)


def fill_sheet(worksheet: xlwt.Worksheet, exams: list):
    """
    This function fills a worksheet with the given exams

    Parameters
    ----------
    worksheet : xlwt.Worksheet
        Patient name
    exams: list
        All metrics by contition

    Returns
    -------
    bool
        Whether the process was succesful
    """

    # Header
    header = ["MÉTRICA", "MÉDIA", "DESVPAD"]

    # Redefine HEADER
    for i in range(len(exams)):
        header.insert(i + 1, f"E{i+1}")

    # Fill header
    for i, item in enumerate(header):
        worksheet.write(0, i, item, style=STYLE)

    # Fill metrics
    for i, metrics in enumerate(exams):
        keys = list(metrics.keys())
        for j, key in enumerate(keys):
            # Metrics labels
            if not i:
                worksheet.write(j + 1, 0, keys[j], style=STYLE)
            worksheet.write(j + 1, i + 1, round(metrics[key], 2))

    # Fill mean and stdev
    nrows = len(exams[0])
    ncols = len(exams)
    for i in range(nrows):
        worksheet.write(i + 1, ncols + 1, xlwt.Formula(f"AVERAGE(B{i+2}:D{i+2})"))
        worksheet.write(i + 1, ncols + 2, xlwt.Formula(f"STDEV(B{i+2}:D{i+2})"))

    # Change cell size
    col_width = 256 * 15  # 20 characters wide
    try:
        for i in itertools.count():
            worksheet.col(i).width = col_width
    except ValueError:
        pass


def generate_report(name: str, exams: dict, date: str):
    """
    This function generates a report with the given exams

    Parameters
    ----------
    name : str
        Patient name
    exams : dict
        All exams by contition
    date : str
        Exam date

    Returns
    -------
    bool
        Whether the process was succesful
    """

    # Init Workbook
    workbook = xlwt.Workbook()

    keys = [
        t.replace("O", "OA").replace("F", "E").replace("C", "OF").replace("N", "")
        for t in list(exams.keys())
    ]

    for i, key in enumerate(exams.keys()):
        worksheet = workbook.add_sheet(keys[i])
        fill_sheet(worksheet, exams[key])

    workbook.save(f"reports/{name} ({date}).xls")


if __name__ == "__main__":
    import numpy as np

    metrics = dict()
    keys = [
        "AP_",
        "ML_",
        "dis_media",
        "dis_mediaAP",
        "dis_mediaML",
        "dis_rms_total",
        "dis_rms_AP",
        "dis_rms_ML",
        "totex_total",
        "totex_AP",
        "totex_ML",
        "mvelo_total",
        "mvelo_AP",
        "mvelo_ML",
        "amplitude_total",
        "amplitude_AP",
        "amplitude_ML",
    ]
    values = np.random.random_sample(len(keys))
    for i, key in enumerate(keys):
        metrics[key] = values[i]

    name = "Raí"
    exams = {
        "OA": [metrics, metrics, metrics],
        "OF": [metrics, metrics, metrics],
        "OAE": [metrics, metrics, metrics],
        "OFE": [metrics, metrics, metrics],
    }
    date = datetime.date.today().isoformat()

    generate_report(name, exams, date)
