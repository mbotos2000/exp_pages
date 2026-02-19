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

for key in ["val_inc_nd","nr_contract","data_contract","beneficiar","cerere","numec","val_ET","ore_et","tarif_et","zimax_et","zimin_et",
    "val_a_3d","val_a_rel","zimax_a","zimin_a","zimax_IND","zimin_IND","val_bet","val_geo","val_dezveliri","nr_dezveliri","val_dezv_8"
    "zimax_geo","zimin_geo","val_et_finisaje","val_rel_struct","val_et_actualizat","zimin_rel","zimax_et_rel","termen_predare","termen_val","semnatura",
		   "total1","total2","total","adresant","mobilizare","constructie&adresa","gen",'den_obiectiv','adresa']:
    st.session_state.setdefault(key, '')
for key in ["val_inc_nd","val_ET","val_a_3d","val_a_rel","val_bet","val_geo","val_dezveliri","nr_dezveliri","val_dezv_8"
    "val_et_finisaje","val_rel_struct","val_et_actualizat","total1","total2","total"]:
    st.session_state.setdefault(key, 0.0)
for key in ["zimax_et","zimin_et","zimax_a","zimin_a",
    "zimax_IND","zimin_IND","zimax_geo","zimin_geo","zimin_rel","zimax_rel","zimin_et_rel","zimax_et_rel","nr_cladiri"]:
    st.session_state.setdefault(key, int(60.0))
keys_none=['cap2','cap3','cap4','resetare' ,'file','cond',"1_1","2_1","3_1","4_1","5_1"]
st.session_state["val_dezv_8"]="0.00"
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
                st.write('Scanare laser')
                st.text_area('Constructia si adresa: ', key='constructie&adresa')
                col1, col2, col3 = st.columns(3)
                with col1:
                 try:
                  aa=st.text_area('Mobilizare si deplasare la obiectiv: ',value=df.iloc[115, 8])
                 except:
                  aa=st.text_area('Mobilizare si deplasare la obiectiv: ',  value="0")
                 try:
                  bb=st.text_area('Scan 3D și generare nor de puncte: ',value=df.iloc[115, 8])
                 except:
                  bb=st.text_area('Scan 3D și generare nor de puncte: ',  value="0")
                with col2:            
                 st.selectbox('Durata de realizare a norului de puncte: ',range(1, 60),index=25,key='zimax_a')
                with col3:            
                 st.selectbox('Nu mai putin de: ',range(1, int(st.session_state['zimax_a'])-1),key='zimin_a')
                st.selectbox('Termen valabilitate',range(1, 60),index=8, key='termen_val')
                num_rows = st.selectbox("Selecteaza numarul de tipuri de releveu:", list(range(1, 5)),index=3)
                inputs = []
                for i in range(num_rows):
                 col1, col2, col3, col4 = st.columns(4)
                 row = {}
                 row["c1"] = col1.text_input(f" 3.{i+1} Tip releveu", key=f"{i}_1")
                 row["c2"] = col2.text_input(f" Valoare realizare releveu 3.{i+1}", key=f"{i}_2")
                 row["c3"] = col3.selectbox(f" Durata de realizare a cap 3.{i+1}",range(1, 60), key=f"{i}_3")
                 row["c4"] = col4.selectbox(f" Nu mai putin de: ",range(1, 60), key=f"{i}_4")
                 inputs.append(row)

    
    if (st.session_state.step >= 4)&(st.session_state['1_1']!=None):	
      _,_,_,_,_,_,template=load_ftp_file()
      st.session_state["mobilizare"]=format_number(aa)
      st.session_state['val_a_3d']=format_number(bb)
      for idx, row in enumerate(inputs):
        r_c1=row["c1"]
        r_c2=format_number(str(row["c2"]))
        r_c3=row["c3"]       
        r_c4=row["c4"]
		st.session_state.cap3i+=f"3.{idx+1} Elaborare releveu {r_c1} - {r_c2} RON + TVA;\n"
        st.session_state.note+= f"Termenul de elaborare pentru releveu {r_c1} este de maxim {r_c3} zile lucrătoare de la semnarea contractului și plata ratei 1, dar nu mai puțin de {r_c4} zile lucrătoare de la generarea norului de puncte.\n"
        

      keys_to_merge=["val_inc_nd","val_ET","val_bet","val_geo","val_dezveliri","val_a_3d","val_a_rel", "val_et_finisaje","val_rel_struct","val_et_actualizat",
                    "nr_contract","data_contract","beneficiar","cerere","numec",
                    "ore_et","tarif_et",
					 "zimax_et","zimin_et","zimax_a","zimin_a","zimax_IND","zimin_IND","zimax_geo","zimin_geo","zimin_rel","zimax_et_rel","zimax_rel","zimin_et_rel",
                     "termen_predare","termen_val","semnatura",
					 "total1","total2","total", "adresant","mobilizare","constructie&adresa","cap3i","note",'gen']

      document=MailMerge(template)
      for key in keys_to_merge:
                    document.merge(**{key: st.session_state[key]})
      document.write("oferta.docx")
      for key in ["cap3i","note"]:
                    st.session_state[key]="\n"
	  
      st.markdown(get_binary_file_downloader_html("oferta.docx", 'Word document'), unsafe_allow_html=True)
    
    submitted = st.form_submit_button("Next")
 # Logic AFTER the form
  if submitted:
    st.session_state.step += 1

        





