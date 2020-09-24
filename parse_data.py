
import pandas as pd
import github
import io


url = 'https://docs.google.com/spreadsheets/d/16-bnsDdmmgtSxdWbVMboIHo5FRuz76DBxsz_BbsEVWA/export?format=csv&id=16-bnsDdmmgtSxdWbVMboIHo5FRuz76DBxsz_BbsEVWA&gid=0'
df = pd.read_csv(url)
df2 = pd.read_csv('covid-19-arg.csv')

if df.loc[df.index[-1], "fecha"] == df2.loc[df2.index[-1], "fecha"]:
    print("Nothing to update")
    exit(0)

print("New csv")
df.to_csv('covid-19-arg.csv', index=False)
f = io.open("covid-19-arg.csv", mode="r", encoding="utf-8")

token = ""
gh = github.Github(token)
gist = gh.get_gist("")
gist.edit(
    description="Update csv",
    files={"covid-19-arg.csv": github.InputFileContent(content=f.read())},
)
