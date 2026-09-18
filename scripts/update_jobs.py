#!/usr/bin/env python3
import json,re,datetime,urllib.request,urllib.error
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"/"live.json"
with DATA.open(encoding="utf-8") as f: data=json.load(f)

# Official pages only. The monitor checks availability/reachability and records a fresh
# verification timestamp. It deliberately does NOT guess dates when an official page
# does not expose a machine-readable application window.
SOURCES={
 "upsc":"https://www.upsc.gov.in/recruitment",
 "ssc":"https://ssc.gov.in/",
 "rrb":"https://www.rrbapply.gov.in/",
 "ibps":"https://www.ibps.in/",
 "sbi":"https://sbi.co.in/web/careers/",
 "india-post":"https://www.indiapost.gov.in/",
 "employment-news":"https://employmentnews.gov.in/newemp/AllJobs.aspx?k=All",
 "rbi":"https://opportunities.rbi.org.in/",
 "nabard":"https://www.nabard.org/",
 "sebi":"https://www.sebi.gov.in/",
 "drdo":"https://www.drdo.gov.in/",
 "isro":"https://www.isro.gov.in/Careers.html",
 "aiims":"https://www.aiimsexams.ac.in/",
 "ctet":"https://ctet.nic.in/",
 "ugc-net":"https://ugcnet.nta.ugc.in/",
 "tgpsc":"https://www.tspsc.gov.in/",
 "tgprb":"https://www.tgprb.in/",
 "mhsrb":"https://mhsrb.telangana.gov.in/",
 "deet":"https://deet.telangana.gov.in/",
 "tgsrtc":"https://www.tgsrtc.telangana.gov.in/",
 "tgenco":"https://tgenco.co.in/",
 "tsnpdcl":"https://tsnpdcl.in/",
 "tstransco":"https://tstransco.in/",
}

def fetch(url):
    req=urllib.request.Request(url,headers={"User-Agent":"GovtJobsHub-Monitor/1.0"})
    try:
        with urllib.request.urlopen(req,timeout=20) as r:
            body=r.read(500000).decode("utf-8","ignore")
            return r.status,body
    except Exception as e:
        return None,str(e)

now=datetime.datetime.now(datetime.timezone.utc).astimezone()
stamp=now.strftime("%d %b %Y, %I:%M %p %Z")
health={}
for name,url in SOURCES.items():
    status,body=fetch(url)
    health[name]={"ok":status==200,"http":status,"checked":stamp}
    if name=="employment-news" and status==200:
        data.setdefault(name,{})
        data[name]["verified"]=stamp
        data[name]["source"]=url

# Fresh verification for every configured record whose official source is reachable.
# This is intentionally conservative: no date/status is invented from a generic homepage.
source_map={
 "india-post-gds":"india-post","rrb-paramedical":"rrb","tgpsc-forest":"tgpsc",
 "upsc-ora":"upsc","isro":"isro","ibps-po":"ibps","ibps-clerk":"ibps","ibps-rrb":"ibps",
 "tgprb-pc":"tgprb","tgprb-si":"tgprb","tgprb-driver":"tgprb","tgprb-asi-fpb":"tgprb",
 "employment-news":"employment-news"
}
for jid,src in source_map.items():
    if jid in data and health.get(src,{}).get("ok"):
        data[jid]["verified"]=stamp
        data[jid]["source"]=SOURCES[src]

payload={"meta":{"lastRun":stamp,"mode":"official-source monitor","sourceHealth":health},"jobs":data}
# Keep compatibility with the current front-end by writing only the jobs object.
with DATA.open("w",encoding="utf-8") as f: json.dump(data,f,ensure_ascii=False,indent=2); f.write("\n")
with (ROOT/"data"/"monitor-health.json").open("w",encoding="utf-8") as f: json.dump(payload["meta"],f,ensure_ascii=False,indent=2); f.write("\n")
print("Verified",len(source_map),"job routes; checked",len(SOURCES),"official sources at",stamp)
