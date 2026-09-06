import re
from difflib import SequenceMatcher

STOP={"the","a","an","is","in","on","at","and","or","of","to","for","with","my","was","this","that"}

def tokens(text):
    return {x for x in re.findall(r"[a-z0-9]+", text.lower()) if x not in STOP and len(x)>2}

def score_pair(lost,found):
    lt=tokens(f"{lost.title} {lost.description} {lost.location} {lost.category}")
    ft=tokens(f"{found.title} {found.description} {found.location} {found.category}")
    overlap=len(lt&ft)/max(1,len(lt|ft))
    seq=SequenceMatcher(None,lost.description.lower(),found.description.lower()).ratio()
    score=.65*overlap+.35*seq
    if lost.location.strip().lower()==found.location.strip().lower(): score=min(1,score+.15)
    if lost.category==found.category and lost.category!="Other": score=min(1,score+.10)
    return score
