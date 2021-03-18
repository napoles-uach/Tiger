import streamlit as st
import graphistry
import pandas as pd
import streamlit.components.v1 as components
import pyTigerGraphBeta as tg
import flat_table
import plotly.express as px
#import mplleaflet
#import matplotlib.pyplot as plt
import base64
import plotly.express as px
from pxmap import px_static
from stvis import pv_static
from pyvis.network import Network

st.set_page_config(
  page_title='TIGERGRAPH APP HACK',
  layout="wide",
  page_icon=':tiger:'
  )


def call_host():
  graphistry.register(api=3, protocol="https", server="hub.graphistry.com", username="_______", password="______")
  TG_HOST = 'https://_______.i.tgcloud.io'
  #TG_HOST2 = '________'
  TG_USERNAME = '_____'
  TG_PASSWORD = '_______'
  TG_GRAPHNAME = '_________'
  TG_SECRET = '_____________'

  conn = tg.TigerGraphConnection(host=TG_HOST,username=TG_USERNAME,password=TG_PASSWORD,graphname=TG_GRAPHNAME,)
  conn.getToken(TG_SECRET)
  return conn

conn=call_host()




st.sidebar.title('Project: Covid19 exploration')
st.sidebar.header('Enter patient and contact information')

#col1, col2 = st.beta_columns(2)
#with col2:
pat_id=st.sidebar.number_input('Enter patient ID',value=4100000006,min_value=0)



@st.cache
def fun1():
  results = conn.runInstalledQuery("edgeCrawl")
  df = pd.DataFrame(results)
  data = flat_table.normalize(df) # Cleaning uo the data
  #st.write(data)
  g = graphistry.bind(source='@@edgeList.from_id', destination='@@edgeList.to_id').edges(data)
  iframe_url = g.plot(render=False)
  return iframe_url
iframe_url=fun1()


#------------------------------------subgraph-------------------------------------------
@st.cache
def fun3():
  results2 = conn.runInstalledQuery("allConnection",params={'p':pat_id})
  df2=pd.DataFrame(results2)
  data2 = flat_table.normalize(df2) # Cleaning uo the data
  #g2 = graphistry.bind(source='@@edgeList.from_id', destination='@@edgeList.to_id').edges(data2)
  #iframe_url2 = g2.plot(render=False)
  return data2

subnet_df=fun3()
#st.write(subnet_df)
got_net = Network(height='400px', width='1200px', bgcolor='white', font_color='gray')
#got_net.barnes_hut()

got_data = subnet_df
sources = got_data['@@edgeList.from_id']
targets = got_data['@@edgeList.to_id']

edge_data = zip(sources, targets)

for e in edge_data:
    src = e[0]
    dst = e[1]
    #w = e[2]

    got_net.add_node(src, src, title=src,color='orange')
    got_net.add_node(dst, dst, title=dst,color='violet')
    got_net.add_edge(src, dst )#value=w)


neighbor_map = got_net.get_adj_list()
got_net.show_buttons(filter_=['physics'])
for node in got_net.nodes:
    #node['title'] += ' Neighbors:<br>' + '<br>'.join(neighbor_map[node['id']])
    node['value'] = len(neighbor_map[node['id']])
    #node['size'] = 200
    #node['color'] = '#dd4b39'

#------------------------------------subgraph-------------------------------------------

def fun2():
  results4 = conn.runInstalledQuery("st2",params={'p':pat_id})
  df = pd.DataFrame(results4)
  if (bool(df['S1'][0][0]['attributes']["S1.@Loc"])):
    data = flat_table.normalize(df)
    data['lat']=data['S1.attributes.S1.@Loc.latitude']
    data['lon']=data['S1.attributes.S1.@Loc.longitude']
    return data

  else:
    st.error('No coordinates, choose another patient ID')
    st.stop()
  #data['lat']=data['S1.attributes.S1.@Loc.latitude']
  #data['lon']=data['S1.attributes.S1.@Loc.longitude']
  
d3=fun2()
#st.write('patient')
#d3


#---------------------------------------------------------------

##################
def nums():
  results6 = conn.runInstalledQuery("allConnection",params={'p':pat_id})
  df = pd.DataFrame(results6)
  data = flat_table.normalize(df)
#data['lat']=data['S1.attributes.S1.@Loc.latitude']
#data['lon']=data['S1.attributes.S1.@Loc.longitude']
#d3=data
#d3
  index_to_drop=data[data['@@edgeList.to_type']!='Patient'].index
  data.drop(index_to_drop, inplace = True)

  numeros=data['@@edgeList.to_id']
  numeros.drop_duplicates(keep = False, inplace = True)
#numeros=numeros.astype(int)
  numeros=numeros.to_list()
  return numeros

#-----------------actualiza coord--------------------------
numeros=nums()

options = st.sidebar.selectbox('select contact',numeros)
results5 = conn.runInstalledQuery("st2",params={'p':int(options)})

df5 = pd.DataFrame(results5)

if (bool(df5['S1'][0][0]['attributes']["S1.@Loc"]) ):
  data = flat_table.normalize(df5)
  data['lat']=data['S1.attributes.S1.@Loc.latitude']
  data['lon']=data['S1.attributes.S1.@Loc.longitude']
  d4=data
  d3=d3.append(d4)

#d3

#-----------------actualiza coord--------------------------

fig = px.scatter_mapbox(d3, lat=d3['lat'], lon=d3['lon'],opacity=0.4,color=d3['S1.v_id'],size=d3['index']+1)
#
#fig.update_layout(mapbox_style="carto-darkmatter")
#mapstyle=st.radio('chosse map style',['carto-positron','open-street-map','carto-darkmatter'])
fig.update_layout(mapbox_style='carto-positron')


################## Streamlit Stuff  ##################### 

col1, col2 ,col3 = st.beta_columns((0.5,3,1))
with col2:
  st.image('https://challengepost-s3-challengepost.netdna-ssl.com/photos/production/challenge_photos/001/380/923/datas/full_width.png')


with col2:
  st.markdown('## Dynamically Visualize South Korea COVID-19 data :mask: using TigerGraph , Graphistry  and Streamlit :tiger::chart::balloon:')

with col3:
  st.write('Made with :heart: by')
  st.write('José Manuel Nápoles')
  st.write('[@napoles3d]((https://twitter.com/napoles3d))')


components.iframe(iframe_url,width=1200, height=600)

with st.beta_expander('Subgraph'):
  st.write('Subgraph for patient:',pat_id)
  pv_static(got_net)
  '''
    This subgraph is made with a component developed especially for this hackaton.
    The component its called **stvis** and can be installed by:
    '''
  st.code('pip install stvis')
  st.write('https://github.com/napoles-uach/stvis')

with st.beta_expander('Map for Contacts'):
  px_static(fig,width=1200)
  '''
    This subgraph is made with a component developed especially for this hackaton.
    The component its called **pxmap** and can be installed by:
    '''
  st.code('pip install pxmap')
  st.write('https://github.com/napoles-uach/pxmap')








st.sidebar.markdown(''' 
This web app has been developed for the TIGERGRAPH WEB-APP HACK : FEB 22 - MAR 22, 2021, and it is based on the COVID19 Starter Kit.

''')

st.sidebar.image('https://streamlit.io/images/brand/streamlit-logo-secondary-colormark-darktext.png')
st.sidebar.image('https://dist.neo4j.com/wp-content/uploads/20190505065926/banner_transparent_colored.png')
st.sidebar.image('data:image/png;base64,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')


with st.sidebar.beta_expander("Credits"):
        """
        Although minimalist, this app, stvis and pxmap components are the result of weeks of work by:
        - [José Manuel Nápoles] (https://github.com/napoles-uach)
        
        The full code is provided as open source in github. 
        
            """
