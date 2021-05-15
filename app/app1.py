#!/usr/bin/env python
# coding: utf-8
# author: DJ

# app1.py
# basic packages
import os, glob, datetime, base64

# streamlit
import streamlit as st

# data processing
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from io import StringIO, BytesIO

# ranking
from skcriteria.madm import simple
from skcriteria import Data

# upload data
def file_selector(folder_path="."):
    filenames = os.listdir(folder_path)
    selected_filename = st.selectbox('Select a file', filenames)
    return os.path.join(folder_path, selected_filename)

# download result
def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine="openpyxl")
    df.to_excel(writer, sheet_name='Ranking', index=False)
    writer.save()
    processed_data = output.getvalue()
    return processed_data

def get_table_download_link(df):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    val = to_excel(df)
    b64 = base64.b64encode(val)  # val looks like b'...'
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="Ranking_Results.xlsx">Download excel file</a>' # decode b'abc' => abc

def f1():
    st.title("Ranking Algorithm")
    st.markdown("<description> Rapid ranking based on indicator data </description>",
                unsafe_allow_html = True)
    st.sidebar.title("")
    #--------------------------------------------------#
    # Upload data
    #--------------------------------------------------#
    st.markdown("## 1. Upload Your File",
                unsafe_allow_html = True)
    data_file = st.file_uploader("Supported Format: xlsx", type=["xlsx"])

    # read data
    if data_file is not None:
        inputData = pd.read_excel(data_file, engine = "openpyxl") 
        # show the head of data
        is_show_data = st.checkbox("Show content of your file?")
        if is_show_data:
            st.write(inputData.head())
        #--------------------------------------------------#
        # Settings    
        #--------------------------------------------------#
        st.markdown("## ",
                    unsafe_allow_html = True)   
        st.markdown("## 2. Settings",
                unsafe_allow_html = True)
        numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
        numDF = inputData.select_dtypes(include = numerics)
        numCols = numDF.columns.tolist()

        # non-numerical columns 
        idCols = [col for col in inputData.columns.tolist() if col not in numDF]
        #--------------------------------------------------#    
        # Decide indicator relationship with the ranking 
        #--------------------------------------------------#
        st.markdown("### Select Positive Indicators",
                unsafe_allow_html = True) 

        # select positive indicators
        stPos = st.multiselect("Positive Indicator Columns", numCols)
        unselectedCols = [col for col in numCols  if col not in stPos]
        # select negative indicators
        st.markdown("### Select Negative Indicators",
                unsafe_allow_html = True) 
        stNeg = st.multiselect("Negative Indicator Columns", unselectedCols)
        #--------------------------------------------------#
        # collect user provided information
        #--------------------------------------------------#
        criteria =[]
        selectedCols = []
        for colName in numCols:
            if colName in stPos:
                criteria.append(max)
                selectedCols.append(colName)
            elif colName in stNeg:
                criteria.append(min)
                selectedCols.append(colName)
            else:
                pass
            print("criteria",criteria)
            print(selectedCols)

        #--------------------------------------------------#
        # Run Ranking Algorithm
        #--------------------------------------------------#
        st.markdown("## ",
                    unsafe_allow_html = True)   
        if len(selectedCols) > 0:
            st.markdown("## 3. Run Ranking Algorithm",
                    unsafe_allow_html = True)   
            if st.button('Run'):
                # X   
                X = inputData[selectedCols]

                # fill NA
                X.fillna(0,inplace=True)

                # scaling X
                min_max_scaler =MinMaxScaler()
                X_scaled_values = min_max_scaler.fit_transform(X.values)

                # format as dataframe
                X_scaled = pd.DataFrame(X_scaled_values, columns=X.columns)

                # prepare input data for ranking
                criteria_data = Data(X_scaled, 
                        criteria,
                        #anames=y,
                        cnames = X_scaled.columns)
                #------------------------------------#        
                # ranking algorithm: WeightedProduct  
                #------------------------------------#    
                dp = simple.WeightedProduct()
                # run ranking algorithm 
                dec_dp = dp.decide(criteria_data)
                
                #--------------------------------------------------#
                # Save results
                #--------------------------------------------------#
                # add ranking result back to selected data
                X.loc[:, "Rank_using_selected_columns"] = dec_dp.rank_

                # add id cols back 
                outputData = pd.concat([inputData[idCols].reset_index(drop=True), X], axis =1)      
                # sort if needed
                #outputData =outputData.sort_values(by ="Rank_using_selected_columns")              
                #--------------------------------------------------#
                # Download results
                #--------------------------------------------------#
                st.markdown("## ",
                        unsafe_allow_html = True)   
                st.markdown("## 4. Download Results",
                        unsafe_allow_html = True)      
                st.markdown(get_table_download_link(outputData), 
                            unsafe_allow_html=True)