from __future__ import print_function
from io import BytesIO
from datetime import *
import streamlit as st
import pandas as pd
from pandas import *
from docx2python import docx2python
import os
import base64
import time
import ftplib
from mailmerge import MailMerge
from difflib import get_close_matches
import pickle
import string
from auth_simple import require_login
import hashlib
import time

def _hash(pwd: str) -> str:
    return hashlib.sha256(pwd.encode("utf-8")).hexdigest()

def _get_users():
    try:
        return st.secrets["users"]
    except Exception:
        return {}

def require_login(title="Login"):
    st.title(title)
    if "auth" not in st.session_state:
        st.session_state.auth = {"ok": False, "user": None, "name": None, "time": None}

    if st.session_state.auth["ok"]:
        with st.sidebar:
            if st.button("Logout"):
                st.session_state.auth = {"ok": False, "user": None, "name": None, "time": None}
                st.rerun()
        return st.session_state.auth["name"], st.session_state.auth["user"]

    users = _get_users()
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    if st.button("Login"):
        if u in users and _hash(p) == users[u]["hash"]:
            st.session_state.auth = {"ok": True, "user": u, "name": users[u]["name"], "time": time.time()}
            st.rerun()
        else:
            st.error("Invalid username or password")
            st.stop()

    st.stop()

def format_number(value: str) -> str:
    # 1. Trim spaces
    v = value.strip()

    # 2. Normalize decimal separator → use dot internally
    v = v.replace(',', '.')

    # 3. Convert to float
    num = float(v)

    # 4. Format with thousands separator and 2 decimals
    #    This creates: x,xxx,xxx.xx
    formatted = f"{num:,.2f}"

    # 5. Convert to European style: x.xxx.xxx,xx
    formatted = formatted.replace(",", "X")   # temporary
    formatted = formatted.replace(".", ",")   # dot → comma for decimals
    formatted = formatted.replace("X", ".")   # thousands separator

    return formatted
def load_ftp_file():
    # Establish FTP connection
    #ftp_server = ftplib.FTP("users.utcluj.ro", st.secrets['u'], st.secrets['p'])
    ftp_server = ftplib.FTP_TLS("users.utcluj.ro")
    ftp_server.login(user=st.secrets['u'], passwd=st.secrets['p'])
    ftp_server.prot_p()
    ftp_server.encoding = "utf-8"  # Force UTF-8 encoding
    ftp_server.cwd('./public_html')

    # Download CSV files
    
    # Download DOCX templates
    docx_files = {}
    for filename in ["template.docx","template1.docx","template2.docx","template3.docx","template4.docx","template5.docx","template6.docx"]:
        file_data = BytesIO()
        ftp_server.retrbinary(f"RETR {filename}", file_data.write)
        file_data.seek(0)  # Reset file pointer to the start
        docx_files[filename] = file_data
    # Close FTP connection
    ftp_server.quit()

    # Return downloaded files
    return ( 
        docx_files["template.docx"],
		docx_files["template1.docx"],
		docx_files["template2.docx"],
		docx_files["template3.docx"],
		docx_files["template4.docx"],
		docx_files["template5.docx"],
		docx_files["template6.docx"]  )
# Use a session state flag to control cache invalidation
name, user = require_login("🔐 App Login")
st.title("Dashboard")
st.success(f"Welcome, {name}!")


def get_binary_file_downloader_html(bin_file, file_label='File'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">Download {file_label}</a>'
    return href

def format_eu_number(value):
    # Convert input to integer
    n = int(value)
    # Format using Python's standard formatting
    formatted = f"{n:,.2f}"
    # Swap separators: , ↔ .
    formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")
    return formatted
if "step" not in st.session_state:
    st.session_state.step = 1
if "cap3" not in st.session_state:
    st.session_state.cap3 = 1
if "cap3i" not in st.session_state:
    st.session_state.cap3i = ''
if "note" not in st.session_state:
    st.session_state.note = ''
st.set_page_config(page_title="Exp_oferte",
    page_icon="🧭",
    layout="wide")

for key in ["nr_contract","data_contract","beneficiar","cerere","numec","val_ET","zimax_et","zimin_et",
           "termen_predare","termen_val","semnatura",
		   "adresant","constructie&adresa","gen",'den_obiectiv','adresa']:
    st.session_state.setdefault(key, '')
for key in ["val_ET"]:
    st.session_state.setdefault(key, 0.0)
for key in ["zimax_et","zimin_et","nr_cladiri"]:
    st.session_state.setdefault(key, int(60.0))
keys_none=['cap2','cap3','cap4','resetare' ,'file','cond',"1_1","2_1","3_1","4_1","5_1"]

for key in keys_none:
    st.session_state.setdefault(key, None)
st.session_state['file'] = st.file_uploader("Incarca centralizatorul in excel", type="xlsx")
if st.button("Nu am oferta in excell!"):
	st.session_state['cond']=1
if st.session_state['file']!=None or st.session_state['cond']!=None:
  if st.session_state['file']:
        df = pd.read_excel(st.session_state['file'], header=None)
        #st.dataframe(df)
        st.success("Datele au fost citite din fisierul excell!")

  st.title("Generare oferta")
  st.write('{:%d-%b-%Y}'.format(date.today()))
  
  with st.form('Inregistrare cerere'):
    st.header('Inregistrare cerere')
    if st.session_state.step >= 1:
        st.write('Oferta expertiza')
        c1,c2 =st.columns(2)
        with c1:          
          st.text_area('Numar oferta',key='nr_contract')
        with c2:
          d_com=st.date_input("Data ofertei",date.today())
          st.session_state['data_contract']=str(d_com)     
			
    if st.session_state.step >= 2:
                st.write('Date despre beneficiar si cererea depusa:')
                g=st.selectbox("Domnului sau doamnei?",["","d-nei","d-lui"])
                st.session_state['gen']=g		
                try:
                 st.text_area('Persoana careia ii este adresata oferta',value=df.iloc[2, 0],key='adresant')
                except:
                 st.text_area('Persoana careia ii este adresata oferta',key='adresant')
                try:
                 st.text_area('Beneficiar',value=df.iloc[0, 0],key='beneficiar')
                except:
                 st.text_area('Beneficiar',key='beneficiar')
                try:
                 st.text_area('Denumire contract',value=df.iloc[1, 0],key='numec')
                except:
                 st.text_area('Denumire contract',key='numec')
                d=st.selectbox("Oferta va fi semnata de:", ["Dr. ing. Ovidiu Prodan"],
							 placeholder="Selecteaza din lista sau adauga persoana care va semna oferta",accept_new_options=True)
                st.session_state['semnatura']=d
   
    if (st.session_state.step >= 3):
                st.write('Expertiză tehnica vecinatati')
                st.text_area('Adresa pentru expertiza', key='adresa')
                st.selectbox('Numar cladiri din vecinatate pentru care se face expertiza: ',range(1, 10),key='nr_cladiri')
                try:
                 aa=st.text_area('Valoare expertiza vecinatati',value=df.iloc[113, 8])
                except:
                 aa=st.text_area('Valoare expertiza vecinatati', value="0")                
                colA, colB = st.columns(2)
                with colA:
                 st.text_area('Numar ore necesar verificare',value="8",key='ore_et')
                 st.selectbox('Durata de realizare a expertizei tehnice: ',range(1, 60),index=25,key='zimax_et')
                with colB:
                 st.text_area('Tarif verificare',value="375",key='tarif_et')                         
                 st.selectbox('Nu mai putin de: ',range(1, int(st.session_state['zimax_et'])-1),key='zimin_et')
                st.selectbox('Termen valabilitate',range(1, 60),index=8, key='termen_val')
    
    if (st.session_state.step >= 4):	
      _,_,_,_,_,template,_=load_ftp_file()
      st.session_state["val_ET"]=format_number(aa)
      keys_to_merge=["val_ET",
                    "nr_contract","data_contract","beneficiar","cerere","numec",                 
					 "zimax_et","zimin_et",
                     "termen_predare","termen_val","semnatura",
					 "adresant",'gen','den_obiectiv']
      document=MailMerge(template)
      for key in keys_to_merge:
                    document.merge(**{key: st.session_state[key]})
      document.write("oferta.docx")
      st.markdown(get_binary_file_downloader_html("oferta.docx", 'Word document'), unsafe_allow_html=True)
    
    submitted = st.form_submit_button("Next")
 # Logic AFTER the form
  if submitted:
    st.session_state.step += 1

        




