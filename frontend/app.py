import os, requests, streamlit as st

API=os.getenv("FINDIT_API_URL","http://127.0.0.1:8000")
st.set_page_config(page_title="FindIt AI",page_icon="🔎",layout="wide")

if "user" not in st.session_state: st.session_state.user=None

def call(method,path,**kwargs):
    try:
        r=requests.request(method,API+path,timeout=30,**kwargs)
        if r.ok:return r.json()
        st.error(f"{r.status_code}: {r.text}")
    except Exception as e: st.error(f"Backend unavailable: {e}")
    return None

st.title("🔎 FindIt AI")
st.caption("AI-powered Lost & Found matching for campuses and communities.")

with st.sidebar:
    st.header("Account")
    if st.session_state.user:
        st.success(f"Hi, {st.session_state.user['name']}")
        if st.button("Logout"): st.session_state.user=None; st.rerun()
    else:
        tab1,tab2=st.tabs(["Login","Register"])
        with tab1:
            e=st.text_input("Email",key="le"); p=st.text_input("Password",type="password",key="lp")
            if st.button("Login"):
                u=call("POST","/auth/login",json={"email":e,"password":p})
                if u: st.session_state.user=u; st.rerun()
        with tab2:
            n=st.text_input("Name",key="rn"); e=st.text_input("Email",key="re"); p=st.text_input("Password",type="password",key="rp")
            if st.button("Create account"):
                u=call("POST","/auth/register",json={"name":n,"email":e,"password":p})
                if u: st.session_state.user=u; st.rerun()

menu=st.sidebar.radio("Navigate",["🏠 Home","📝 Report","🔎 Browse","🎯 Matches","📊 Dashboard"])

if menu=="🏠 Home":
    st.header("Find lost things faster.")
    st.write("Report a lost or found item. FindIt AI analyzes the report and ranks possible matches.")
    c1,c2,c3=st.columns(3)
    stats=call("GET","/stats") or {}
    c1.metric("Reports",stats.get("total_items",0)); c2.metric("Lost",stats.get("lost",0)); c3.metric("Found",stats.get("found",0))
    st.info("Tip: Include brand, color, model, unique marks and exact location for better matching.")

elif menu=="📝 Report":
    st.header("Create a report")
    if not st.session_state.user: st.warning("Login first to attach the report to your account.")
    with st.form("report"):
        typ=st.selectbox("Type",["lost","found"])
        title=st.text_input("Title",placeholder="Black HP laptop")
        desc=st.text_area("Detailed description",placeholder="Black HP laptop, silver logo, scratch near touchpad...")
        loc=st.text_input("Location",placeholder="Central Library")
        cat=st.selectbox("Category",["Other","Electronics","ID/Documents","Keys","Clothing","Bags","Books","Accessories","Wallet/Money"])
        contact=st.text_input("Contact (optional)")
        photo=st.file_uploader("Photo (optional)",type=["jpg","jpeg","png","webp"])
        go=st.form_submit_button("Submit report",type="primary")
    if go:
        if not title or not desc or not loc: st.warning("Title, description and location are required.")
        else:
            uid=st.session_state.user["user_id"] if st.session_state.user else 1
            item=call("POST","/items",params={"user_id":uid},json={"item_type":typ,"title":title,"description":desc,"location":loc,"category":cat,"contact":contact or None})
            if item:
                st.success(f"Report #{item['id']} created.")
                st.write("**AI category:**",item["category"]); st.write("**AI summary:**",item["ai_summary"])
                if photo: call("POST",f"/items/{item['id']}/image",files={"image":(photo.name,photo.getvalue(),photo.type)})

elif menu=="🔎 Browse":
    st.header("Recent reports")
    typ=st.selectbox("Filter",["all","lost","found"])
    items=call("GET","/items",params={"item_type":None if typ=="all" else typ}) or []
    for i in items:
        with st.container(border=True):
            st.subheader(f"{'🔴 Lost' if i['item_type']=='lost' else '🟢 Found'} — {i['title']}")
            st.write(i["description"])
            st.caption(f"📍 {i['location']} · 🏷️ {i['category']} · #{i['id']}")
            if i["contact"]: st.write(f"Contact: {i['contact']}")

elif menu=="🎯 Matches":
    st.header("Find possible matches")
    items=call("GET","/items") or []
    if not items: st.info("Create some reports first.")
    else:
        labels={f"#{i['id']} — {i['title']} ({i['item_type']})":i["id"] for i in items}
        chosen=st.selectbox("Report",list(labels))
        if st.button("Find AI matches",type="primary"):
            results=call("GET",f"/matches/{labels[chosen]}") or []
            if not results: st.info("No strong candidate found yet.")
            for r in results:
                with st.container(border=True):
                    st.subheader(f"{r['item']['title']} — {r['score']:.0%} match")
                    st.progress(min(r["score"],1.0))
                    st.write(r["item"]["description"])
                    st.caption(f"📍 {r['item']['location']} · {r['item']['category']}")
                    st.info(r["explanation"])
                    if st.session_state.user and r["item"]["item_type"]=="found":
                        msg=st.text_input("Why is this yours?",key=f"claim_{r['item']['id']}")
                        if st.button("Submit claim",key=f"claimbtn_{r['item']['id']}"):
                            call("POST",f"/items/{r['item']['id']}/claim",params={"user_id":st.session_state.user["user_id"]},json={"message":msg})
                            st.success("Claim submitted.")

elif menu=="📊 Dashboard":
    st.header("Community dashboard")
    s=call("GET","/stats") or {}
    a,b,c,d=st.columns(4)
    a.metric("Total",s.get("total_items",0)); b.metric("Lost",s.get("lost",0)); c.metric("Found",s.get("found",0)); d.metric("Resolved",s.get("resolved",0))
    st.write("### Recent reports")
    for i in (call("GET","/items") or [])[:10]:
        st.write(f"#{i['id']} — {i['title']} — {i['status']}")
