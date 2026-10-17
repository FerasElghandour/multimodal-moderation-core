"""Provider-neutral multimodal moderation decisions and aggregate analytics."""
import math
from dataclasses import dataclass
from collections import Counter

MODALITIES={'text','image','audio','video'}

@dataclass(frozen=True)
class Assessment:
    modality:str
    scores:dict
    explanation:str=''
    error:str|None=None
    def __post_init__(self):
        if self.modality not in MODALITIES:raise ValueError('Unsupported modality')
        if any(not isinstance(v,(int,float)) or not math.isfinite(v) or not 0<=v<=1 for v in self.scores.values()):raise ValueError('Category scores must be finite values in [0,1]')

@dataclass(frozen=True)
class Decision:
    modality:str
    blocked:bool
    categories:tuple
    error:bool

def decide(assessment,threshold=.5,fail_closed=True):
    if not 0<=threshold<=1:raise ValueError('Threshold must be in [0,1]')
    flagged=tuple(sorted(k for k,v in assessment.scores.items() if v>=threshold))
    return Decision(assessment.modality,bool(flagged) or bool(assessment.error and fail_closed),flagged,bool(assessment.error))

def assess(payload,modality,provider):
    if modality not in MODALITIES:raise ValueError('Unsupported modality')
    try:
        result=provider(payload,modality)
        if not isinstance(result,Assessment) or result.modality!=modality:raise ValueError('Provider returned an inconsistent assessment')
        return result
    except Exception:
        # Do not include raw provider errors or submitted media in analytics.
        return Assessment(modality,{},error='Provider assessment unavailable')

def summarize(decisions):
    rows=list(decisions);modes=Counter(r.modality for r in rows);categories=Counter(c for r in rows for c in r.categories)
    blocked=sum(r.blocked for r in rows)
    return {'total':len(rows),'blocked':blocked,'blocked_fraction':blocked/len(rows) if rows else 0.,
       'errors':sum(r.error for r in rows),'modalities':dict(modes),'categories':dict(categories)}
