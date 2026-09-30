import json, os, secrets
from pathlib import Path
from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from .database import init_db, connect, now
from .auth import hash_password, verify_password, create_session, get_user, logout, make_jwt_like
from .schemas import RegisterIn, LoginIn, HomeIn, PartyIn, JewelryIn
from .services.gemini_service import GeminiService

BASE=Path(__file__).resolve().parent.parent
load_dotenv(BASE/".env")
os.environ.setdefault("DATABASE_PATH", str(BASE/"pocketsmart.db"))
init_db()
app=FastAPI(title="PocketSmart AI", version="1.0.0")
app.mount("/static", StaticFiles(directory=str(BASE/"static")), name="static")
templates=Jinja2Templates(directory=str(BASE/"templates"))
ai=GeminiService()

@app.get("/", response_class=HTMLResponse)
def home(request: Request): return templates.TemplateResponse("index.html", {"request":request,"user":get_user(request)})
@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request): return templates.TemplateResponse("register.html", {"request":request,"user":get_user(request)})
@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request): return templates.TemplateResponse("login.html", {"request":request,"user":get_user(request)})
@app.post("/register")
def register(username: str=Form(...), email: str=Form(...), password: str=Form(...)):
    conn=connect()
    try:
        conn.execute("INSERT INTO users(username,email,password_hash,created_at) VALUES (?,?,?,?)",(username.strip(),email.strip().lower(),hash_password(password),now())); conn.commit()
    except Exception:
        conn.close(); return RedirectResponse("/register?error=Username+or+email+already+exists",status_code=303)
    user=conn.execute("SELECT id FROM users WHERE username=?",(username.strip(),)).fetchone(); conn.close()
    token=create_session(user["id"]); r=RedirectResponse("/dashboard",status_code=303); r.set_cookie("pocketsmart_session",token,httponly=True,samesite="lax"); return r
@app.post("/login")
def login(username: str=Form(...), password: str=Form(...)):
    conn=connect(); user=conn.execute("SELECT * FROM users WHERE username=?",(username.strip(),)).fetchone(); conn.close()
    if not user or not verify_password(password,user["password_hash"]): return RedirectResponse("/login?error=Invalid+username+or+password",status_code=303)
    token=create_session(user["id"]); r=RedirectResponse("/dashboard",status_code=303); r.set_cookie("pocketsmart_session",token,httponly=True,samesite="lax"); return r
@app.get("/logout")
def logout_route(request:Request):
    logout(request.cookies.get("pocketsmart_session")); r=RedirectResponse("/login",status_code=303); r.delete_cookie("pocketsmart_session"); return r

def protected(request):
    user=get_user(request)
    if not user: raise HTTPException(401,"Please sign in")
    return user

def save_rec(user_id,category,data,result):
    conn=connect(); cur=conn.execute("INSERT INTO recommendations(user_id,category,request_json,result_json,created_at) VALUES (?,?,?,?,?)",(user_id,category,json.dumps(data),json.dumps(result),now())); conn.commit(); rid=cur.lastrowid; conn.close(); return rid

@app.get("/dashboard",response_class=HTMLResponse)
def dashboard(request:Request):
    user=protected(request); conn=connect(); rows=conn.execute("SELECT * FROM recommendations WHERE user_id=? ORDER BY id DESC LIMIT 5",(user['id'],)).fetchall(); conn.close();
    return templates.TemplateResponse("dashboard.html",{"request":request,"user":user,"recent":rows})
@app.get("/planner/home",response_class=HTMLResponse)
def home_planner(request:Request): return templates.TemplateResponse("home_planner.html",{"request":request,"user":protected(request)})
@app.get("/planner/party",response_class=HTMLResponse)
def party_planner(request:Request): return templates.TemplateResponse("party_planner.html",{"request":request,"user":protected(request)})
@app.get("/planner/jewelry",response_class=HTMLResponse)
def jewelry_planner(request:Request): return templates.TemplateResponse("jewelry_planner.html",{"request":request,"user":protected(request)})
@app.get("/history",response_class=HTMLResponse)
def history(request:Request):
    user=protected(request); conn=connect(); rows=conn.execute("SELECT * FROM recommendations WHERE user_id=? ORDER BY id DESC",(user['id'],)).fetchall(); conn.close();
    return templates.TemplateResponse("history.html",{"request":request,"user":user,"history":rows})
@app.get("/recommendation/{rid}",response_class=HTMLResponse)
def recommendation(request:Request,rid:int):
    user=protected(request); conn=connect(); row=conn.execute("SELECT * FROM recommendations WHERE id=? AND user_id=?",(rid,user['id'])).fetchone(); conn.close()
    if not row: raise HTTPException(404,"Recommendation not found")
    result=json.loads(row['result_json']); return templates.TemplateResponse("recommendation.html",{"request":request,"user":user,"row":row,"result":result})
@app.get("/testimonials",response_class=HTMLResponse)
def testimonials(request:Request): return templates.TemplateResponse("testimonials.html",{"request":request,"user":get_user(request)})

@app.post("/generate-home")
def generate_home(request:Request, payload:HomeIn):
    user=protected(request); data=payload.model_dump(); data["rooms"]=payload.rooms; result=ai.home(data); rid=save_rec(user['id'],'Home Interior',data,result); return {"id":rid,"result":result}
@app.post("/generate-party")
def generate_party(request:Request, payload:PartyIn):
    user=protected(request); data=payload.model_dump(); result=ai.party(data); rid=save_rec(user['id'],'Party Planning',data,result); return {"id":rid,"result":result}
@app.post("/generate-jewelry")
async def generate_jewelry(request:Request,budget:float=Form(...),occasion:str=Form("Birthday"),style:str=Form("Elegant"),notes:str=Form(""),outfit:UploadFile|None=File(None)):
    user=protected(request); image_bytes=await outfit.read() if outfit and outfit.filename else None; mime=outfit.content_type if outfit else "image/jpeg"; data={"budget":budget,"occasion":occasion,"style":style,"notes":notes,"image_uploaded":bool(image_bytes)}; result=ai.jewelry(data,image_bytes,mime); rid=save_rec(user['id'],'Jewelry',data,result); return RedirectResponse(f"/recommendation/{rid}",status_code=303)
@app.post("/api/generate-jewelry")
async def api_generate_jewelry(request:Request,budget:float=Form(...),occasion:str=Form("Birthday"),style:str=Form("Elegant"),notes:str=Form(""),outfit:UploadFile|None=File(None)):
    user=protected(request); image_bytes=await outfit.read() if outfit and outfit.filename else None; data={"budget":budget,"occasion":occasion,"style":style,"notes":notes,"image_uploaded":bool(image_bytes)}; result=ai.jewelry(data,image_bytes,outfit.content_type if outfit else "image/jpeg"); rid=save_rec(user['id'],'Jewelry',data,result); return {"id":rid,"result":result}

@app.post("/token")
def token(form: LoginIn):
    conn=connect(); user=conn.execute("SELECT * FROM users WHERE username=?",(form.username,)).fetchone(); conn.close()
    if not user or not verify_password(form.password,user['password_hash']): raise HTTPException(401,"Incorrect credentials")
    return {"access_token":make_jwt_like(user['id'],os.getenv('SECRET_KEY','dev-secret')),"token_type":"bearer"}
@app.get("/session-info")
def session_info(request:Request):
    user=get_user(request); return {"logged_in":bool(user),"user_id":user['id'] if user else None,"username":user['username'] if user else None}
@app.get("/session-data")
def session_data(request:Request):
    user=protected(request); conn=connect(); count=conn.execute("SELECT COUNT(*) FROM recommendations WHERE user_id=?",(user['id'],)).fetchone()[0]; conn.close(); return {"user_id":user['id'],"recommendation_count":count}
@app.get("/startup")
def startup(): return {"status":"ready","app":"PocketSmart AI"}
@app.get("/health")
def health(): return {"status":"ok"}
