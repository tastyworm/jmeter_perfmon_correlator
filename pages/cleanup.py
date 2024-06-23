import streamlit as st
from config.config import set_page_config
import os
import shutil

set_page_config()



# if there are any files in the formatted_data folder, delete them   
folderlist = ['chart_data', 'formatted_data', 'uploaded_data']

# if there are files in the folders listed above, write a message saying that the files are being deleted
if any([len(os.listdir(folder)) > 0 for folder in folderlist]):
    st.info("Found some old files here to clean up. One moment please...")

# Initialize the progress bar
progress_bar = st.progress(0)

# Initialize a counter
processed_files = 0

for folder in folderlist:
    # Calculate the total number of files in the current folder
    total_files = sum([len(files) for r, d, files in os.walk(folder)])

    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))

        # Update the counter
        processed_files += 1

        # Update the progress bar
        progress = min(processed_files / total_files, 1)
        progress_bar.progress(progress)

# Clear any session states
st.session_state.clear()

st.switch_page("main.py")

