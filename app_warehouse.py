# -*- coding: utf-8 -*-
"""
Created on Tue Feb 16 10:48:19 2021

@author: laura.woznialis
"""
import os
os. getcwd()
os.chdir('C:/Users/laura.woznialis.EFESO/Documents/App - Warehouse Picking Optimisation/Streamlit-training-warehouse-optimisation')

############################################################################
############################################################################
###############                LIBRARIES                       #############

import streamlit as st
import numpy as np
import pandas as pd
from ast import literal_eval
import plotly.express as px
import itertools
import session_state as state
     
#from scipy.cluster.vq import kmeans2, whiten
from random import randrange
from datetime import timedelta
from datetime import datetime
import random

from scipy.spatial.distance import pdist
from scipy.cluster.hierarchy import ward, fcluster



############################################################################
############################################################################
###############              PAGE   SETUP                      #############


NUM_SECTIONS = 60 
st.set_page_config(page_title='Warehouse Optimisation', page_icon='assets/logo_small.png',
                   layout='centered', initial_sidebar_state='collapsed')

############################################################################

session_state = state.get(sections=[False for i in range(NUM_SECTIONS)],
                          survived_clicked=False, test_clicked=False)

def continue_button(step):
    """Add a "Continue" button at the beginning of a new section."""
    if not session_state.sections[step] and not st.button('Continue', key=f'cont-{step}'):
        st.stop()
    session_state.sections[step] = True

############################################################################

session_state_xmas = state.get(sections=[False for i in range(NUM_SECTIONS)],
                          survived_clicked=False, test_clicked=False)

def continue_button_xmas(step):
    """Add a "Continue" button at the beginning of a new section."""
    if not session_state_xmas.sections[step] and not st.button('Show me! ', key=f'cont-{step}'):
        st.stop()
    session_state_xmas.sections[step] = True



############################################################################
############################################################################
###############   READING DATA  &  SETTING  UP PARAMETHERS     #############


dataset     = pd.read_csv('final_dataset_for_optimisation.csv')
nodes = pd.read_csv("df_nodes.csv")
#nodes = nodes.rename(columns={'x': 'y', 'y': 'x'})
#nodes.y = nodes.y + 5
#nodes = nodes.append({"nodeID":999, "x": 0, "y":0, "CorrID":0},ignore_index=True)
#nodes.to_csv("df_nodes.csv", index=False)
# =============================================================================
# 
# =============================================================================


def random_date(start, end):
    """
    This function will return a random datetime between two datetime 
    objects.
    """
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return start + timedelta(seconds=random_second)



random.seed(2021)
list_of_dates = list()
dstart = datetime.strptime('1/2/2021 9:00 AM', '%m/%d/%Y %I:%M %p')
dend   = datetime.strptime('1/2/2021 11:30 AM', '%m/%d/%Y %I:%M %p')


# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================
# TESTING THE CODE - Time-In-Full
# remove after 
# =============================================================================
# dataset1 = dataset.loc[dataset["orders_id"] < 23]
# dataset2 = dataset.loc[dataset["orders_id"] > 142]
# dataset2["orders_id"] = list(range(23,30))
# dataset = dataset1.append(dataset2)
# dataset.orders_id.nunique()
# 
# random.seed(2021)
# list_of_dates = list()
# dstart = datetime.strptime('1/2/2021 9:00 AM', '%m/%d/%Y %I:%M %p')
# dend   = datetime.strptime('1/2/2021 9:30 AM', '%m/%d/%Y %I:%M %p')
# 
# =============================================================================

# =============================================================================
# =============================================================================
# =============================================================================
# =============================================================================

# this is needed because python incorrectly reads the date - need to investigate 

dataset.drop("date", inplace=True, axis=1)
date_byorder = dataset.copy()
date_byorder = date_byorder[["orders_id"]].drop_duplicates(['orders_id'], keep='first')


# =============================================================================
#---------------      assign shiping date      -------    
# will be done once on base dataset
list_of_dates = list()
for i in range(0, len(date_byorder.orders_id.unique())):
    list_of_dates.append(random_date(dstart, dend))


date_byorder["date"] = list_of_dates
dataset = pd.merge(dataset, date_byorder, on = "orders_id" )
#dataset.to_csv("final_dataset_for_optimisation.csv", index=False)

# =============================================================================
# 
# =============================================================================





# Parameters for travelling salesman
y_high=nodes.y.max() +1  # the position where we can pass the shelfs and change the hallway
y_low=4                  # the position where we can pass the shelfs and change the hallway
Loc_orn = [0, 0, 0] 			# Origin Location
orders_number = 3 			# Number of orders per wave
start_loc = [0,0,0]

# Parameters for Clustering 
distance_threshold = 40
clust_start = 0
wave_start=0

 
# Create lists to store results
list_wid, list_dst, list_route, list_ord = [], [], [], []



############################################################################
############################################################################
###############   INTRODUCTION FOR WAREHOUSE OPTIMISATION      #############


st.image('assets/2_picking_in_warehouse.jfif' ,  width=700)
st.title("Welcome to the Warehouse Picking Optimisation")
st.write(''' 
Warehouse optimization is key to the efficient operation of warehouses of all
 sizes. A disciplined process, **warehouse optimization includes automation** and
 a determination of **how to save time, space, and resources**. 
         

## Today we will focus on 2 parts: 

>* **Part 1**: Review current Warehouse Picking Optimisation - understand what hides behind the WMS picking optimisation and how it works
>* **Part 2**: Exploring ways to improve overall performance. How can we add **Waving Optimisation** and get exponentally growing benefits?

# 
        ''')
        

st.warning('''**Disclaimer**
           
This optmization is built for old fashioned 
picking setup and for training purposes **only**. 



        ''')


#---------------------------------------------------------------------------
continue_button(0)


#st.header('')
#st.title('')
st.write('''
        ## What is it all about?

        In a Distribution Center (DC), walking time from one location to another 
        during picking route can account for 60% to 70% of operator’s working time.
        
        **Reducing this walking time is the most effective way to increase your DC 
        overall productivity**.
        ''')

       

st.image('assets/one-by-one piskup.png', width = 700, caption="Picking routes for three orders")
##st.warning('''  **Travelling is 60%-70% of labor cost**''')
 

st.write('''
        ## Why picking optimisation matters? 

        ### Higher revenue
        the more goods you can move through your warehouse, the more revenue 
        you can generate in the result.

        
        ### Improved customer experience
        customers receive their products faster, which increases their 
        satisfaction with your service and makes them return for new purchases.  ''')


#---------------------------------------------------------------------------
continue_button(1)


############################################################################
############################################################################
###############         DATA NEEDED FOR ANALYSIS               #############

     
st.header('') 
st.header('What will we need for the analysis?')      
st.header('') 
################## Product list
col1, mid, col2 = st.beta_columns([1,2,20])
with col1:
    st.image('assets/products_on_shelf.jpg', width=75)
with col2:
    st.write(''' 
             ### Product list
             A list of products that are available in the warehouse.''')        
        
               
################## Storage mapping
col1, mid, col2 = st.beta_columns([1,2,20])
with col1:
    st.image('assets/location mapping.png', width=86)
with col2:
    st.write(''' 
             ### Storage mapping
             We need a mapping of products and their storage locations with 
             2-D coordinates. This information will be crucial in measuring the
             walking distance.''')        
        
             
################## Order information
col1, mid, col2 = st.beta_columns([1,2,20])
with col1:
    st.image('assets/order_editor.png', width=80)
with col2:
    st.write(''' 
             ### Order information
             Information about the orders that need to be assembled. 
             Order lines can be extracted from your WMS SQL database''')        
        
        
#---------------------------------------------------------------------------
continue_button(2)

st.write('''
        ## What data do we have?

        Let's see!
                       
        ''')
        
if st.checkbox('Show dataset'):
    st.dataframe(dataset)
             


#---------------------------------------------------------------------------
#continue_button(3)

st.write('''
       * We have 150 unique orders (orders_id)
       * 287 unique SKUs (itemID)
       * Each order has on average 3 different SKUs. 
       
       ## 

       Let's also check the distribution of orders! 
       
       From below graph we can also see that there more than 50 orders with 1 SKU only
       and only 3 order with 7 different products: 
        ''')
        

#### Plot histogram
# average SKUs per order          
SKUs_per_order = pd.DataFrame(dataset["orders_id"].value_counts())
SKUs_per_order = SKUs_per_order.rename(columns={"orders_id": "Unique SKUs per order"}) 

st.plotly_chart(px.histogram(SKUs_per_order, x="Unique SKUs per order", labels={'count':'Number of orders'}))


#---------------------------------------------------------------------------
continue_button(4)



############################################################################
############################################################################
###############         INFORMATION ABOUT THE WAREHOUSE        #############

st.write('''
        ## Few notes about our Warehouse:
                      
        * 18 Aisles
        * 9 Hallways through which we can reach the products
        * Each blue dot represents the position from which the picker can take the goods
        * Picking journey starts and ends at Depot (0,0)
        * The values on x and y axes represent distance in meters from the Depot 
        
        ''')

st.title("")
st.image('assets/our warehouse.png' ,  width=700, caption="2-D overview of the warehouse")
   

#---------------------------------------------------------------------------
continue_button(5)


############################################################################
############################################################################
###############            BUILDING THE MODEL                  #############

st.title("We are all set to build the model! ")
st.write('''
        Our aim is to **increase efficiency** and **decrease time** needed to process the order. 
        One way of achieving it is by minimizing the walking distance. 
        
       
        Together we can build a tool from scratch that will help us to that! 
        ''')
        
        
        
st.write('''
        ### Our assumptions 
        1. All orders have the same importance 
        2. Small and light dimension items 
        3. Picking cart of capacity up to 10 orders
        4. Picking route starts and ends at the depot
        ''')



st.title("")
st.image('assets/lets do this together.png', width = 600, caption="Dont worry, we will build all the steps together")
 


#---------------------------------------------------------------------------
continue_button(6)


############################################################################
############################################################################
###############          WAVES PICKING - INTRODUCTION          #############


st.header('')   
st.image('assets/waves.jpg' ,  width=700)
st.write('''
        ## Waves picking 

        This method is used to combine orders into small sets called “waves” based on some shared parameters. 
        Typically, orders are picked one by one without route optimization.
        The warehouse manager combines orders together, or WMS/ERP does the same automatically.
        
        
        ### Waves picking is good for
        * Medium and large warehouses (distribution centers)
        * Warehouses with medium/large numbers of SKUs
        * Orders can be filtered by some standard parameters
        * The products have a wide range of sizes
        ###
        ''')
        
        
continue_button(7)
st.write('''
        ## Waves picking based on the delivery date

        Imagine you have 20 orders from your website

        * 8 need to be delivered tomorrow
        * 10 need to be delivered end of the week
        * 2 need to be delivered next week
        
        ''')
        
st.image('assets/Calendar_orders.png' ,  width=700)     
        
st.write('''        
        We can create three “waves” for each group of orders based on delivery date. 
        Ten merged orders will be collected by one picker, and then they will be split
        by orders and sent on the same date. 
        
        Orders are picked one after another.
        ''')

import base64
file_ = open("assets/Gif-Picking-based-on-dates.gif", "rb")
contents = file_.read()
data_url = base64.b64encode(contents).decode("utf-8")
file_.close()

st.markdown(
    f'<img src="data:image/gif;base64,{data_url}" alt="cat gif">',
    unsafe_allow_html=True,
)


#---------------------------------------------------------------------------
continue_button(8)


############################################################################
############################################################################
###############          BATCH PICKING - INTRODUCTION          #############


st.header('')
st.image('assets/batch.jpg' ,  width=700)
st.write('''
        ## Batch picking 

        Groups of sales orders picked at the same time is called batch picking. 
        This method is usually applied to minimize repeat visits to the same
        stocked items in the same locations.
        
        Imagine you have 20 orders from your website
        * each order has 3 - 6 different SKUs
        * some of the items appear in most of the orders
        
        By picking order-by-order we will need to pass through the same location multiple times.
        Instead, we can combine all the 20 orders and treat it as one order. Batch picking allows 
        you to go through locations once and collect all needed items for all 20 sales orders.
                
        ''')


import base64
file_ = open("assets/Gif-batch-picking.gif", "rb")
contents = file_.read()
data_url = base64.b64encode(contents).decode("utf-8")
file_.close()

st.markdown(
    f'<img src="data:image/gif;base64,{data_url}" alt="cat gif">',
    unsafe_allow_html=True,
)


#---------------------------------------------------------------------------
continue_button(9)


############################################################################
############################################################################
###############     BUILDING THE MODEL - WALKING DISTANCE      #############

st.write('''
        ## How can we improve efficiency? 

        We can design a model to simulate the impact of several picking processes 
        and routing methods to find **optimal order picking**.  ''')

st.info(''' ** Using batch picking allows to significantly increase the 
        speed of picking goods for your customers.** You don’t need to hire additional
        staff or rent another warehouse to process more orders with the same tools.        ''')
    
    
st.write('''  During the next steps we will build step-by-step all the components needed for optimisation.    ''')
st.title("")
st.image('assets/walking distance.jpg' ,  width=700, caption="Long walks are best enjoyed outdoors. Let's then keep the distance of warehouse picking as short as possible")


#---------------------------------------------------------------------------
continue_button(10)


############################################################################
############################################################################
###############       VISUALISATION - WALKING DISTANCE         #############


############################################################################
#---------------     distance calculation between 2 nodes   ----------------   
# Function

def distance_picking(Loc1, Loc2, y_low, y_high):

    # Start Point
    x1, y1, h1 = Loc1[0], Loc1[1], Loc1[2]
    # End Point
    x2, y2, h2 = Loc2[0], Loc2[1], Loc2[2]
    # Distance x-axis
    distance_x = abs(x2 - x1)
    # Distance y-axis
    if x1 == x2:
        distance_y1 = abs(y2 - y1)
        distance_y2 = distance_y1
    else:
        if h1 == h2:   # Picker doesnt need to change the hall, therefore he doenst need to reach y_max or y_min
            distance_y1 = abs(y2 - y1)
            distance_y2 = distance_y1       
        else:
            distance_y1 = (y_high - y1) + (y_high - y2)
            distance_y2 = abs(y1 - y_low) + abs(y2 - y_low)
    # Minimum distance on y-axis 
    distance_y = min(distance_y1, distance_y2)    
    # Total distance
    distance = distance_x + distance_y

    return distance


############################################################################
#---------------     function to plot the warehouse shape   ----------------   
# Function
 
def warehouse_shape(scatter_plot):
    #scatter_plot.add_hline(y=0.9)
    #scatter_plot.add_vrect(x0=2.1, x1=3.9)
    scatter_plot.add_shape(type="rect",
        x0=-1, y0=4.5, x1=-0.15, y1=34.5,
        line=dict(color="black"),
    )
    
    scatter_plot.add_shape(type="rect",
        x0=2.15, y0=4.5, x1=3.85, y1=34.5,
        line=dict(color="black"),
    )
    
    scatter_plot.add_shape(type="rect",
        x0=6.15, y0=4.5, x1=7.85, y1=34.5,
        line=dict(color="black"),
    )
    
    scatter_plot.add_shape(type="rect",
        x0=10.15, y0=4.5, x1=11.85, y1=34.5,
        line=dict(color="black"),
    )
    
    scatter_plot.add_shape(type="rect",
        x0=14.15, y0=4.5, x1=15.85, y1=34.5,
        line=dict(color="black"),
    )
    
    scatter_plot.add_shape(type="rect",
        x0=18.15, y0=4.5, x1=19.85, y1=34.5,
        line=dict(color="black"),
    )
    
    scatter_plot.add_shape(type="rect",
        x0=22.15, y0=4.5, x1=23.85, y1=34.5,
        line=dict(color="black"),
    )
    
    scatter_plot.add_shape(type="rect",
        x0=26.15, y0=4.5, x1=27.85, y1=34.5,
        line=dict(color="black"),
    )
    
    scatter_plot.add_shape(type="rect",
        x0=30.15, y0=4.5, x1=31.85, y1=34.5,
        line=dict(color="black"),
    )
    
    scatter_plot.add_shape(type="rect",
        x0=34.15, y0=4.5, x1=35.00, y1=34.5,
        line=dict(color="black"),
    )

    return scatter_plot


############################################################################
#---------------     function to plot path to closest point ----------------   
# Function
 
def path_to_closest(scatter_plot, Loc1, Loc2):  

    if Loc1[0] == Loc2[0]:  # if product is on the same Aisle: x is the same 
        scatter_plot.add_shape(type="line",
        x0=Loc1[0], y0=Loc1[1], x1=Loc2[0], y1=Loc2[1],
        line=dict(color="DarkOrange",width=3)  # , dash="dot"
        )
    
    else: 
        if Loc1[2] == Loc2[2]:   # product is in the same hall, therefore he doenst need to reach y_max or y_min
            scatter_plot.add_shape(type="line",
                        x0=Loc1[0], y0=Loc1[1], x1=Loc2[0], y1=Loc1[1], 
                        line=dict(color="DarkOrange",width=3))
                        
            scatter_plot.add_shape(type="line",
                        x0=Loc2[0], y0=Loc1[1], x1=Loc2[0], y1=Loc2[1], 
                        line=dict(color="DarkOrange",width=3)  )    
    
    
        else: 
            distance_y1 = (y_high - Loc1[1]) + (y_high - Loc2[1])
            distance_y2 = abs(Loc1[1] - y_low) + abs(Loc2[1] - y_low)
            
            if distance_y1 < distance_y2:  # shorter path is going through end of the shelves
                scatter_plot.add_shape(type="line",
                        x0=Loc1[0], y0=Loc1[1], x1=Loc1[0], y1=y_high, # x1 & up
                        line=dict(color="DarkOrange",width=3))
                
                scatter_plot.add_shape(type="line",
                        x0=Loc2[0], y0=Loc2[1], x1=Loc2[0], y1=y_high, # x2 & up
                        line=dict(color="DarkOrange",width=3))
                
                scatter_plot.add_shape(type="line",
                        x0=Loc1[0], y0=y_high, x1=Loc2[0], y1=y_high, # line between the points 
                        line=dict(color="DarkOrange",width=3))                    
            
            else: # if its closer to pass through beginning of shelves 
                scatter_plot.add_shape(type="line",
                        x0=Loc1[0], y0=Loc1[1], x1=Loc1[0], y1=y_low, # x1 & down
                        line=dict(color="DarkOrange",width=3))
                
                scatter_plot.add_shape(type="line",
                        x0=Loc2[0], y0=Loc2[1], x1=Loc2[0], y1=y_low, # x2 & down
                        line=dict(color="DarkOrange",width=3))
                
                scatter_plot.add_shape(type="line",
                        x0=Loc1[0], y0=y_low, x1=Loc2[0], y1=y_low, # line between the points
                        line=dict(color="DarkOrange",width=3))   
    return scatter_plot




############################################################################
#---------------     Plotting in streamlit  - path between 2 nodes   -------   
# Streamlit

st.write('''
        ## 1. Walking Distance between 2 locations
               
        Let's start from calculating walking distance between 2 picking locations
        in our warehouse.
          
        Select 2 Location IDs and we will create the shortest path and calculate the 
        distance between them:
        ''')


nodeID1 = st.selectbox(
    'Select 1st Location ID: ',
    nodes['nodeID'].unique(),
    index=15)  # set a default value before choosing

nodeID2 = st.selectbox(
    'Select 2nd Location ID: ',
    nodes['nodeID'].unique(),
    index=123)


Loc1 = [nodes.loc[nodes["nodeID"] == nodeID1,"x"].values[0],
        nodes.loc[nodes["nodeID"] == nodeID1,"y"].values[0],
        nodes.loc[nodes["nodeID"] == nodeID1,"CorrID"].values[0]]

Loc2 = [nodes.loc[nodes["nodeID"] == nodeID2,"x"].values[0],
        nodes.loc[nodes["nodeID"] == nodeID2,"y"].values[0],
        nodes.loc[nodes["nodeID"] == nodeID2,"CorrID"].values[0]]


## Testing DISTANCE 
#nodeID1 = 999 
#nodeID2 = 110 
#Loc1 = [8,20,3]
#Loc2 = [24,9,7]

aa = distance_picking(Loc1, Loc2, y_low , y_high)
"The distance between 2 selected points is:" , aa , "meters"



############################################################################
#---------------     Plotting in streamlit  - path between 2 nodes   -------   
# Streamlit

abb = px.scatter(nodes, x= "x", y="y", hover_name = "nodeID")
abb.update_layout(annotations=[{"x":Loc1[0], "y":Loc1[1], "text": "<b>Location 1</b>", "font":{"color":"red", "size":15}, "arrowcolor":"red"},
                               {"x":Loc2[0], "y":Loc2[1], "text": "<b>Location 2</b>", "font":{"color":"red", "size":15}, "arrowcolor":"red"}] )
abb = warehouse_shape(abb) 
abb = path_to_closest(abb, Loc1, Loc2) 
st.plotly_chart(abb)


#---------------------------------------------------------------------------
#continue_button(11)
continue_button(12)


############################################################################
############################################################################
###############            ROUTE   OPTIMISATION                #############

col1, mid, col2 = st.beta_columns([18,1,25])
with col1:
    st.write(''' 
        ## 2. Route optimisation
        
        Imagine that order you are assembling has **10 products**. All of them are 
        **scattered across the warehouse**. One approach could be to pick the items 
        in random order...   
        
        ### ...but,  
        ####
        much better approach would be to **go to the next closest item**.  
        
        Using above distance calculation between two locations, we can sort the 
        list of products in a way that would decrease the walking distance for all the order.''')
with col2:
    st.image('assets/jobsintown.de_add1.jpg', width=320, caption = "You don't need to do it manually! Let the machine work its magic")

st.write(''' 
        ##
        Deciding on the right route is a well-known algorithmic problem in the fields
        of computer science and operations research and is called  **Travelling Salesman Problem**. 
        Let's check it out what it means 
        ''')







#--------------------------------------------------------------------------- 
continue_button(13)



############################################################################
############################################################################
###############   TRAVELLING SALESMAN  - INTRODUCTION          #############


st.image('assets/travelling_salesman.jpg', width = 700)
 
st.write('''
        ## Travelling Salesman Problem (TSP)
        
        The Travelling Salesman Problem (TSP) is the challenge of finding 
        the shortest yet most efficient route for a person to take given 
        a list of specific destinations. 
   
        It has no “quick” solution and the complexity of calculating the 
        best route will increase when you add more destinations to the problem.       ''') 

  
################## Set of points
col1, mid, col2 = st.beta_columns([3,1,15])
with col1:
    st.image('assets/travelling_1dots.jpeg', width=150)
with col2:
    st.write(''' 
             ### The task 
             Given a set of points and distance between every pair of points,
             the problem is to find the shortest possible route that goes through 
             every point exactly once and returns to the starting point.''')        
        
################## Product list
col1, mid, col2 = st.beta_columns([3,1,15])
with col1:
    st.image('assets/travelling_2solution.jpeg', width=150)
with col2:
    st.write(''' 
             ### Searching for optimal path  
             There are obviously a lot of different routes to choose from:
             * With 10 destinations, there can be more than 300,000 roundtrip 
             permutations and combinations. 
             * With 15 destinations, the number of possible routes could exceed 87 billion.
             ''')        
        
################## Travelling salesman examples
col1, mid, col2 = st.beta_columns([30,1,20])
with col1:
    st.write(''' 
    ### Examples of such problems include: 
    * delivering products from Business to Client
    * schedulling multiple jobs on a single machine 
    * assigning crew to flights
    * order-picking problem in warehouses

             ''') 
with col2:
    st.image('assets/Amazon.jpg', width=250)
     
#---------------------------------------------------------------------------
continue_button(14)          



st.header('')
col1, mid, col2 = st.beta_columns([20,40,20])
with col1:
    st.image('assets/question.jpg', width=150)
with mid:
    st.write('''
             #### 
             
             ## What is **World’s toughest transportation challenge?**  ''')                 
with col2:
    st.image('assets/question.jpg', width=150)
    
    
st.header('')    
continue_button_xmas(19)
st.write('''
        ## World’s toughest logistics challenge         
        
        >* 1 night 
        >* 120m presents
        >* 180,000 tonnes of toys (and packaging)
        >* Rudolph and team will need 3,660 tonnes of carrots to fuel them
        >* Travel the 230,000 kilometers (144,000 miles)
        
''') 

st.image('assets/travelling_Santa2.png', width = 700, caption="World’s toughest logistics challenge - delivering all gifts in one night")
 
#### X-mas edition: 
# https://www.themanufacturer.com/articles/crunching-numbers-worlds-toughest-logistics-challenge/ 
  


############################################################################
############################################################################
###############   TRAVELLING SALESMAN  - 1. CLOSEST LOCATION   #############


############################################################################
#---------------     TSP - Find closest next location       ----------------   
# Function

def next_location(start_loc, list_locs, y_low, y_high):

    # Distance to every next points candidate
    list_dist = [distance_picking(start_loc, i, y_low, y_high) for i in list_locs]
    # Minimum Distance 
    distance_next = min(list_dist)
    # Location of minimum distance
    index_min = list_dist.index(min(list_dist))
    next_loc = list_locs[index_min] # Next location is the first location with distance = min (**)
    list_locs.remove(next_loc)      # Next location is removed from the list of candidates
    
    return list_locs, start_loc, next_loc, distance_next
	

## Testing next location 
#
#bbb = dataset.loc[1:50,]
#list_locs = list(bbb['Coord_hall'].apply(lambda t: literal_eval(t)).values)
#list_locs
#next_location(start_loc, list_locs, y_low, y_high)



############################################################################
#---------------     TSP - list all the locations in a wave     ------------   
# Function

def locations_listing(df_orderlines, wave_id):

	# Filter by wave_id
	df = df_orderlines[df_orderlines.WaveID == wave_id]
	# Create coordinates listing
	list_locs = list(df['Coord_hall'].apply(lambda t: literal_eval(t)).values)
	#list_locs.sort() ## LAURA - just checking for baselie
	# Get unique Unique coordinates
	list_locs = list(k for k,_ in itertools.groupby(list_locs))
	n_locs = len(list_locs)

	return list_locs, n_locs
	

## Testing Location listing
#bbb = dataset.loc[1:50,]
#list_locs = list(bbb['Coord_hall'].apply(lambda t: literal_eval(t)).values)
#list_locs
#locations_listing(bbb, 3)


############################################################################
#---------------     TSP - create a picking route        -------------------   
# Function


def create_picking_route(origin_loc, list_locs, y_low, y_high):

    # Total distance variable
    wave_distance = 0
    # Current location variable 
    start_loc = origin_loc
    # Store routes
    list_chemin = []
    list_chemin.append(start_loc)
    
    while len(list_locs) > 0: # Looping until all locations are picked
        # Going to next location
        list_locs, start_loc, next_loc, distance_next = next_location(start_loc, list_locs, y_low, y_high)
        # Update start_loc 
        start_loc = next_loc
        list_chemin.append(start_loc)
        # Update distance
        wave_distance = wave_distance + distance_next 

    # Final distance from last storage location to origin
    wave_distance = wave_distance + distance_picking(start_loc, origin_loc, y_low, y_high)
    list_chemin.append(origin_loc)
    
    return wave_distance, list_chemin


## Testing create_picking_route
#origin_loc = start_loc
#create_picking_route(origin_loc, list_locs, y_low, y_high)



############################################################################
#---------------     TSP - Mapping orders by wave number      --------------   
# Function

#    * Orderlines mapping assigns new order ID (after sorting by date) 
#    * assigns as many orders as fits in the picking cart (defined by orders_number)

def orderlines_mapping(df_orderlines, orders_number):

	# Order dataframe by timeframe
	df_orderlines = df_orderlines.sort_values(by=[ 'date', "orders_id"], ascending = True)
	# Unique order numbers list
	list_orders = df_orderlines.orders_id.unique()
	# Dictionnary for mapping
	dict_map = dict(zip(list_orders, [i for i in range(1, len(list_orders)+1)]))
	# Order ID mapping
	df_orderlines['OrderID'] = df_orderlines['orders_id'].map(dict_map)
	# Grouping Orders by Wave of orders_number 
	# df_orderlines['WaveID'] = (df_orderlines.OrderID%orders_number == 0).shift(1).fillna(0).cumsum()
	rrr = pd.DataFrame({"OrderID": df_orderlines.OrderID.unique()})
	rrr['WaveID'] = (rrr.OrderID%orders_number == 0).shift(1).fillna(0).cumsum()
	df_orderlines = pd.merge(df_orderlines,rrr, on = "OrderID" )

    # Counting number of Waves
	waves_number = df_orderlines.WaveID.max() + 1

	return df_orderlines, waves_number


#---------------------------------------------------------------------------  
continue_button(16)



############################################################################
############################################################################
###############   TRAVELLING SALESMAN  - 2. BATCHING           #############


st.write('''
        ## 3. Batching
        
        Imagine that you have 3 orders. 
        
        Each order could be assembled separately. It would mean that we start in Depot,
        gather all the products that belong to the first order and come back to Depot.              ''')

st.image('assets/one-by-one piskup.png', width = 800, caption="Picking routes for three orders - 1 order per Wave")

st.write('''
        A first intuitive way to optimize this process is to **combine these 
        three orders in one batch** — this strategy is commonly called 
        Batch Picking.          
        ''')        

st.image('assets/1_picking_route.PNG', width = 600, caption="Combining 3 orders into one Batch")


st.write(''' ### In order to combine multiple orders: 
* First, we need to decide the **priority order**. 
In our model we will sort orders based 
        on the date. This way we will execute them based on first-come-first-go rule.         
        
* Then, we decide the **size of the batch** - how many orders should be included in
        each trip - and then assign batch numbers based on set priority.         ''')
        

        
#---------------------------------------------------------------------------
continue_button(17)


############################################################################
############################################################################
###############   TRAVELLING SALESMAN  - 4. OPTIMISING THE ROUTE   #########



############################################################################
#---------------     TSP - run waving simulation      --------------   
# Function

#    * this function calls function that vreates waves based on the walking distance similarity 
#    * loops through each wave 
#    * calls function that creates picking route withing the wave
#    * calculates total distance needed to complete all orders 

list_wid, list_dst, list_route, list_ord, list_ord_act = [], [], [], [], []

# Function 
def simulation_wave(y_low, y_high, orders_number, df_orderlines, list_wid, list_dst, list_route, list_ord, list_ord_act):

	# Create variable to store total distance
	distance_route = 0 
	# Create waves
	df_orderlines, waves_number = orderlines_mapping(df_orderlines, orders_number)
	# Loop all waves
	for wave_id in range(waves_number):
		# Listing of all locations for this wave 
		list_locs, n_locs = locations_listing(df_orderlines, wave_id)
		# Results
		wave_distance, list_chemin = create_picking_route(Loc_orn, list_locs, y_low, y_high)
		distance_route = distance_route + wave_distance
		actual_orders_in_batch = df_orderlines.groupby(["WaveID"])["orders_id"].nunique()
		# Append lists of results 
		list_wid.append(wave_id)
		list_dst.append(wave_distance)
		list_route.append(list_chemin)
		list_ord.append(orders_number)
		list_ord_act.append(actual_orders_in_batch[wave_id])
        

	return list_wid, list_dst, list_route, list_ord, distance_route, list_ord_act, df_orderlines





# TEST 
#list_wid, list_dst, list_route, list_ord = [], [], [], []
#ggg = simulation_wave(y_low, y_high, orders_number, dataset, list_wid, list_dst, list_route, list_ord)

############################################################################
#---------------     TSP - run waving simulation on ready WAVES     --------   
# Function

#    * waves are already created in the dataset 
#    * loops through each wave 
#    * calls function that creates picking route withing the wave
#    * calculates total distance needed to complete all orders 

list_wid, list_dst, list_route, list_ord, list_ord_act = [], [], [], [], []

def simulation_wave_ready_waves(y_low, y_high, orders_number, df_orderlines, list_wid, list_dst, list_route, list_ord, number_of_waves, list_ord_act):
	# Create variable to store total distance
	distance_route = 0 
	# Create waves
	# NOT NEEDED< WAVES CREATED # df_orderlines, number_of_waves = orderlines_mapping(df_orderlines, orders_number)
	# Loop all waves
	for wave_id in range(number_of_waves):
		# Listing of all locations for this wave 
		list_locs, n_locs = locations_listing(df_orderlines, wave_id)
		# Results
		wave_distance, list_chemin = create_picking_route(Loc_orn, list_locs, y_low, y_high)
		distance_route = distance_route + wave_distance
		actual_orders_in_batch = df_orderlines.groupby(["WaveID"])["orders_id"].nunique()
		# Append lists of results 
		list_wid.append(wave_id)
		list_dst.append(wave_distance)
		list_route.append(list_chemin)
		list_ord.append(orders_number)
		list_ord_act.append(actual_orders_in_batch[wave_id])

	return list_wid, list_dst, list_route, list_ord, distance_route, list_ord_act




############################################################################
#---------------     TSP - run simulation diff #orders        --------------   
# Function

# Test several values of orders per wave
# Create lists to store results
list_wid, list_dst, list_route, list_ord, list_ord_act = [], [], [], [], []

for orders_number in range(1, 10):
	list_wid, list_dst, list_route, list_ord, distance_route, list_ord_actual, df_TSP_diff_orderNum = simulation_wave(y_low, y_high, orders_number, dataset, list_wid, list_dst, list_route, list_ord, list_ord_act)
	#print("Total distance covered for {} orders/wave: {:,} m".format(orders_number, distance_route))

# Create df for results
df_results = pd.DataFrame({'Wave_Number': list_wid,
			   'Distance_Route': list_dst,
			   'Chemins': list_route,
			   'OrderPerWave': list_ord,
               'OrderPerWave_act':list_ord_actual},)

#print(df_results.head())
	

############################################################################
#---------------  Visualisation in streamlit - diff #orders    -------------   
# Streamlit 

#     * display the dataframe with wave #xx 
#     * let the user choose number of waves 


st.write('''
        ## 4. Optimising the route for each Batch of orders           
        
        Once the orders are combined in a batch, we can treat it as one order. 
        This will help us to find shortest distances between all the items, 
        and therefore avoid returning to same location during the order collection.
        ''')
  

orders_of_waves_selected = st.selectbox(
    'Select how many order per batch we should have: ',
    [1,2,3,4,5,6,7,8,9,10],
    index=2)  # set a default value before choosing

wave_number_selected = st.selectbox(
    'Select which batch number you would like to view: ',
    df_results[df_results["OrderPerWave"] == orders_of_waves_selected ]["Wave_Number"].unique(),
    index=1)  # set a default value before choosing

#orders_of_waves_selected  = 5
#wave_number_selected = 1

hhh = orderlines_mapping(dataset, orders_of_waves_selected)
dataset_for_visualisation = hhh[0]

st.header('')
st.write(''' All of the visible products will be merged under one batch. 
         In the next step, all the products will be sorted based on the next closest location. 
         Following this approach will help us to minimize the distance needed to gather assigned orders. ''')


dataset_for_visualisation[dataset_for_visualisation["WaveID"]==wave_number_selected]


#---------------------------------------------------------------------------
continue_button(18)

############################################################################
############################################################################
###############            BATCHING   -   SUMMARY                  #########


st.write(''' ## Evaluating number of orders per route
To estimate the impact of batching in your productivity,
we’ll run several simulations with gradual number of orders per batch and 
measure total walking distance: how much your total walking distance 
is reduced if you increase the number of orders per route 

        ''')
 

# average SKUs per order          
df_results_agg = pd.DataFrame(df_results.groupby("OrderPerWave")["Distance_Route"].sum())
df_results_agg["OrderPerWave"] = df_results_agg.index
st.write(px.bar(df_results_agg, x='OrderPerWave', y='Distance_Route'), labels={'OrderPerWave':'Number of orders per wave', 'Distance_Route':'Routing distance (m)'}, tickmode='linear')  # , labels={'count':'Routing Distance'}
st.write("""What actions could we take to increase efficiency?  """)

#---------------------------------------------------------------------------
continue_button(20)

st.write(""" # Possible solution 
Replace regular picking carts with giant picking carts!  

""")
st.image('assets/giant_shopper_cart.jpg' ,  width=700)

st.write(""" 
#### Just kidding, there are much better (and realistic) solutions!

### During the next chapter we will search for more optimal ways 
on how to handle the orders. Sorting them by the date is a good start, but might not 
bring the most optimal solution. 

### 
""")

#---------------------------------------------------------------------------
continue_button(21)

############################################################################
############################################################################
###############      WAVING OPTIMISATION  -  INTRODUCTION          #########


st.image('assets/growth1.jpg', width = 700)

st.write("""# Waving Optimisation
#### """)

st.info('''**Optimizing the waving algorithm could significantly increase 
the efficiency** of a warehouse. 

      
There might be many factors to consider when we prioritize the orders. To name a few:       
* Delivery date
* Picking zones in the warehouse
* Type of orders
* Customer location
* Frequency of orders
        
        ''')
   

#---------------------------------------------------------------------------
continue_button(22)


############################################################################
############################################################################
###############      WAVING OPTIMISATION  -  INTRODUCTION          #########

#st.write(''' # Waving Optimisation
#Up until now we saw one approach on how to make our warehouse more 
#efficient: 
#* deciding how many orders one wave should have
#* **sorting orders based on the order date**
#* splitting orders into waves 
#* within each wave sorting the products in a way to minimize tptal walking distance.   ''')

#---------------------------------------------------------------------------
#continue_button(23)


############################################################################
############################################################################
###############      WAVING OPTIMISATION  -  CLUSTERING            #########



st.header('')
col1, mid, col2 = st.beta_columns([35,2,20])
with col1:
    st.write(""" ## Clustering Picking Locations
Grouping several orders by location cluster can ensure that our picker will stay in a delimited zone.

Group picking locations by clusters to reduce walking 
distance for each picking route. Here, similarity metric
 will be **walking distance** from one location to another.
 
_For instance, I would like to group locations ensuring that
maximum walking distance between two locations is 10 m._""")
   
with col2:
    st.image('assets/clustering.png', width=220)
   


    
st.write(""" 

### Let's start from Orders with one SKU
Steps for creating clusters for Single Line Orders 
* extract orders with single SKU 
* set distance threshold - how far grouped locations could be located
* search for similar locations - similatiry metric used is walking distance
* assign cluster ID to all orders 

         """)
       
#---------------------------------------------------------------------------         
continue_button(24)        
        


one_line_orders = pd.DataFrame(dataset.groupby(['orders_id'])['itemID'].count()).reset_index()
one_line_orders= one_line_orders.loc[one_line_orders["itemID"] == 1].reset_index(drop=True)
df_single_line = dataset[dataset["orders_id"].isin(one_line_orders["orders_id"])].reset_index(drop=True)
multi_line_orders = dataset[~dataset["orders_id"].isin(one_line_orders["orders_id"])].reset_index(drop=True)

aaaa = df_single_line.copy()



############################################################################
#---------------     CLustering  - 1. Custom made distance       -----------   
# Function


def distance_func(Loc1, Loc2):
    y_low=4 
    y_high=35
    
    # Start Point
    x1, y1, h1 = Loc1[0], Loc1[1], Loc1[2]
    # End Point
    x2, y2, h2 = Loc2[0], Loc2[1], Loc2[2]
    # Distance x-axis
    distance_x = abs(x2 - x1)
    # Distance y-axis
    if x1 == x2:
        distance_y1 = abs(y2 - y1)
        distance_y2 = distance_y1
    else:
        if h1 == h2:   # Picker doesnt need to change the hall, therefore he doenst need to reach y_max or y_min
            distance_y1 = abs(y2 - y1)
            distance_y2 = distance_y1       
        else:
            distance_y1 = (y_high - y1) + (y_high - y2)
            distance_y2 = abs(y1 - y_low) + abs(y2 - y_low)
    # Minimum distance on y-axis 
    distance_y = min(distance_y1, distance_y2)    
    # Total distance
    distance = distance_x + distance_y

    return distance


############################################################################
#---------------     CLustering  - 2. Clustering + Mapping       -----------   
# Function

def clustering_loc(df, distance_threshold, dist_method, orders_number, 
	wave_start, clust_start, df_type):

	# 1. Create Clusters
	list_coord, list_OrderNumber, clust_id, df = cluster_wave(df, distance_threshold, dist_method, clust_start, df_type)
	clust_idmax = max(clust_id) # Last Cluster ID

	# 2. Mapping Order lines with clusters
	dict_map, dict_omap, df, Wave_max = lines_mapping_clst(df, list_coord, list_OrderNumber, clust_id, orders_number, wave_start)

	return dict_map, dict_omap, df, Wave_max, clust_idmax




############################################################################
#---------------     CLustering  - 2. Create Waves using Clusters    -------   
# Function

def cluster_wave(df, distance_threshold, dist_method, clust_start, df_type):

	# Create Column for Clustering
	if df_type == 'df_mono':
		df['Coord_Cluster'] = df['Coord_hall'] 

	# Mapping points
	df_map = pd.DataFrame(df.groupby(['orders_id', 'Coord_Cluster'])['itemID'].count()).reset_index() 	# Here we use Coord Cluster
	list_coord, list_OrderNumber = np.stack(df_map.Coord_Cluster.apply(lambda t: literal_eval(t)).values), df_map.orders_id.values

	# Cluster picking locations
	clust_id = cluster_locations(list_coord, distance_threshold, dist_method, clust_start)
	clust_id = [(i + clust_start) for i in clust_id]

	# List_coord
	list_coord = np.stack(list_coord)

	return list_coord, list_OrderNumber, clust_id, df
 

############################################################################
#---------------     CLustering  - 3. Create clusters of (x, y)      -------   
# Function

def cluster_locations(list_coord, distance_threshold, dist_method, clust_start):

	# Create linkage matrix
	if dist_method == 'euclidian':
		Z = ward(pdist(np.stack(list_coord)))
	else:
		Z = ward(pdist(np.stack(list_coord), metric = distance_func))
	# Single cluster array
	fclust1 = fcluster(Z, t = distance_threshold, criterion = 'distance')

	return fclust1


############################################################################
#---------------     CLustering  - 4. Mapping Orders with clusters   -------   
# Function

def lines_mapping_clst(df, list_coord, list_OrderNumber, clust_id, orders_number, wave_start):

	# Dictionnary for mapping by cluster
    dict_map = dict(zip(list_OrderNumber, clust_id))
	# Dataframe mapping
    df['ClusterID'] = df['orders_id'].map(dict_map)
	# Order by ID and mapping
    df = df.sort_values(['ClusterID','date'], ascending = True)   #df = df.sort_values(['ClusterID','orders_id'], ascending = True)
    list_orders = list(df.orders_id.unique())
	# Dictionnary for order mapping 
    dict_omap = dict(zip(list_orders, [i for i in range(1, len(list_orders)+1)]))
	# Order ID mapping
    df['OrderID'] = df['orders_id'].map(dict_omap)

	# Create Waves: Increment when reaching orders_number or changing cluster
    #rrr = pd.DataFrame({"OrderID": df.OrderID.unique()})
    rrr = df[["OrderID", "ClusterID"]].drop_duplicates()
    #rrr = pd.merge(rrr,df[["OrderID", "ClusterID"]], on = "OrderID" )
    #rrr['WaveID'] = (rrr.OrderID%orders_number == 0).shift(1).fillna(0).cumsum()
    rrr['WaveID'] = wave_start + ((rrr.OrderID%orders_number == 0) | (rrr.ClusterID.diff(periods=-1) != 0)).shift(1).fillna(0).cumsum() 	
    df= pd.merge(df,rrr[["OrderID", "WaveID"]], on = "OrderID" )
    #df['WaveID'] = wave_start + ((df.OrderID%orders_number == 0) | (df.ClusterID.diff(periods=-1) != 0)).shift(1).fillna(0).cumsum() 
    Wave_max = df.WaveID.max()

    return dict_map, dict_omap, df, Wave_max



#---------------     Running CLustering  -------   
# =============================================================================
# dict_map_single, dict_omap_single, df_single, Wave_max, clust_idmax = clustering_loc(df_single_line, distance_threshold, 'custom', orders_number, 
# 	wave_start, clust_start, 'df_mono')
# 
# =============================================================================



#####################################################################
######################################   START TESTING pieces of code for Clsutering single lines 
#####################################################################

###############################################

## CLEAN below

# =============================================================================
# ############################################### FUNCTION cluster_wave
# # Create Column for Clustering
# df_single_line['Coord_Cluster'] = df_single_line['Coord_hall'] 
# 
# # Mapping points
# df_map = pd.DataFrame(df_single_line.groupby(['orders_id', 'Coord_Cluster'])['itemID'].count()).reset_index() 	# Here we use Coord Cluster
# list_coord, list_OrderNumber = np.stack(df_map.Coord_Cluster.apply(lambda t: literal_eval(t)).values), df_map.orders_id.values
# 
# 
# ############################################### FUNCTION cluster_locations
# # cluster_locations
# Z = ward(pdist(np.stack(list_coord), metric = distance_func))
# 	# Single cluster array
# fclust1 = fcluster(Z, t = distance_threshold, criterion = 'distance')
# clust_id =fclust1
# clust_id = [(i + clust_start) for i in clust_id]
# list_coord = np.stack(list_coord)
# 
# ############################################### FUNCTION lines_mapping_clst
# # Dictionnary for mapping by cluster
# dict_map = dict(zip(list_OrderNumber, clust_id))
# # Dataframe mapping
# df_single_line['ClusterID'] = df_single_line['orders_id'].map(dict_map)
# # Order by ID and mapping
# df_single_line = df_single_line.sort_values(['ClusterID','date'], ascending = True)
# list_orders = list(df_single_line.orders_id.unique())
# # Dictionnary for order mapping 
# dict_omap = dict(zip(list_orders, [i for i in range(1, len(list_orders)+1)]))
# # Order ID mapping
# df_single_line['OrderID'] = df_single_line['orders_id'].map(dict_omap)
# 
# # Create Waves: Increment when reaching orders_number or changing cluster
# df_single_line['WaveID'] = wave_start + ((df_single_line.OrderID%orders_number == 0) | (df_single_line.ClusterID.diff(periods=-1) != 0)).shift(1).fillna(0).cumsum() 
# Wave_max = df_single_line.WaveID.max()
# 
# 
# ########################################################################
# ######################## ---------   Visualisation of clusters 
# # Streamlit
# 
# distance_threshold_vis = st.slider('Distance in meters', 10, 70, 40)  # min: 0h, max: 23h, default: 17h
# 
# fclust1_visualisation = fcluster(Z, t = distance_threshold_vis, criterion = 'distance')
# 
# aaaa["clusterIDvis"] = fclust1_visualisation
# aaaa = aaaa.sort_values(by=['clusterIDvis'])
# aaaa["clusterIDvis"] = aaaa["clusterIDvis"].astype('category')
# 
# 
# abc = px.scatter(aaaa, x= "x", y="y", hover_name = "nodeID", color="clusterIDvis")
# abc = warehouse_shape(abc)
# abc.update_layout(width=650)
# st.plotly_chart(abc)
# 
# 
# =============================================================================
distance_threshold_vis = st.slider('Distance in meters', 10, 70, 40)  # min: 0h, max: 23h, default: 17h

clustered_nodes = clustering_loc(df_single_line, distance_threshold_vis, 'custom', orders_number, wave_start, clust_start, 'df_mono')
clustered_nodes_df = clustered_nodes[2]
clustered_nodes_df["ClusterID"]= clustered_nodes_df["ClusterID"].astype('category')

abcd = px.scatter(clustered_nodes[2], x= "x", y="y", hover_name = "nodeID", color="ClusterID")
abcd = warehouse_shape(abcd)
abcd.update_layout(width=650)
st.plotly_chart(abcd)






#####################################################################
#####################################################################   END TESTING pieces of code
#####################################################################


#---------------------------------------------------------------------------
continue_button(25)        
 

st.write(""" 

We just saw how easy it is to cluster the orders with one product only.          
Unlike single-line orders, multi-line orders can cover several picking locations.
However, we can apply the same methodology applied to centroids of storage locations.

### Let's proceed with clustering of Orders with multiple SKUs
Steps for creating clusters for Multiple Line Orders 
* extract remaining orders 
* keep the same distance threshold - how far grouped locations could be located
* compute centroids for all orders 
* search for similar locations - similatiry metric used is walking distance
* assign cluster ID to all orders 

         """)
         
st.image('assets/centroid.png', width=620, caption="How a centroid is calculated for order with multiple different SKUs")



############################################################################
#---------     Clustering  - 5. Centroid calculation and mapping    --------   
# Function

 
def centroid(list_in):
    x, y, z = [p[0] for p in list_in], [p[1] for p in list_in], [p[2] for p in list_in]
    centroid = [round(sum(x) / len(list_in),2), round(sum(y) / len(list_in), 2), np.median(z) ] # np.random.randint(1, 100, 1)[0] ##3rd part is added to randomly generate "HALL ID"
    return centroid



# Mapping Centroids
def centroid_mapping(df_multi):

    # Mapping multi
    df_multi['Coord_hall'] = df_multi['Coord_hall'].apply(literal_eval)
    # Group coordinates per order
    df_group = pd.DataFrame(df_multi.groupby(['orders_id'])['Coord_hall'].apply(list)).reset_index()
    # Calculate Centroid
    df_group['Coord_Centroid'] = df_group['Coord_hall'].apply(centroid)
    # Dictionnary for mapping
    list_order, list_coord = list(df_group.orders_id.values), list(df_group.Coord_Centroid.values)
    dict_coord = dict(zip(list_order, list_coord))

    # Final mapping
    df_multi['Coord_Cluster'] = df_multi['orders_id'].map(dict_coord).astype(str)
    df_multi['Coord_hall'] = df_multi['Coord_hall'].astype(str)

    return df_multi
  





# =============================================================================
# ############################################################################
# #---------     Clustering  - 5. Centroid calculation and mapping    --------   
# # TESTING 
# 
# df_multi = multi_line_orders.copy()
# 
# # Mapping multi
# df_multi['Coord_hall'] = df_multi['Coord_hall'].apply(literal_eval)
# # Group coordinates per order
# df_group = pd.DataFrame(df_multi.groupby(['orders_id'])['Coord_hall'].apply(list)).reset_index()
# # Calculate Centroid
# df_group['Coord_Centroid'] = df_group['Coord_hall'].apply(centroid)
# # Dictionnary for mapping
# list_order, list_coord = list(df_group.orders_id.values), list(df_group.Coord_Centroid.values)
# dict_coord = dict(zip(list_order, list_coord))
# 
# # Final mapping
# df_multi['Coord_Cluster'] = df_multi['orders_id'].map(dict_coord).astype(str)
# df_multi['Coord_hall'] = df_multi['Coord_hall'].astype(str)
# 
# #######################################################################
# #######################################################################
# 
# df_multi = multi_line_orders.copy()
# 
# wave_start  = Wave_max+1
# clust_start = clust_idmax+1
# 
# df_multi = centroid_mapping(df_multi)
# dict_map_multi, dict_omap_multi, df_multi, Wave_max_m, clust_idmax_m = clustering_loc(df_multi, distance_threshold, 'custom', orders_number, 
# 	wave_start, clust_start, 'df_multi')
# #######################################################################
# # Merging single line with multiline dataset
# 
# df_full  = df_single.append(pd.DataFrame(data = df_multi), ignore_index=True)
# 
# 
# =============================================================================






#---------------------------------------------------------------------------
continue_button(26)        


############################################################################
############################################################################
###############                THROUGHPUT                    ###############
st.title("")
st.image('assets/throughput2.jpg', width=720) # caption=""

st.write(""" # Throughput  
         
is the amount of a product that a company can produce within a specified period of time. 
Examples: 
               
>* 20 copies being printed within a 5 minute period
>* 10 orders picked during 1 hour 
>* 3 cars assembled during 2 days 
         """)

st.write( r"""#         
         
We will define:
$\textcolor{orangered}{throughput}  \mapsto \>   \textcolor{orangered}{\Tau} = \Large \frac{number \> of \> orders}{ \textcolor{blue}{time \>  to \>  travel}}$
#
""")


# $\textcolor{#21b85d}{Velocity}    \mapsto \> \textcolor{#21b85d}\nu = \Large(\frac{\textcolor{orangered}{distance \> to \> travel}}{\textcolor{blue}{time \> to \>travel }})$  , therefore $\implies$  
# $\textcolor{blue}{Time \> to \> travel} \mapsto \textcolor{blue}\tau = > \Large(\frac{\textcolor{orangered}{distance \> to \> travel}}{ \textcolor{#21b85d}{velocity}})$ 

#---------------------------------------------------------------------------      
continue_button(27)        
 

st.write(r""" # Waving Optimisation 
### Objective
$\Uparrow$ Maximize the average $\textcolor{orangered}{throughput}$ of all the waves 
### Constrains:
* 1 picker 
* 3 orders per cart per wave - cart capacity is is limited and will be used to the fullest possible 
* 1 $\frac{m}{s}$ velocity - speed with which an average picker is moving through
the warehouse. With this speed a picker can walk 3.6km in 1 hour.

Example of a single picker in 2 different waves:
        """)




################## Example of 2 waves with one picker
col1, mid, col2 = st.beta_columns([30,60,70])
with col1:
    st.image('assets/throughput1ninja.png', width=400)
with col2:
    st.image('assets/throughput1ninja_num.png', width= 180)        
        
col1, mid, col2 = st.beta_columns([30,60,70])
with col1:
    st.image('assets/throughput2ninja.png', width=340)
with col2:
    st.image('assets/throughput2ninja_num.png', width= 180)        
        
    
#---------------------------------------------------------------------------
continue_button(28) 
st.write( r"""#         

$\Uparrow$ $\textcolor{orangered}{throughput}  \mapsto \>   \textcolor{orangered}{\Tau} = \Large \frac{ \Uparrow number \> of \> orders}{ \textcolor{blue}{ \Downarrow time \>  to \>  travel}}$

#
         
In order to **maximise** the throughput we can:
* $\uparrow$ increase the number of orders per wave $\uparrow$ or 
* $\downarrow$ decrease the time to travel $\downarrow$  

In the constrains we have specified that we can't exceed 3 orders per picking cart. 
That means that that in each wave we can keep the number of orders at maximum and at the
same time also minimize the time to travel. 

# 
""") 

#---------------------------------------------------------------------------
continue_button(29) 

st.write( r"""#    
$\> \textcolor{blue}{ \Downarrow time \> to \> travel} \mapsto \textcolor{blue}\tau = \> \Large \frac{\textcolor{#ffbc05}{ \Downarrow distance \> to \> travel}}{ \Uparrow velocity}$ 
  
#
Based on above formula, in order to **minimize** the time to travel we can:
* $\downarrow$ decrease the distance to travel$\downarrow$  or 
* $\uparrow$ increase the velocity $\uparrow$

# 
""")

#---------------------------------------------------------------------------
continue_button(30)


file_ = open("assets/warehouse drifting.gif", "rb")
contents = file_.read()
data_url = base64.b64encode(contents).decode("utf-8")
file_.close()


col1, mid, col2 = st.beta_columns([30,2,40])
with col1:
    st.write(""" 
Each picker has his own walking spead and it would be quite difficult to 
increase it, without implementing similar "adjustments"  $\implies$ 


                           
####    
For this reason we will treat the velocity as a constant unchanging number. 
####
             """)
with col2:
    st.markdown(
    f'<img src="data:image/gif;base64,{data_url}" alt="cat gif"  width=400>',
    unsafe_allow_html=True,
)
        
    

st.write( r"""
The good news is that we can still focus on **minimizing** the $\textcolor{#ffbc05}{distance \> to \> travel}$! 

Previously in the course we saw various ways on how to minimize this metric. 
It is a great opportunity to see which approach best **maximizes the $\textcolor{orangered}{throughput}$**.

#
""")



#---------------------------------------------------------------------------
#continue_button(31) 
continue_button(32) 

st.image('assets/podium.jpg', width=600)
st.write(""" # Let's compare the results:
1. **Baseline** - we will split all the orders randomly into the batches of 3 orders and pick products based on their order
2. **TSP** / WMS - we will sort the orders based on the delivery date, assign 3 orders to batches and sort products based on the walking distance
3. **Clustering** - clustering order locations and th,[en assigning to waves 
4. **3 closest orders** - we will take 3 closest orders to the depot and assign them to waves          
        
         """)

#---------------------------------------------------------------------------
#continue_button(33) 
#continue_button(34) 
continue_button(35)
 
####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################


############################################################################
#---------------            Dataset for comparison           ---------------    

dataset_for_comparison = dataset.copy()
orders_number_comparison = 3
pickers_speed = 3600    # m per hour



############################################################################
#---------------     next_location_not_based_on_distance       ----------------   
# Function

def next_location_not_based_on_distance(start_loc, list_locs, y_low, y_high):

    # Distance to every next points candidate
    list_dist = [distance_picking(start_loc, i, y_low, y_high) for i in list_locs]
    # Minimum Distance 
    distance_next = list_dist[0] #min(list_dist)
    # Location of minimum distance
    ##index_min = list_dist.index(min(list_dist))
    next_loc = list_locs[0]      #list_locs[index_min] # Next location is the first location with distance = min (**)
    list_locs.remove(next_loc)      # Next location is removed from the list of candidates
    
    return list_locs, start_loc, next_loc, distance_next
	


############################################################################
#---------     create_picking_route_not_based_on_distanc        -----------   
# Function

def create_picking_route_not_based_on_distance(origin_loc, list_locs, y_low, y_high):

    # Total distance variable
    wave_distance = 0
    # Current location variable 
    start_loc = origin_loc
    # Store routes
    list_chemin = []
    list_chemin.append(start_loc)
    
    while len(list_locs) > 0: # Looping until all locations are picked
        # Going to next location
        list_locs, start_loc, next_loc, distance_next = next_location_not_based_on_distance(start_loc, list_locs, y_low, y_high)
        # Update start_loc 
        start_loc = next_loc
        list_chemin.append(start_loc)
        # Update distance
        wave_distance = wave_distance + distance_next 

    # Final distance from last storage location to origin
    wave_distance = wave_distance + distance_picking(start_loc, origin_loc, y_low, y_high)
    list_chemin.append(origin_loc)
    
    return wave_distance, list_chemin


############################################################################
#---------     simulation_wave_ready_waves_not_based_on_distance        -----------   
# Function


def simulation_wave_ready_waves_not_based_on_distance(y_low, y_high, orders_number, df_orderlines, list_wid, list_dst, list_route, list_ord, number_of_waves):
	# Create variable to store total distance
	distance_route = 0 
	# Create waves
	# NOT NEEDED< WAVES CREATED # df_orderlines, number_of_waves = orderlines_mapping(df_orderlines, orders_number)
	# Loop all waves

	for wave_id in range(number_of_waves):
		# Listing of all locations for this wave 
		list_locs, n_locs = locations_listing(df_orderlines, wave_id)
		# Results
		wave_distance, list_chemin = create_picking_route_not_based_on_distance(Loc_orn, list_locs, y_low, y_high)
		distance_route = distance_route + wave_distance
		# Append lists of results 
		list_wid.append(wave_id)
		list_dst.append(wave_distance)
		list_route.append(list_chemin)
		list_ord.append(orders_number)

	return list_wid, list_dst, list_route, list_ord, distance_route




############################################################################
#----------      1.   BASELINE                                   ----------    



############################################################################
#---------     preparing the dataset by assigning the wave       -----------   
# Function


### Assigning wave number randomly
orders_number_comparison_baseline = dataset_for_comparison.copy()
list_orders = orders_number_comparison_baseline.orders_id.unique()
dict_map = dict(zip(list_orders, [i for i in range(1, len(list_orders)+1)]))
# Order ID mapping
orders_number_comparison_baseline['OrderID'] = orders_number_comparison_baseline['orders_id'].map(dict_map)
rrr = pd.DataFrame({"OrderID": orders_number_comparison_baseline.OrderID.unique()})
rrr['WaveID'] = (rrr.OrderID%orders_number_comparison == 0).shift(1).fillna(0).cumsum()

orders_number_comparison_baseline = pd.merge(orders_number_comparison_baseline,rrr, on = "OrderID" )
# Counting number of Waves
number_of_waves = orders_number_comparison_baseline.WaveID.max() + 1




############################################################################
#---------------     merging results -  BASELINE                     -------  
list_wid, list_dst, list_route, list_ord = [], [], [], []

results_baseline = simulation_wave_ready_waves_not_based_on_distance(y_low, y_high, orders_number_comparison, orders_number_comparison_baseline, list_wid, list_dst, list_route, list_ord, number_of_waves)


############################################################################
#---------------     merging results  BASELINE  -------  
# Create df for results
df_results_baseline = pd.DataFrame({'Wave_Number': results_baseline[0],
			   'Distance_Route': results_baseline[1],
			   'Chemins': results_baseline[2],
			   'OrderPerWave': results_baseline[3]})


print(df_results_baseline.head())

df_results_baseline["time_to_travel"] = df_results_baseline["Distance_Route"]/pickers_speed
df_results_baseline["throughput"]     = df_results_baseline["OrderPerWave"]/df_results_baseline["time_to_travel"]
round(df_results_baseline["throughput"].mean(),4)



####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################



############################################################################
#----------      2.   Travelling Salespan problem Optimisation      --------    


# Running TSP on the dataset to get throughput 
list_wid, list_dst, list_route, list_ord, list_ord_act = [], [], [], [], []
TSP_optimisation_results = simulation_wave(y_low, y_high, orders_number_comparison, dataset_for_comparison, list_wid, list_dst, list_route, list_ord, list_ord_act)
df_results_TSP_waveID = TSP_optimisation_results[6]

# Create df for results
df_results_TSP_optimisation = pd.DataFrame({'Wave_Number': TSP_optimisation_results[0],
			   'Distance_Route': TSP_optimisation_results[1],
			   'Chemins': TSP_optimisation_results[2],
			   'OrderPerWave': TSP_optimisation_results[3],
               'OrderPerWave_act':TSP_optimisation_results[5]})

print(df_results_TSP_optimisation.head())

df_results_TSP_optimisation["time_to_travel"] = df_results_TSP_optimisation["Distance_Route"]/pickers_speed
df_results_TSP_optimisation["throughput"]     = df_results_TSP_optimisation["OrderPerWave_act"]/df_results_TSP_optimisation["time_to_travel"]
round(df_results_TSP_optimisation["throughput"].mean(),4)




####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################


############################################################################
#---------------             3.   Clustering                   -------------    


# Parameters for Clustering 
distance_threshold_comarison = 68
clust_start = 0
wave_start=0

############################################################################
#---------------     split dataset into single and multi-line orders  -------   

line_orders = pd.DataFrame(dataset_for_comparison.groupby(['orders_id'])['itemID'].count()).reset_index()
line_orders= line_orders.loc[line_orders["itemID"] == 1].reset_index(drop=True)
clust_df_single_line = dataset_for_comparison[dataset_for_comparison["orders_id"].isin(line_orders["orders_id"])].reset_index(drop=True)
clust_multi_line_orders = dataset_for_comparison[~dataset_for_comparison["orders_id"].isin(line_orders["orders_id"])].reset_index(drop=True)

aaaa = df_single_line.copy()


############################################################################
#---------------     single line CLustering  -------   
dict_map_single, dict_omap_single, df_results_clust_single, Wave_max, clust_idmax = clustering_loc(clust_df_single_line, distance_threshold_comarison, 'custom', orders_number_comparison, 
	wave_start, clust_start, 'df_mono')


############################################################################
#---------------     multi line CLustering  -------   

clust_start = clust_idmax+1
wave_start  = Wave_max+1

clust_multi_line_orders = centroid_mapping(clust_multi_line_orders)
dict_map_multi, dict_omap_multi, df_results_clust_multi, Wave_max_m, clust_idmax_m = clustering_loc(clust_multi_line_orders, distance_threshold_comarison, 'custom', orders_number_comparison, 
	wave_start, clust_start, 'df_multi')


############################################################################
#---------------     merging results  CLustering  -------   
df_results_clust  = df_results_clust_single.append(pd.DataFrame(data = df_results_clust_multi), ignore_index=True)
number_of_waves = df_results_clust.WaveID.max() + 1


############################################################################
#---------------     results with clustering                         -------  

list_wid, list_dst, list_route, list_ord, list_ord_act = [], [], [], [], []
df_results_clustering_distance = simulation_wave_ready_waves(y_low, y_high, orders_number_comparison, df_results_clust, list_wid, list_dst, list_route, list_ord, number_of_waves ,list_ord_act)



############################################################################
#---------------     merging results  CLustering  -------  
# Create df for results
df_results_clustering_optimisation = pd.DataFrame({'Wave_Number': df_results_clustering_distance[0],
			   'Distance_Route': df_results_clustering_distance[1],
			   'Chemins': df_results_clustering_distance[2],
			   'OrderPerWave': df_results_clustering_distance[3],
               'OrderPerWave_act':df_results_clustering_distance[5]})


print(df_results_clustering_optimisation.head())

df_results_clustering_optimisation["time_to_travel"] = df_results_clustering_optimisation["Distance_Route"]/pickers_speed
df_results_clustering_optimisation["throughput"]     = df_results_clustering_optimisation["OrderPerWave_act"]/df_results_clustering_optimisation["time_to_travel"]
round(df_results_clustering_optimisation["throughput"].mean(),4)






####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################

####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################


############################################################################
#---------------     Clustering distance optimisation     ------------------  


#---------------     split dataset into single and multi-line orders  -------   
# OPTIMISATION  + + STREAMLIT VISUALISATION 
line_orders = pd.DataFrame(dataset_for_comparison.groupby(['orders_id'])['itemID'].count()).reset_index()
line_orders= line_orders.loc[line_orders["itemID"] == 1].reset_index(drop=True)
clust_df_single_line = dataset_for_comparison[dataset_for_comparison["orders_id"].isin(line_orders["orders_id"])].reset_index(drop=True)
clust_multi_line_orders = dataset_for_comparison[~dataset_for_comparison["orders_id"].isin(line_orders["orders_id"])].reset_index(drop=True)



optimising_clustering_distance_df = pd.DataFrame()
for opt_distance_threshold in range(50, 70):
    clust_start = 0
    wave_start=0

    #---------------     single line CLustering  -------   
    dict_map_single, dict_omap_single, df_results_clust_single, Wave_max, clust_idmax = clustering_loc(clust_df_single_line, opt_distance_threshold, 'custom', orders_number_comparison, 
                                                                                                       wave_start, clust_start, 'df_mono')
   
    #---------------     multi line CLustering  -------   
    clust_start = clust_idmax+1
    wave_start  = Wave_max+1

    clust_multi_line_orders = centroid_mapping(clust_multi_line_orders)
    dict_map_multi, dict_omap_multi, df_results_clust_multi, Wave_max_m, clust_idmax_m = clustering_loc(clust_multi_line_orders, opt_distance_threshold, 'custom', orders_number_comparison, 
                                                                                                        wave_start, clust_start, 'df_multi')
       
    #---------------     merging results  CLustering  -------   
    df_results_clust  = df_results_clust_single.append(pd.DataFrame(data = df_results_clust_multi), ignore_index=True)
    number_of_waves = df_results_clust.WaveID.max() + 1


    #---------------     results with clustering   -------  

    list_wid, list_dst, list_route, list_ord, list_ord_act = [], [], [], [], []
    df_results_clustering_distance = simulation_wave_ready_waves(y_low, y_high, orders_number_comparison, df_results_clust, list_wid, list_dst, list_route, list_ord, number_of_waves, list_ord_act)

    #---------------     saving results to df    -------  

    optimising_clustering_distance_df_interm = pd.DataFrame({'Wave_Number': df_results_clustering_distance[0],
			   'Distance_Route': df_results_clustering_distance[1],
			   'Chemins': df_results_clustering_distance[2],
			   'OrderPerWave': df_results_clustering_distance[3],
               'Clustering_distance': opt_distance_threshold,
               'OrderPerWave_act':df_results_clustering_distance[5]})


    #---------------     calculate throughput by batch    -------  

    optimising_clustering_distance_df_interm["time_to_travel"] = optimising_clustering_distance_df_interm["Distance_Route"]/pickers_speed
    optimising_clustering_distance_df_interm["throughput"]     = optimising_clustering_distance_df_interm["OrderPerWave_act"]/optimising_clustering_distance_df_interm["time_to_travel"]

    #---------------     create one dataset with appended results from different distances -------  
    optimising_clustering_distance_df = optimising_clustering_distance_df.append(pd.DataFrame(data = optimising_clustering_distance_df_interm), ignore_index=True)




#---------------     summary per distance     -------  
optimising_clustering_distance_df_summary = optimising_clustering_distance_df.groupby(["Clustering_distance"])['throughput'].mean().reset_index()
optimising_clustering_distance_df_summary["throughput"] = round(optimising_clustering_distance_df_summary["throughput"],1)

optimising_clustering_distance_df_summary["throughput"].max()
optimising_clustering_distance_df_summary["Clustering_distance"].max()




st.image("assets/clustering distance optimisation.PNG")
fig_dist_opt = px.line(optimising_clustering_distance_df_summary, x="Clustering_distance", y="throughput", title='Throughput with different distance threshhold in clustering. 3 orders per batch')

fig_dist_opt.update_layout(annotations=[{"x":68,
                                         "y":optimising_clustering_distance_df_summary["throughput"].max(), 
                                         "text": "Max =  75.2",
                                         "font":{"color":"red", "size":15}, 
                                         "arrowcolor":"red"}])
st.plotly_chart(fig_dist_opt)



####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################




####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################



############################################################################
#----------         4th Approach - pick always closest orders      ----------    


#---------------     Calculate the centroids for miltiline-orders     -------   

line_orders = pd.DataFrame(dataset_for_comparison.groupby(['orders_id'])['itemID'].count()).reset_index()
line_orders= line_orders.loc[line_orders["itemID"] == 1].reset_index(drop=True)
clust_df_single_line = dataset_for_comparison[dataset_for_comparison["orders_id"].isin(line_orders["orders_id"])].reset_index(drop=True)
clust_df_multi_line_orders = dataset_for_comparison[~dataset_for_comparison["orders_id"].isin(line_orders["orders_id"])].reset_index(drop=True)


clust_df_single_line['Coord_Cluster'] = clust_df_single_line['Coord_hall'] 
clust_df_multi_line_orders = centroid_mapping(clust_df_multi_line_orders)
df_dataset_with_centroids  = clust_df_single_line.append(pd.DataFrame(data = clust_df_multi_line_orders), ignore_index=True)
   

#---------------     keep dataset with order & Coord_Cluster     -------   

df_dataset_with_centroids_unique = df_dataset_with_centroids[["orders_id","Coord_Cluster"]].drop_duplicates('orders_id', keep='first')
df_dataset_with_centroids_unique = df_dataset_with_centroids_unique.sort_values("orders_id").reset_index(drop=True)


#---------------     start assigning all orders to batches      -------   
# 1. closest to depot --> x1
# 2. add closest to x1 --> x2
# 3. add closest to x2 --> x3
# 4. if number of orders = order_threshold --> go back to depot. 
# 5. repeat till all orders are served 


list_locs = list(df_dataset_with_centroids_unique['Coord_Cluster'].apply(lambda t: literal_eval(t)).values)
list_locs = list(k for k,_ in itertools.groupby(list_locs))
len(list_locs)

depot_location = [0,0,0]
wave_distance = 0
list_orders_per_batch = []
orders_per_batch  = orders_number_comparison  # 3
start_loc = depot_location
wave_number = 0

df_dataset_with_centroids_unique['Coord_Cluster'] = df_dataset_with_centroids_unique['Coord_Cluster'].apply(lambda t: literal_eval(t)).values
df_dataset_with_centroids_unique['Coord_Cluster'] = df_dataset_with_centroids_unique['Coord_Cluster'].astype(str)
df_dataset_with_centroids_unique["WaveID"] = -1  # initialising a variable 
  
 
# =============================================================================

while len(list_locs) > 0:
	len(list_locs)
	list_dist = [distance_picking(start_loc, i, y_low, y_high) for i in list_locs]
	distance_next = min(list_dist)
	#index_min = list_dist.index(min(list_dist))
	next_order = list_dist.index(min(list_dist)) # index with lowest distance
	next_loc = list_locs[next_order] # Next location is the first location with distance = min (**)
	list_locs.remove(next_loc)      # Next location is removed from the list of candidates
	list_orders_per_batch.append(next_order)
	start_loc = next_loc
	
	df_dataset_with_centroids_unique.loc[(df_dataset_with_centroids_unique["Coord_Cluster"] == str(next_loc) ) & (df_dataset_with_centroids_unique["WaveID"] < 0 ), "WaveID" ] = wave_number
	
	#if len(list_orders_per_batch) >= orders_per_batch:
	if (df_dataset_with_centroids_unique.loc[df_dataset_with_centroids_unique["WaveID"] == wave_number , "orders_id"].count() ) >=  orders_per_batch: ## 
		list_orders_per_batch = []
		wave_number += 1
    

# =============================================================================
#---------------     our dataset with the waves     -------    

# add to dataset_for_comparison the wave number
dataset_for_comparison_3closest = pd.merge(dataset_for_comparison,df_dataset_with_centroids_unique[["orders_id", "WaveID"]], on = "orders_id" ) 

# =============================================================================
#---------------      Now we need to calculate throughput     -------    
number_of_waves = df_dataset_with_centroids_unique.WaveID.max() + 1


############################################################################
#---------------     results with clustering                         -------  

list_wid, list_dst, list_route, list_ord, list_ord_act = [], [], [], [], []
df_results_3closest = simulation_wave_ready_waves(y_low, y_high, orders_number_comparison, dataset_for_comparison_3closest, list_wid, list_dst, list_route, list_ord, number_of_waves ,list_ord_act)


############################################################################
#---------------     merging results  CLustering  -------  
# Create df for results
df_results_3closest_optimisation = pd.DataFrame({'Wave_Number': df_results_3closest[0],
			   'Distance_Route': df_results_3closest[1],
			   'Chemins': df_results_3closest[2],
			   'OrderPerWave': df_results_3closest[3],
               'OrderPerWave_act':df_results_3closest[5]})


print(df_results_3closest_optimisation.head())

df_results_3closest_optimisation["time_to_travel"] = df_results_3closest_optimisation["Distance_Route"]/pickers_speed
df_results_3closest_optimisation["throughput"]     = df_results_3closest_optimisation["OrderPerWave_act"]/df_results_3closest_optimisation["time_to_travel"]
round(df_results_3closest_optimisation["throughput"].mean(),4)


#"The average throughput for 1 hour is using TSP + 3 closest orders:" , round(df_results_3closest_optimisation["throughput"].mean(),1) , "."





####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################

############################################################################
#---------------     Visualize all the results  -------  
# streamlit


df_results_baseline["method"]  = "baseline"
df_results_TSP_optimisation["method"]  = "TSP"
df_results_clustering_optimisation["method"] = "TSP + Clustering"
df_results_3closest_optimisation["method"] = "TSP + 3 closest orders"


df_results_all = df_results_baseline.append(df_results_TSP_optimisation)
df_results_all = df_results_all.append(df_results_clustering_optimisation)
df_results_all = df_results_all.append(df_results_3closest_optimisation)
df_results_all["method"] = df_results_all["method"].astype('category')



st.write(""" #### 1. BASELINE  """)
"The average throughput for 1 hour in baseline :" , round(df_results_baseline["throughput"].mean(),1) , "."


st.write(""" #### 2. TSP  """)
"The average throughput for 1 hour is using TSP:" , round(df_results_TSP_optimisation["throughput"].mean(),1) , "."


st.write(""" #### 3. TSP + Clustering """)
"The average throughput for 1 hour is using TSP + clustering (68m between the orders) :" , round(df_results_clustering_optimisation["throughput"].mean(),1) , "."


st.write(""" #### 4. TSP + 3 closest orders """)
"The average throughput for 1 hour is using TSP + 3 closest orders:" , round(df_results_3closest_optimisation["throughput"].mean(),1) , "."


####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################


option = st.radio('', ( "Distance",'Box Plot', 'Histogram'))

if option == 'Box Plot':
    fig = px.box(df_results_all, x="method", y="throughput", color="method")
    fig.update_traces(quartilemethod="exclusive") # or "inclusive", or "linear" by default
    st.plotly_chart(fig)
 

elif option == 'Histogram':
    fig2 = px.histogram(df_results_all, x="throughput", color="method", marginal="rug", # can be `box`, `violin`
                         hover_data=df_results_all.columns, nbins=100)
    st.plotly_chart(fig2)

elif option == 'Distance':
    fig4 = px.histogram(df_results_all, x="Distance_Route", color="method", marginal="rug", # can be `box`, `violin`
                         hover_data=df_results_all.columns, nbins=40)
    st.plotly_chart(fig4)



df_results_all.method.unique()


####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################





####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################


####################################################################################################
#----------        5. ADD Time in full - 2nd optimisation objective                 ----------------    


# =============================================================================
#               A FUNCTION FOR TIME IN FULL CALCULATION 
# =============================================================================

#dstart = start of the shift 

def calculate_time_in_full(dataset_with_orders_WaveID, dataset_with_throughput, dstart ):    

    #---------------      dataset with orders, shipping date and Wave ID      -------    
    timeInfull_byorder = dataset_with_orders_WaveID[["orders_id", "date","WaveID"]].drop_duplicates(['orders_id',"WaveID"], keep='first')


    #---------------      dataset with Throughput, distance and time to travel       -------    
    timeInfull = dataset_with_throughput.copy() 
    timeInfull = timeInfull[["Wave_Number", "Distance_Route","time_to_travel", "throughput"]]
    timeInfull["seconds_to_travel"] = pd.to_timedelta(timeInfull["time_to_travel"]*60*60,  unit='s')


    pickup_start = dstart
    for waveID in range(0, timeInfull.Wave_Number.max()+1):
        pickup_start = pickup_start + np.mean(timeInfull.loc[timeInfull["Wave_Number"] == waveID, "seconds_to_travel"])
        timeInfull.loc[timeInfull["Wave_Number"] == waveID, "order_completion_time"] = pickup_start 


    # =============================================================================
    #---------------      CALCULATE TIME IN FULL                -------------------    

    timeInfull = pd.merge(timeInfull_byorder,timeInfull[["Wave_Number", "Distance_Route", "throughput","seconds_to_travel", "order_completion_time"]], left_on= "WaveID" ,right_on="Wave_Number",)
    timeInfull["time_in_full"] =  round((timeInfull["order_completion_time"] - timeInfull["date"]  ).dt.total_seconds() / 60,1)

    return timeInfull






# =============================================================================
#               Calculate time in full for Baseline
#orders_number_comparison_baseline
#df_results_baseline

timeInfull_base = calculate_time_in_full(orders_number_comparison_baseline, df_results_baseline, dstart )
#"Time in full for Base:" , str(round(timeInfull_base["time_in_full"].mean(),1))

# =============================================================================
#               Calculate time in full for TSP 
# df_results_TSP_waveID
# df_results_TSP_optimisation

timeInfull_TSP = calculate_time_in_full(df_results_TSP_waveID, df_results_TSP_optimisation, dstart )
#"Time in full for TSP:" , str(round(timeInfull_TSP["time_in_full"].mean(),1))


# =============================================================================
#               Calculate time in full for TSP & Clustering
# df_results_clust
# df_results_clustering_optimisation

timeInfull_clustering = calculate_time_in_full(df_results_clust, df_results_clustering_optimisation, dstart )
#"Time in full for TSP & Clustering:" , str(round(timeInfull_clustering["time_in_full"].mean(),1))


# =============================================================================
#               Calculate time in full for 3 closest
# dataset_for_comparison_3closest
# df_results_3closest_optimisation
timeInfull_3closest = calculate_time_in_full(dataset_for_comparison_3closest, df_results_3closest_optimisation, dstart )
#"Time in full for 3 closest orders:" , str(round(timeInfull_3closest["time_in_full"].mean(),1))



 




#---------------------------------------------------------------------------
#continue_button(36) 
#continue_button(37) 
continue_button(38)

####################################################################################################
#----------        5. ADD Time in full - 2nd optimisation objective                 ----------------    



st.image("assets/time_clocks.jpg", width = 700)

st.write(""" # Time In Full 

#### Average time (in minutes) when order is completed comparing to the deadline 
#         

This objective can help us ensure, that we ship all out orders on time. 
Idealli we would like to ship before the shipping date and therefore deliver product faster to the clients
and increase customer satisfaction.

Previously we wanted to increase the Throughput, but having the Time in Full - we would like to minimize it. 

Lets explore how our developed solutions perform based on ** Time In Full metric **.
    

#     
""")


#---------------------------------------------------------------------------
continue_button(39) 
#continue_button(40) 
#continue_button(41)
          

        
col1, mid, col2 = st.beta_columns([40,70,40])
with col1:
    col1.header("Throughput")   
    "**1. Baseline:** ", round(df_results_baseline["throughput"].mean(),1) 
    st.write(""" #### """)
    "**2. TSP :** ", round(df_results_TSP_optimisation["throughput"].mean(),1) 
    st.write(""" #### """)
    "**3. TSP + Clustering: ** ", round(df_results_clustering_optimisation["throughput"].mean(),1) 
    st.write(""" #### """)
    "**4. TSP + 3 closest orders: **" , round(df_results_3closest_optimisation["throughput"].mean(),1) 
with mid:
    st.image("assets/double objective.png", width = 300)
with col2:
    col2.header("Time in full") 
    "**1. Baseline:** ", round(timeInfull_base["time_in_full"].mean(),1) 
    st.write(""" #### """)
    "**2. TSP :** ", round(timeInfull_TSP["time_in_full"].mean(),1) 
    st.write(""" #### """)
    "**3. TSP + Clustering: ** ", round(timeInfull_clustering["time_in_full"].mean(),1) 
    st.write(""" #### """)
    "**4. TSP + 3 closest orders: **" , round(timeInfull_3closest["time_in_full"].mean(),1) 
     
     
     
     
# =============================================================================
#      
# "**1. Baseline Distance_Route:** ", round(timeInfull_base["Distance_Route"].sum(),1) 
# "**2. TSP Distance_Route:** ", round(timeInfull_TSP["Distance_Route"].sum(),1) 
# "**3. TSP + Clustering Distance_Route: ** ", round(timeInfull_clustering["Distance_Route"].sum(),1) 
# "**4. TSP + 3 closest orders Distance_Route: **" , round(timeInfull_3closest["Distance_Route"].sum(),1) 
# 
# =============================================================================



####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################

####################################################################################################=============================================================
####################################################################################################=============================================================
####################################################################################################=============================================================
####################################################################################################=============================================================

# =============================================================================
#                          BRUTE FORCE OPTIMISATION 
# =============================================================================


# =============================================================================
#--------------------------- Parameters ------------------------------
numer_of_datasets = 30  # How many datasets I would like to run in SOFT-BRUTE-FORCE 

# =============================================================================
#--------------------------- create WaveIDs ------------------------------
wave_ID = list(range(0,50)) #50
wave_ID = wave_ID * 3
wave_ID.sort()
len(wave_ID)

# =============================================================================
#--------------------------- create Dataframes with different order ------------------------------

order_IDs_WaveID = pd.DataFrame({})
for i in range(0, numer_of_datasets):
    orders_id = list(range(0,150)) #150
    random.shuffle(orders_id)  
    RunID_i = pd.DataFrame({"orders_id": orders_id,
                            "WaveID": wave_ID,
                            "runID":i})
    order_IDs_WaveID = order_IDs_WaveID.append(RunID_i)


# =============================================================================
#--------------------------- loop to Calculate Throughput & Time in Full ------


dfID_i_results_all = pd.DataFrame({})   # the dataset that will have throughput && time_in_full

for i in range(0, numer_of_datasets):
    dfID_i = order_IDs_WaveID.loc[order_IDs_WaveID["runID"] == i]
    dataset_for_comparison_MULTI = pd.merge(dataset_for_comparison, dfID_i, on = "orders_id").sort_values(by=['WaveID', "orders_id"])
    number_of_waves = order_IDs_WaveID.WaveID.max() + 1

    # =============================================================================
    #--------------------------- Throughput   ------------------------------
    list_wid, list_dst, list_route, list_ord, list_ord_act = [], [], [], [], []
    dfID_i_results_wave = simulation_wave_ready_waves(y_low, y_high, orders_number_comparison, dataset_for_comparison_MULTI, list_wid, list_dst, list_route, list_ord, number_of_waves ,list_ord_act)

    dfID_i_results_throughput = pd.DataFrame({'Wave_Number': dfID_i_results_wave[0],
			   'Distance_Route': dfID_i_results_wave[1],
			   'Chemins': dfID_i_results_wave[2],
			   'OrderPerWave': dfID_i_results_wave[3],
               'OrderPerWave_act':dfID_i_results_wave[5]})

    #---------------     calculate throughput by batch    -------  
    dfID_i_results_throughput["time_to_travel"] = dfID_i_results_throughput["Distance_Route"]/pickers_speed
    dfID_i_results_throughput["throughput"]     = round(dfID_i_results_throughput["OrderPerWave_act"]/dfID_i_results_throughput["time_to_travel"],1)

    #--------------------------- Time in Full  ------------------------------
    dfID_i_results_timeInfull = calculate_time_in_full(dataset_for_comparison_MULTI, dfID_i_results_throughput, dstart )
    dfID_i_results_timeInfull["runID"] = i

    dfID_i_results_all = dfID_i_results_all.append(dfID_i_results_timeInfull)
    print(i)


#--------------------------- get summary of the results   ------------------------------
dfID_i_results_all_for_optimisation = pd.DataFrame(dfID_i_results_all.groupby(by = ["runID"], as_index=False)["throughput","time_in_full"].mean())
dfID_i_results_all_for_optimisation["throughput"]   = round(dfID_i_results_all_for_optimisation["throughput"],1)
dfID_i_results_all_for_optimisation["time_in_full"] = round(dfID_i_results_all_for_optimisation["time_in_full"],1)

#dfID_i_results_all_for_optimisation.to_csv("dfID_i_results_all_for_optimisation_250.csv", index=False)
#dfID_i_results_all_for_optimisation.to_csv("dfID_i_results_all_for_optimisation_57000__.csv", index=False)





# ==========================================================================================================================================================
# TEST 
# ==========================================================================================================================================================
i=57038
test = dfID_i_results_all.copy()
orders_id1 = df_results_clust.orders_id.unique()
RunID_i = pd.DataFrame({})
RunID_i  = df_results_clust[["orders_id", "WaveID"]]
RunID_i["runID"] = i

RunID_i = RunID_i.drop_duplicates()

len(orders_id1)

if i>0:
    dfID_i = RunID_i.loc[RunID_i["runID"] == i]
    dataset_for_comparison_MULTI = pd.merge(dataset_for_comparison, dfID_i, on = "orders_id").sort_values(by=['WaveID', "orders_id"])
    number_of_waves = dfID_i.WaveID.max() + 1

    # =============================================================================
    #--------------------------- Throughput   ------------------------------
    list_wid, list_dst, list_route, list_ord, list_ord_act = [], [], [], [], []
    dfID_i_results_wave = simulation_wave_ready_waves(y_low, y_high, orders_number_comparison, dataset_for_comparison_MULTI, list_wid, list_dst, list_route, list_ord, number_of_waves ,list_ord_act)

    dfID_i_results_throughput = pd.DataFrame({'Wave_Number': dfID_i_results_wave[0],
			   'Distance_Route': dfID_i_results_wave[1],
			   'Chemins': dfID_i_results_wave[2],
			   'OrderPerWave': dfID_i_results_wave[3],
               'OrderPerWave_act':dfID_i_results_wave[5]})

    #---------------     calculate throughput by batch    -------  
    dfID_i_results_throughput["time_to_travel"] = dfID_i_results_throughput["Distance_Route"]/pickers_speed
    dfID_i_results_throughput["throughput"]     = round(dfID_i_results_throughput["OrderPerWave_act"]/dfID_i_results_throughput["time_to_travel"],1)
    dfID_i_results_throughput["throughput"] .mean()

    #--------------------------- Time in Full  ------------------------------
    dfID_i_results_timeInfull = calculate_time_in_full(dataset_for_comparison_MULTI, dfID_i_results_throughput, dstart )
    dfID_i_results_timeInfull["runID"] = i
    dfID_i_results_timeInfull["time_in_full"].mean()


    dfID_i_results_all = dfID_i_results_all.append(dfID_i_results_timeInfull)









# ==========================================================================================================================================================
# 
# ==========================================================================================================================================================
#--------- STREAMLIT  Throughput & Time in Full ------
st.write(""" #

# Optimising two objectives 

As we just saw - one approach might be opptimal for one objective, but when we have two objectives 
we need to find the golden balance. 

Let's run multiple different assignments of orders to batches and let's see their performance one
both objectives.
           
### The performance of various batching assignments:
         """)

fig36 = px.scatter(dfID_i_results_all_for_optimisation, x="time_in_full", y="throughput", hover_name="runID")
st.plotly_chart(fig36)


st.write(""" ### 1000 different assignments""")
dfID_i_results_all_for_optimisation_1000 = pd.read_csv('dfID_i_results_all_for_optimisation_1000.csv')
fig37 = px.scatter(dfID_i_results_all_for_optimisation_1000, x="time_in_full", y="throughput", hover_name="runID")
st.plotly_chart(fig37)


st.write(""" ### 10,000 different assignments""")
dfID_i_results_all_for_optimisation_10000 = pd.read_csv('dfID_i_results_all_for_optimisation_10000.csv')
fig39 = px.scatter(dfID_i_results_all_for_optimisation_10000, x="time_in_full", y="throughput", hover_name="runID")
st.plotly_chart(fig39)
 

st.write(""" ### 57,000 different assignments""")
dfID_i_results_all_for_optimisation_57000 = pd.read_csv('dfID_i_results_all_for_optimisation_57000.csv')
fig39 = px.scatter(dfID_i_results_all_for_optimisation_57000, x="time_in_full", y="throughput", hover_name="runID")
st.plotly_chart(fig39)
 


st.image("assets/to be continued.jpg")


####################################################################################################=============================================================
####################################################################################################=============================================================
####################################################################################################=============================================================
####################################################################################################=============================================================

####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################



# =============================================================================
#                          combinations 
# =============================================================================
# =============================================================================


# =============================================================================
# import itertools
# from itertools import combinations
# 
# list_of_orders = list(range(0,10))
# #list_of_orders = dataset_for_comparison.orders_id.unique()
# comb = list(combinations(list_of_orders, 3))
# len(comb)  
# comb
# 
# # =============================================================================
# #   PERMUTATIONS----- 9 orders 
# # =============================================================================
# 
# list_of_orders = list(range(0,9))
# lists_of_orders_perm = list(itertools.permutations(list_of_orders))
# len(lists_of_orders_perm)
# 
# lists_of_orders_perm[0:9]
# 
# 
# =============================================================================


####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################

####################################################################################################
####################################################################################################
####################################################################################################
####################################################################################################




# =============================================================================
#                          combinations 
# =============================================================================
# =============================================================================
# 
# 
# import itertools
# from itertools import combinations
# 
# # Get all combinations of [1, 2, 3]
# # and length 2
# 
# list_of_orders = list(range(0,10))
# #list_of_orders = dataset_for_comparison.orders_id.unique()
# comb = list(combinations(list_of_orders, 3))
# len(comb)  
# 
# 
# solution1 = list()
# solution2 = list()
# solution_for_testing = list()
# 
# solution1.extend(comb[1])
# 
# solution_for_testing.extend(comb[2])
# solution1
# solution2
# len(comb[2])
# len(solution1)
# 
# 
# i=1
# j=1
# final_solution = list()
# solution1 = list()
# solution_for_testing = list()
# 
# for i in range(0, len(comb)):  
#     solution1.extend(comb[i])
#     
#     for j in range(0, len(comb)):
#         solution_for_testing = solution1
#         solution_for_testing.extend(comb[j])
#         if len(set(solution_for_testing)) == (len(solution1) + len(comb[j])):
#             print("its true")
#             solution1.extend(comb[j])
#         else: 
#             solution_for_testing = solution1
# 
# 
# if len(solution1) >= 10:
#     print("its 49orders")
#     final_solution.append(solution1)
#     solution1 = list()
#     solution_for_testing = list()
# 
# final_solution
# 
# 
# 
# 
# 
# solution1 in solution2
# 
# # Print the obtained combinations
# for i in list(comb):
#     print(i)
# 
# 
# [item for sublist in comb[0] for item in sublist]
# 
# 
# a = comb[0]
# tupe(a)
# 
# # =============================================================================
# # 
# # =============================================================================
# # =============================================================================
# # 
# # =============================================================================
# # =============================================================================
# #   PERMUTATIONS----- 21 orders 
# # =============================================================================
# 
# aa = list_of_orders = list(range(0,9))
# #aa = list(itertools.permutations([1, 2, 3]))
# aa[0] 
# 
# 
# lists_of_orders_perm = list(itertools.permutations(list_of_orders))
# len(lists_of_orders_perm)
# 
# 
# lists_of_orders_perm[0:3]
# 
# 
# itertools.combinations(list_of_orders, 3)
# # =============================================================================
# # 
# # =============================================================================
# from itertools import combinations
#   
# 
# 
# list_of_orders = list(dataset_for_comparison.orders_id.unique())
# 
# 
# 
# 
# dataset_for_comparison.orders_id.unique()
# 
# # =============================================================================
# # 
# # =============================================================================
# 
# 
# # Python program to print all permutations using
# # Heap's algorithm
#  
# # Generating permutation using Heap Algorithm
# def heapPermutation(a, size):
#  
#     # if size becomes 1 then prints the obtained
#     # permutation
#     if size == 1:
#         print(a)
#         return
#  
#     for i in range(size):
#         heapPermutation(a, size-1)
#  
#         # if size is odd, swap 0th i.e (first)
#         # and (size-1)th i.e (last) element
#         # else If size is even, swap ith
#         # and (size-1)th i.e (last) element
#         if size & 1:
#             a[0], a[size-1] = a[size-1], a[0]
#         else:
#             a[i], a[size-1] = a[size-1], a[i]
# 
#  
# # Driver code
# a = [1, 2, 3, 4, 5]
# n = len(a)
# w = heapPermutation(a, n)
#  
# 
# 
# 
# 
# 
# 
# # =============================================================================
# # 
# # =============================================================================
# 
# # 6 orders 
# test = 4
# test_list=list()
# 
# i=1
# j=2
# for i in range(1, test+1):
#     print(i, "first")
#     if i not in test_list:
#         test_list.append(i)
#         for j in range(1, test+1):
#             if i != j:
#                 if j not in test_list:
#                     print(j)
#                     test_list.append(j)
#     
# 
# 
# 
# 
# 
# 
# # =============================================================================
# # 
# # =============================================================================
# 
# 
# 
# 
# from itertools import permutations
# 
# 
# 
# step = 0
# 
# string = "12345"
# i = 2
# def permutations(string, step = 0):
#     if step == len(string):
#         # we've gotten to the end, print the permutation
#         print("".join(string))
#     for i in range(step, len(string)):
#         # copy the string (store as array)
#         string_copy = [c for c in string]
#          # swap the current index with the step
#         string_copy[step], string_copy[i] =string_copy[i], string_copy[step]
#          # recurse on the portion of the stringthat has not been swapped yet
#         permutations(string_copy, step + 1)
# print (permutations ('12345'))
# 
# 
# def permutations(string, step = 0):
#     if step == len(string):
#         # we've gotten to the end, print the permutation
#         print("".join(string))
#     for i in range(step, len(string)):
#         # copy the string (store as array)
#         string_copy = [c for c in string]
#          # swap the current index with the step
#         string_copy[step], string_copy[i] =string_copy[i], string_copy[step]
#          # recurse on the portion of the stringthat has not been swapped yet
#         permutations(string_copy, step + 1)
# print (permutations ('12345'))
# 
# 
# 
# 
# 
# 
# =============================================================================














########################################################################################################################################################################################################
########################################################################################################################################################################################################
########################################################################################################################################################################################################
########################################################################################################################################################################################################


################################################################################################################
#---------------     Clustering distance optimisation - single- and multi- lines together     ------------------  
################################################################################################################
# at some point we could cluster the locations together - and compare 
# performance with separate single-line clustering + separate multi-line clustering


# =============================================================================
# 
# #---------------     split dataset into single and multi-line orders  -------   
# 
# line_orders = pd.DataFrame(dataset_for_comparison.groupby(['orders_id'])['itemID'].count()).reset_index()
# line_orders= line_orders.loc[line_orders["itemID"] == 1].reset_index(drop=True)
# clust_df_single_line = dataset_for_comparison[dataset_for_comparison["orders_id"].isin(line_orders["orders_id"])].reset_index(drop=True)
# clust_df_multi_line_orders = dataset_for_comparison[~dataset_for_comparison["orders_id"].isin(line_orders["orders_id"])].reset_index(drop=True)
# 
# 
# clust_df_single_line['Coord_Cluster'] = clust_df_single_line['Coord_hall'] 
# clust_df_multi_line_orders = centroid_mapping(clust_df_multi_line_orders)
# df_results_clust  = clust_df_single_line.append(pd.DataFrame(data = clust_df_multi_line_orders), ignore_index=True)
#    
# 
# 
# 
# optimising_clustering_distance_df = pd.DataFrame()
# for opt_distance_threshold in range(50, 80):
#     clust_start = 0
#     wave_start=0
# 
#     #---------------     CLustering / waving  -------   
#     clustering_loc_results = clustering_loc(df_results_clust, opt_distance_threshold, 'custom', orders_number_comparison, 
#                                                                                                        wave_start, clust_start, 'df_combined')
# 
#     df_results_clust_combined = clustering_loc_results[2]
#     #---------------     Assigning batches and calculating distance   ------- 
#     number_of_waves = df_results_clust_combined.WaveID.max() + 1
#     list_wid, list_dst, list_route, list_ord, list_ord_act = [], [], [], [], []
#     df_results_clustering_distance = simulation_wave_ready_waves(y_low, y_high, orders_number_comparison, df_results_clust_combined, list_wid, list_dst, list_route, list_ord, number_of_waves, list_ord_act)
# 
# 
#     #---------------     saving results to df    -------  
# 
#     optimising_clustering_distance_df_interm = pd.DataFrame({'Wave_Number': df_results_clustering_distance[0],
# 			   'Distance_Route': df_results_clustering_distance[1],
# 			   'Chemins': df_results_clustering_distance[2],
# 			   'OrderPerWave': df_results_clustering_distance[3],
#                'Clustering_distance': opt_distance_threshold,
#                'OrderPerWave_act':df_results_clustering_distance[5]})
# 
# 
#     #---------------     calculate throughput by batch    -------  
# 
#     optimising_clustering_distance_df_interm["time_to_travel"] = optimising_clustering_distance_df_interm["Distance_Route"]/pickers_speed
#     optimising_clustering_distance_df_interm["throughput"]     = optimising_clustering_distance_df_interm["OrderPerWave_act"]/optimising_clustering_distance_df_interm["time_to_travel"]
# 
#     #---------------     create one dataset with appended results from different distances -------  
#     optimising_clustering_distance_df = optimising_clustering_distance_df.append(pd.DataFrame(data = optimising_clustering_distance_df_interm), ignore_index=True)
# 
# 
# 
# 
# #---------------     summary per distance     -------  
# optimising_clustering_distance_df_summary = optimising_clustering_distance_df.groupby(["Clustering_distance"])['throughput'].mean().reset_index()
# optimising_clustering_distance_df_summary["throughput"] = round(optimising_clustering_distance_df_summary["throughput"],1)
# 
# optimising_clustering_distance_df_summary["throughput"].max()
# optimising_clustering_distance_df_summary["Clustering_distance"].max()
# 
# 
# st.write("Clustering together single- and milti- line orders")
# fig_dist_opt = px.line(optimising_clustering_distance_df_summary, x="Clustering_distance", y="throughput", title='Clustering together single- and milti- line orders')
# 
# 
# fig_dist_opt.update_layout(annotations=[{"x":68,
#                                          "y":75.2, 
#                                          "text": "throughput from separate clustering =  75.2",
#                                          "font":{"color":"red", "size":15}, 
#                                          "arrowcolor":"red"}])
# 
#  
# st.plotly_chart(fig_dist_opt)
# 
# 
# =============================================================================






########################################################################################################################################################################################################
########################################################################################################################################################################################################
########################################################################################################################################################################################################
########################################################################################################################################################################################################


########################################################################################################################################################################################################
########################################################################################################################################################################################################
########################################################################################################################################################################################################
########################################################################################################################################################################################################



########################################################################################################################################################################################################
########################################################################################################################################################################################################
########################################################################################################################################################################################################
########################################################################################################################################################################################################



########################################################################################################################################################################################################
########################################################################################################################################################################################################
########################################################################################################################################################################################################
########################################################################################################################################################################################################


