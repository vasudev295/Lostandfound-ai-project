from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from pathlib import Path
import shutil, uuid, json

from dotenv import load_dotenv
load_dotenv()

from .database import Base, engine, get_db
from .models import User, Item, Match, Claim
from .schemas import RegisterIn, LoginIn, ItemIn, ClaimIn, StatusIn
from .security import hash_password, verify_password, make_token
from .ai import analyze_item, explain_match, image_hint
from .matching import score_pair

Base.metadata.create_all(bind=engine)
app=FastAPI(title="FindIt AI",version="2.0.0")
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
UPLOAD_DIR=Path("uploads"); UPLOAD_DIR.mkdir(exist_ok=True)

def serialize_item(i):
    return {"id":i.id,"user_id":i.user_id,"item_type":i.item_type,"title":i.title,"description":i.description,
            "location":i.location,"category":i.category,"contact":i.contact,"image_path":i.image_path,
            "status":i.status,"ai_summary":i.ai_summary,"created_at":i.created_at.isoformat() if i.created_at else None}

@app.get("/")
def root(): return {"name":"FindIt AI","version":"2.0.0","docs":"/docs"}

@app.post("/auth/register")
def register(data:RegisterIn,db:Session=Depends(get_db)):
    if db.query(User).filter(User.email==data.email.lower()).first(): raise HTTPException(409,"Email already registered")
    u=User(name=data.name,email=data.email.lower(),password_hash=hash_password(data.password))
    db.add(u); db.commit(); db.refresh(u)
    return {"user_id":u.id,"name":u.name,"email":u.email,"token":make_token(u.id)}

@app.post("/auth/login")
def login(data:LoginIn,db:Session=Depends(get_db)):
    u=db.query(User).filter(User.email==data.email.lower()).first()
    if not u or not verify_password(data.password,u.password_hash): raise HTTPException(401,"Invalid email or password")
    return {"user_id":u.id,"name":u.name,"email":u.email,"is_admin":u.is_admin,"token":make_token(u.id)}

@app.post("/items")
def create_item(data:ItemIn, user_id:int=1, db:Session=Depends(get_db)):
    ai=analyze_item(data.title,data.description,data.location)
    item_data=data.model_dump()
    item_data["category"]=ai["category"]
    i=Item(user_id=user_id,**item_data,ai_summary=ai["summary"],ai_keywords=json.dumps(ai["keywords"]))
    db.add(i); db.commit(); db.refresh(i)
    return serialize_item(i)

@app.post("/items/{item_id}/image")
def image(item_id:int,image:UploadFile=File(...),db:Session=Depends(get_db)):
    i=db.get(Item,item_id)
    if not i: raise HTTPException(404,"Item not found")
    ext=Path(image.filename or "").suffix.lower()
    if ext not in {".jpg",".jpeg",".png",".webp"}: raise HTTPException(400,"Unsupported image type")
    name=f"{uuid.uuid4().hex}{ext}"; path=UPLOAD_DIR/name
    with path.open("wb") as f: shutil.copyfileobj(image.file,f)
    i.image_path=str(path); db.commit()
    return {"message":"Image saved","ai_note":image_hint(name)}

@app.get("/items")
def items(status="active", item_type=None, category=None, db:Session=Depends(get_db)):
    q=db.query(Item)
    if status!="all": q=q.filter(Item.status==status)
    if item_type: q=q.filter(Item.item_type==item_type)
    if category: q=q.filter(Item.category==category)
    return [serialize_item(i) for i in q.order_by(desc(Item.created_at)).all()]

@app.get("/items/{item_id}")
def item(item_id:int,db:Session=Depends(get_db)):
    i=db.get(Item,item_id)
    if not i: raise HTTPException(404,"Item not found")
    return serialize_item(i)

@app.patch("/items/{item_id}/status")
def status(item_id:int,data:StatusIn,db:Session=Depends(get_db)):
    i=db.get(Item,item_id)
    if not i: raise HTTPException(404,"Item not found")
    i.status=data.status; db.commit(); return {"message":"Status updated","status":i.status}

@app.get("/matches/{item_id}")
def matches(item_id:int,db:Session=Depends(get_db)):
    target=db.get(Item,item_id)
    if not target: raise HTTPException(404,"Item not found")
    opposite="found" if target.item_type=="lost" else "lost"
    candidates=db.query(Item).filter(Item.item_type==opposite,Item.status=="active",Item.id!=item_id).all()
    out=[]
    for c in candidates:
        s=score_pair(target,c)
        if s>=.18:
            explanation=explain_match(serialize_item(target),serialize_item(c),s)
            out.append({"item":serialize_item(c),"score":round(s,3),"explanation":explanation})
    return sorted(out,key=lambda x:x["score"],reverse=True)[:10]

@app.post("/items/{item_id}/claim")
def claim(item_id:int,data:ClaimIn,user_id:int=1,db:Session=Depends(get_db)):
    if not db.get(Item,item_id): raise HTTPException(404,"Item not found")
    c=Claim(item_id=item_id,claimant_user_id=user_id,message=data.message)
    db.add(c); db.commit(); db.refresh(c)
    return {"claim_id":c.id,"status":c.status}

@app.get("/claims")
def claims(db:Session=Depends(get_db)):
    return [{"id":c.id,"item_id":c.item_id,"claimant_user_id":c.claimant_user_id,"message":c.message,"status":c.status} for c in db.query(Claim).order_by(desc(Claim.created_at)).all()]

@app.get("/stats")
def stats(db:Session=Depends(get_db)):
    return {
        "total_items":db.query(Item).count(),
        "lost":db.query(Item).filter(Item.item_type=="lost").count(),
        "found":db.query(Item).filter(Item.item_type=="found").count(),
        "active":db.query(Item).filter(Item.status=="active").count(),
        "resolved":db.query(Item).filter(Item.status=="resolved").count(),
        "matches":db.query(Match).count(),
        "claims":db.query(Claim).count()
    }
