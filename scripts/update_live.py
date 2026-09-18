import json, re, urllib.request
from datetime import datetime, timezone

SOURCES = [
  ("upsc","UPSC Recruitment","https://www.upsc.gov.in/recruitment"),
  ("ssc","SSC","https://ssc.gov.in/"),
  ("rrb","RRB","https://www.rrbapply.gov.in/"),
  ("ibps","IBPS","https://www.ibps.in/"),
  ("india-post","India Post","https://www.indiapost.gov.in/"),
  ("employment-news","Employment News","https://employmentnews.gov.in/newemp/AllJobs.aspx?k=All"),
  ("isro","ISRO Careers","https://www.isro.gov.in/Careers.html"),
  ("drdo","DRDO Careers","https://www.drdo.gov.in/careers"),
  ("tgprb","Telangana Police Recruitment Board","https://www.tgprb.in/"),
  ("mhsrb","Telangana MHSRB","https://mhsrb.telangana.gov.in/"),
  ("tspsc","TGPSC","https://www.tspsc.gov.in/"),
]

def get(url):
    req=urllib.request.Request(url,headers={"User-Agent":"GovtJobsHub-LiveUpdater/1.0"})
    with urllib.request.urlopen(req,timeout=20) as r:
        return r.read().decode("utf-8","ignore")

def extract_dates(text):
    patterns=[
        r"\b\d{1,2}[/-](?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*[/-]\d{2,4}\b",
        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
        r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b",
    ]
    out=[]
    for p in patterns:
        out += re.findall(p,text,re.I)
    return list(dict.fromkeys(out))[:12]

now=datetime.now(timezone.utc).astimezone()
data={"updatedAt":now.isoformat(),"sources":[]}
for key,name,url in SOURCES:
    item={"id":key,"name":name,"url":url,"status":"SOURCE CHECKED","dates":[],"ok":False}
    try:
        html=get(url)
        plain=re.sub(r"<[^>]+>"," ",html)
        plain=re.sub(r"\s+"," ",plain)
        item["dates"]=extract_dates(plain)
        item["ok"]=True
        item["status"]="LIVE SOURCE"
    except Exception as e:
        item["status"]="SOURCE UNAVAILABLE"
        item["error"]=str(e)[:160]
    data["sources"].append(item)

with open("live.json","w",encoding="utf-8") as f:
    json.dump(data,f,ensure_ascii=False,indent=2)
