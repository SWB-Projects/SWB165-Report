#!/usr/bin/env python
# coding: utf-8
# author: DJ
from multiapp import MultiApp
import streamlit as st

# import function from app1
from app1 import f1

def main():
    app = MultiApp()
    # add app 1
    app.add_app("Ranking", f1)
 
    app.run()
if __name__ == "__main__":
  main()