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
def float_to_eu(value: float) -> str:
    formatted = f"{value:,.2f}"
    return formatted.replace(",", "X").replace(".", ",").replace("X", ".")
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
    for filename in ["template.docx","template_fMAT.docx","template_fGEO.docx","template_FND.docx","template-gND.docx"]:
        file_data = BytesIO()
        ftp_server.retrbinary(f"RETR {filename}", file_data.write)
        file_data.seek(0)  # Reset file pointer to the start
        docx_files[filename] = file_data
    # Close FTP connection
    ftp_server.quit()
    st.session_state.step = 1
    # Return downloaded files
    return (docx_files["template.docx"],["template_fMAT.docx"],["template_fGEO.docx"],["template_FND.docx"],["template-gND.docx"]
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
                st.write('Date despre compania si cererea depusa:')
                try:
                 st.text_area('Compania: ',value=df.iloc[0, 0],key='beneficiar')
                except:
                 st.text_area('Compania: ',key='beneficiar')
                g=st.selectbox("Domnului sau doamnei?",["","d-nei","d-lui"])
                st.session_state['gen']=g
                try:
                 st.text_area('Persoana careia ii este adresata oferta',value=df.iloc[2, 0],key='adresant')
                except:
                 st.text_area('Persoana careia ii este adresata oferta',key='adresant')
                try:
                 st.text_area('Obiect oferta',value=df.iloc[1, 0],key='numec')
                except:
                 st.text_area('Obiect oferta',key='numec')
                d=st.selectbox("Oferta va fi semnata de:", ["Dr. ing. Ovidiu Prodan","Dr. ing. Iulia Prodan","ing. Anamaria Avram", "ing. Marius Monda"],
							 placeholder="Selecteaza din lista sau adauga persoana care va semna oferta",accept_new_options=True)
                st.session_state['semnatura']=d
    if (st.session_state.step >= 3):
                st.write('1. Expertiză tehnică')

                try:
                 st.text_area('Valoare expertiza tehnica',value=str(format_eu_number(df.iloc[113, 8])), key='val_ET')
                except:
                 st.text_area('Valoare expertiza tehnica', value=0.0, key='val_ET')                
                colA, colB = st.columns(2)
                with colA:
                 st.text_area('Numar ore necesar verificare',value="8",key='ore_et')
                 st.selectbox('Durata de realizare a expertizei tehnice: ',range(1, 60),index=25,key='zimax_et')
                with colB:
                 st.text_area('Tarif verificare',value="450",key='tarif_et')                         
                 st.selectbox('Nu mai putin de: ',range(1, 59),key='zimin_et')
                #st.selectbox('Termen valabilitate',range(1, 60),index=8, key='termen_val')  

    if (st.session_state.step >= 4) :
                col1, col2, col3 = st.columns(3)
                with col1:            
                 try:
                  st.text_area('2.1 Scan 3D și generare nor de puncte: ',value=str(format_eu_number(df.iloc[115, 8])), key='val_a_3d')
                 except:
                  st.text_area('2.1 Scan 3D și generare nor de puncte: ',  value=0.0,key='val_a_3d')
                 try:
                  st.text_area('2.2 Elaborare planuri si sectiuni de releveu : ',value=str(format_eu_number(df.iloc[113, 8])), key='val_a_rel')       
                 except:
                  st.text_area('2.2 Elaborare planuri si sectiuni de releveu : ', value=0.0, key='val_a_rel')       
                with col2:            
                 st.selectbox('Durata de realizare a releveului: ',range(1, 60),index=25,key='zimax_a')
                with col3:            
                 st.selectbox('Nu mai putin de: ',range(1, int(st.session_state['zimax_a'])-1),key='zimin_a')
					
    if (st.session_state.step >= 5):		
                st.write('3. Investigații prin încercări nedistructive la elementele structurale în vederea determinării modului de alcătuire și armare ')
                try:
                 st.text_area('3. Investigații prin încercări nedistructive : ',value=str(format_eu_number(df.iloc[115, 8])), key='val_inc_nd') 
                except:
                 st.text_area('3. Investigații prin încercări nedistructive : ', value=0.0,key='val_inc_nd')
                st.selectbox('Durata de realizare a incercarilor nedestructive: ',range(1, 60), index=25,key='zimax_IND')
                st.selectbox('Nu mai putin de: ',range(1,int(st.session_state['zimax_IND'])-1),key='zimin_IND')
		
    if (st.session_state.step >= 6):
                st.write('4. Teste pe betonul pus în operă prin extragere și testare carote ')
                try:
                 st.text_area('4. Teste pe betonul pus în operă  : ',value=str(format_eu_number(df.iloc[118, 8])), key='val_bet')
                except:
                 st.text_area('4. Teste pe betonul pus în operă  : ',  value=0.0,key='val_bet')
                
    if (st.session_state.step >= 7):
                st.write('5. Studiu Geotehnic și dezveliri la nivelul fundațiilor')
                try:
                 st.text_area(' Studiu Geotehnic : ',value=str(format_eu_number(df.iloc[119, 8])), key='val_geo') 
                except:
                 st.text_area(' Studiu Geotehnic : ',  value=0.0, key='val_geo') 
                try:
                 st.text_area(' Dezveliri : ',value=str(format_eu_number(df.iloc[119, 8])), key='val_dezveliri')
                except:
                 st.text_area(' Dezveliri : ', value=0,key='val_dezveliri')
                
                st.selectbox('Numarul minim de dezveliri: ',range(1, 60),index=8, key='nr_dezveliri')
                st.selectbox('Durata de realizare a studiului geotehnic: ',range(1, 60),index=30, key='zimax_geo')
                st.selectbox('Nu mai putin de: ',range(1, int(st.session_state['zimax_geo'])-1),key='zimin_geo')
                st.selectbox('Termen predare: ',range(1, 60),index=20, key='termen_predare')
                st.selectbox('Termen valabilitate oferta ',range(1, 60),index=8, key='termen_val')		
    if (st.session_state.step >= 15556):
                try:
                 st.text_area(' Realizare lucrări de decopertare finisaje interioare : ',value=str(format_eu_number(df.iloc[121, 8])), key='val_et_finisaje') 
                except:
                 st.text_area(' Realizare lucrări de decopertare finisaje interioare : ', value='0.0', key='val_et_finisaje') 
                try:
                 st.text_area(' Elaborare releveu structural al construcției : ',value=str(format_eu_number(df.iloc[116, 8])), key='val_rel_struct') 
                except:
                 st.text_area(' Elaborare releveu structural al construcției : ', value='0.0',key='val_rel_struct')      
                try:
                 st.text_area(' Actualizare expertiză tehnică   : ',value=str(format_eu_number(df.iloc[122, 4])), key='val_et_actualizat') 
                except:
                 st.text_area(' Actualizare expertiză tehnică   : ',  value='0.0',key='val_et_actualizat') 
                st.selectbox('Durata de realizare a releveului structural este de maxim: ',range(1, 60),index=30, key='zimax_rel')
                st.selectbox('Nu mai putin de: ',range(1, int(st.session_state['zimax_rel'])-1),index=25,key='zimin_rel')          
                st.selectbox('Durata de realizare a actualizării expertizei tehnice : ',range(1, 60),index=30, key='zimax_et_rel')
                st.selectbox('Nu mai putin de: ',range(1, int(st.session_state['zimax_et_rel'])-1),key='zimin_et_rel')
                st.selectbox('Termen predare: ',range(1, 60),index=20, key='termen_predare')
                st.selectbox('Termen valabilitate oferta ',range(1, 60),index=8, key='termen_val')
   
    if (st.session_state.step >= 8):	
      template=load_ftp_file()	  
      try:
       st.session_state["val_dezv_8"]=int(st.session_state["nr_dezveliri"])*float(st.session_state["val_dezveliri"].replace(".", "").replace(",", "."))
      except:
       st.session_state["val_dezv_8"]=0.00
      st.session_state["total1"]=float(st.session_state["val_ET"].replace(".", "").replace(",", "."))+float(st.session_state["val_a_3d"].replace(".", "").replace(",", "."))+float(st.session_state["val_a_rel"].replace(".", "").replace(",", "."))+ float(st.session_state["val_inc_nd"].replace(".", "").replace(",", "."))+float(st.session_state["val_bet"].replace(".", "").replace(",", "."))+float(st.session_state["val_geo"].replace(".", "").replace(",", "."))+st.session_state["val_dezv_8"]
      #st.session_state["total2"]=float(st.session_state["val_et_finisaje"].replace(".", "").replace(",", "."))+float(st.session_state["val_rel_struct"].replace(".", "").replace(",", "."))+float(st.session_state["val_et_actualizat"].replace(".", "").replace(",", "."))
      st.session_state["total"]=st.session_state["total1"]#+st.session_state["total2"]
      st.session_state["val_dezv_8"]=float_to_eu(st.session_state["val_dezv_8"])
      st.session_state["total1"]=float_to_eu(st.session_state["total1"])
      #st.session_state["total2"]=float_to_eu(st.session_state["total2"])
      st.session_state["total"]=float_to_eu(st.session_state["total"])
      keys_to_merge=["val_inc_nd","val_ET","val_bet","val_geo","val_dezveliri","val_a_3d","val_a_rel", "val_et_finisaje","val_rel_struct","val_et_actualizat",
                    "nr_contract","data_contract","beneficiar","cerere","numec",
                    "ore_et","tarif_et",
					 "zimax_et","zimin_et","zimax_a","zimin_a","zimax_IND","zimin_IND","zimax_geo","zimin_geo","zimin_rel","zimax_et_rel","zimax_rel","zimin_et_rel",
                     "nr_dezveliri","val_dezv_8",
                     "termen_predare","termen_val","semnatura",
					 "total1","total2","total", "adresant",'gen','den_obiectiv']

      document=MailMerge(template)
      for key in keys_to_merge:
                    document.merge(**{key: st.session_state[key]})
      document.write("oferta.docx")
      st.markdown(get_binary_file_downloader_html("oferta.docx", 'Word document'), unsafe_allow_html=True)
    submitted = st.form_submit_button("Next")
 # Logic AFTER the form
  if submitted:
    st.session_state.step += 1

        




