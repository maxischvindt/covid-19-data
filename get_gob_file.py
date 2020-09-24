import requests
import os
import re
import pandas as pd
import pdfplumber
import github
import io
from datetime import date, timedelta


def download_file(url, fileName):
    response = requests.get(url, allow_redirects=True, stream=True)
    file = f"reportes/{fileName}"

    if response.status_code == 404:
        return False

    if os.path.exists(file):
        os.remove(file)

    with open(file, 'wb') as f:
        f.write(response.content)
        return True


def parser_data(filename):
    pdf = pdfplumber.open(f"reportes/{fileName}")
    pages = len(pdf.pages)
    text = ""
    for p in range(0,pages):
        page = pdf.pages[p]
        text += page.extract_text()

    text = text.replace("\n", "")

    # reporte matutino
    # total_confirmed = re.findall(r"confirmados *en *Argentina *es *de *([\d]+.[\d]+.[\d]+)", text)
    # total_recovered = re.findall(r"total *de *altas *es *de *([\d]+.[\d]+.[\d]+)", text)
    # total_deaths = re.findall(r"fallecidas *es *([\d]+.[\d]+.[\d]+)", text)
    # total_tests = re.findall(r"brote *se *realizaron *([\d]+.[\d]+.[\d]+)", text)
    # total_negative_tests = re.findall(r"descartados *hasta *ayer *es *de *([\d]+.[\d]+.[\d]+)", text)

    # reporte vespertino
    total_confirmed = re.findall(r"suman *([\d]+.[\d]+.[\d]+) *positivos *en *el *país", text)
    total_recovered = re.findall(r"([\d]+.[\d]+.[\d]+) *son *pacientes *recuperados", text)
    total_deaths = re.findall(r"fallecidas *es *([\d]+.[\d]+.[\d]+)", text)
    total_tests = re.findall(r"([\d]+.[\d]+.[\d]+) *pruebas *diagnósticas", text)

    pdf.close()

    results = []
    for d in [total_confirmed, total_recovered, total_deaths, total_tests]:
        if len(d) > 0:
            results.append(d[0].replace(".", ""))
        else:
            results.append(0)

    return results


edate = date.today()
dates = pd.date_range(edate - timedelta(days=10), edate, freq='d')

df2 = pd.read_csv('aux-covid-19-arg.csv')

new_data = []
for d in dates:
    _date = (d.strftime('%d-%m-%y'))
    url = f"https://www.argentina.gob.ar/sites/default/files/{_date}-reporte-vespertino-covid-19.pdf"
    # url = f"https://www.argentina.gob.ar/sites/default/files/{_date}-reporte-matutino-covid-19.pdf"
    fileName = f"{_date}-reporte-vespertino-covid-19.pdf"
    status = download_file(url, fileName)

    pre_date = d.strftime('%d-%m-%Y')
    print(f"{fileName} downloaded...status {status} and date to update is {pre_date}")

    if status:
        data = parser_data(fileName)
        if data[1] != 0 and data[3] != 0 and data[0] != 0:
            total_negatives = int(data[3]) - int(data[0])
            new_data.append([pre_date, data[1], total_negatives, data[3]])

df = pd.DataFrame(new_data, columns=["date", "recovered", "negative_tests", "total_tests"])

new_df = pd.concat([df2, df])
df_to_csv = new_df.drop_duplicates(subset=['date'], keep='last')

df_to_csv.to_csv('aux-covid-19-arg.csv', index=False)
f = io.open("aux-covid-19-arg.csv", mode="r", encoding="utf-8")

token = ""
gh = github.Github(token)
gist = gh.get_gist("")
update_date = (edate.strftime('%d-%m-%y'))
gist.edit(
    description=f"Updated csv on {update_date}",
    files={"aux-covid-19-arg.csv": github.InputFileContent(content=f.read())},
)


