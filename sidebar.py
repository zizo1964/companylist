import streamlit as st

def sidebar():
    # st.sidebar.title('Sidebar Title')
    st.sidebar.title('Company Information')
    st.sidebar.header('Sidebar Header')
    st.sidebar.write('This is the sidebar content.')

    st.empty()

# import streamlit as st

    # # Using object notation
    # add_selectbox = st.sidebar.selectbox(
    #     "How would you like to be contacted?",
    #     ("Email", "Home phone", "Mobile phone")
    # )
    
# # Using "with" notation
# with st.sidebar:
#     add_radio = st.radio(
#         "Choose a shipping method",
#         ("Standard (5-15 days)", "Express (2-5 days)")
#     )