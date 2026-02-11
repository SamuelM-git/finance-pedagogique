import streamlit as st
import pandas as pd

st.title("Apprendre à gérer son budget 💶")

revenu = st.number_input("Revenu mensuel (€)", min_value=0)
depenses = st.number_input("Dépenses mensuelles (€)", min_value=0)

reste = revenu - depenses

st.write("Reste à vivre :", reste, "€")

if reste > 0:
    st.success("Bravo ! Vous pouvez épargner.")
else:
    st.error("Attention : dépenses supérieures aux revenus.")
