import pandas as pd
import json

def process(filename):
    final_json={}
    exclude=["MONDAY","TUESDAY","WEDNESDAY","THURSDAY","FRIDAY","SATURDAY","SUNDAY"]

    df = pd.read_excel(filename)
    for i in range(df.shape[1]):
        col=list(df.iloc[:,i])
        
        #col[0]=f'{col[0]:%Y-%m-%d}'
        temp={"breakfast":[],"lunch":[],"dinner":[]}
        bf=False
        lch=False
        dnr=False
        for i in range(1,len(col)):
            if col[i] in exclude:
                continue
            elif col[i]=="BREAKFAST":
                bf=True
                continue
            elif col[i]=="LUNCH":
                bf=False
                lch=True
                continue
            elif col[i]=="DINNER":
                lch=False
                dnr=True
                continue
            elif type(col[i]) is float:
                continue
            elif col[i][0]=="*" and col[i][-1]=="*":
                continue
            elif bf==True:
                temp['breakfast'].append(col[i])
            elif lch==True:
                temp['lunch'].append(col[i])
            elif dnr==True:
                temp['dinner'].append(col[i])
        final_json[col[0]]=temp

    return final_json
