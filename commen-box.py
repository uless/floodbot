import streamlit as st
import random
from utils.database import submit_to_database

st.set_page_config(
    layout='centered',
    page_title='Floods|Ready.gov',
    page_icon='✅'
)

# Apply custom CSS for aggressive styling
def set_background():
    st.markdown(
        """
        <style>
        .stApp {
            background-color: #FFFFFF; /* White background */
        }
        .big-title {
            color: #4C9900; /* Floodready.gov for the title */
            font-size: 50px;
            font-weight: bold;
        }
        .flood-title {
            color: #000000; /* Black font for the title */
            font-size: 36px;
            font-weight: bold;
        }
        .flood-warning {
            background-color: white; 
            color: black; /* Black font for the warning */
            padding: 20px; 
            font-size: 18px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
def main():
    set_background()

    # Show information with a styled title
    st.markdown('<div class="big-title">Get Ready for Floods</div>', unsafe_allow_html=True)

    # Display the title
    st.markdown('<div class="flood-title">Staying Safe During a Flood</div>', unsafe_allow_html=True)

    # Display flood warning image
    st.image('floodreadygov_floodwarn.png', caption='Staying Safe During a Flood')

    # Display flood warning information with aggressive styling
    st.markdown(
        """
        <div class="flood-warning">
        ✅ Evacuate immediately if told to evacuate. Never drive around barricades. Local responders use them to safely direct traffic out of flooded areas.<br><br>
        ✅ Contact your healthcare provider if you are sick and need medical attention. Wait for further care instructions and shelter in place if possible. If you are experiencing a medical emergency, call 9-1-1.<br><br>
        ✅ Listen to EAS, NOAA Weather Radio, or local alerting systems for current emergency information and instructions regarding flooding.<br><br>
        ✅ Do not walk, swim, or drive through flood waters. <strong>Turn Around. Don’t Drown!</strong><br><br>
        ✅ Stay off bridges over fast-moving water. Fast-moving water can wash bridges away without warning.<br><br>
        ✅ Stay inside your car if it is trapped in rapidly moving water. Get on the roof if water is rising inside the car.<br><br>
        ✅ Get to the highest level if trapped in a building. Only get on the roof if necessary and once there, signal for help. Do not climb into a closed attic to avoid getting trapped by rising floodwater.<br><br>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Add comment box
    comment = st.text_area("Leave your comment here:", "")
    
    if st.button("Submit Comment"):
        if comment:
            # Generate a verification code
            verification_code = random.randint(1000, 9999)
            st.success(f"Your comment has been submitted! Verification Code: {verification_code}")
            
            # Save comment to the database (adjust as needed)
            submit_to_database(comment)
        else:
            st.warning("Please enter a comment before submitting.")

if __name__ == '__main__':
    main()
