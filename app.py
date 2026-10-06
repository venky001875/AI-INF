import json
import pandas as pd
import streamlit as st

from main import influencer_search
from database import add_influencer, get_influencers


st.set_page_config(
    page_title="AI Influencer Research Agent",
    page_icon="🔎",
    layout="wide"
)




if "influencers" not in st.session_state:
    st.session_state.influencers = []

if "search_error" not in st.session_state:
    st.session_state.search_error = None




st.title("🔎 AI Influencer Research Agent")

st.write(
    "Find influencers and creators using web search "
    "and AI-powered information extraction."
)




st.subheader("Find Influencers")

col1, col2 = st.columns(2)

with col1:
    category = st.text_input(
        "Category",
        placeholder="Example: Robotics"
    )

with col2:
    location = st.text_input(
        "Location",
        placeholder="Example: India"
    )


col3, col4 = st.columns(2)

with col3:
    platform = st.selectbox(
        "Platform",
        ["All", "LinkedIn", "YouTube", "Instagram", "X", "Facebook"]
    )

with col4:
    number = st.number_input(
        "Number of influencers",
        min_value=1,
        max_value=10,
        value=3
    )




if st.button(
    "🔍 Find Influencers",
    type="primary",
    width="stretch"
):

    if not category.strip():
        st.warning("Please enter a category.")
        st.stop()

    if not location.strip():
        st.warning("Please enter a location.")
        st.stop()

    st.session_state.influencers = []
    st.session_state.search_error = None

    with st.spinner("🔎 Searching the web..."):

        try:

            result = influencer_search(
                category=category.strip(),
                location=location.strip(),
                platform=platform,
                number=int(number)
            )

            data = json.loads(result)

            if "error" in data:
                st.session_state.search_error = data.get(
                    "message",
                    "Extraction failed."
                )

            else:
                st.session_state.influencers = data.get(
                    "influencers",
                    []
                )

        except Exception as e:

            st.session_state.search_error = str(e)



if st.session_state.search_error:
    st.error(st.session_state.search_error)




influencers = st.session_state.influencers

if influencers:

    st.success(
        f"Research completed! Found {len(influencers)} influencer(s)."
    )

    st.subheader("Influencer Results")

    df = pd.DataFrame(influencers)

    columns = [
        "name",
        "platform",
        "username",
        "followers",
        "category",
        "location",
        "profile_url",
        "email",
        "description",
        "match_reason",
        "source_url"
    ]

    columns = [c for c in columns if c in df.columns]

    st.dataframe(
        df[columns],
        width="stretch",
        hide_index=True,
        column_config={
            "profile_url": st.column_config.LinkColumn(
                "Profile",
                display_text="🔗 Open Profile"
            ),
            "source_url": st.column_config.LinkColumn(
                "Source",
                display_text="📄 Open Source"
            )
        }
    )


    

    st.subheader("Influencer Details")

    for index, influencer in enumerate(influencers):

        name = influencer.get("name") or "Unknown"

        with st.expander(f"👤 {index + 1}. {name}"):

            def show_value(label, value, fallback="Not available"):
                st.write(f"**{label}:**", value if value not in (None, "") else fallback)

            col1, col2 = st.columns(2)

            with col1:
                show_value("Name", influencer.get("name"))
                show_value("Username / Handle", influencer.get("username"))
                show_value("Platform", influencer.get("platform"))
                show_value("Followers", influencer.get("followers"))
                show_value("Category", influencer.get("category"))
                show_value("Location", influencer.get("location"))

            with col2:
                profile_url = influencer.get("profile_url")
                if profile_url:
                    st.markdown(f"[🔗 Open Profile]({profile_url})")
                else:
                    st.write("**Profile Link:** Not available")

                show_value("Email", influencer.get("email"))

                source_url = influencer.get("source_url")
                if source_url:
                    st.markdown(f"[📄 Open Source]({source_url})")
                else:
                    st.write("**Source Link:** Not available")

            description = influencer.get("description")
            if description:
                st.write("**Description / Bio:**")
                st.write(description)
            else:
                st.write("**Description / Bio:** Not available")

            match_reason = influencer.get("match_reason")
            if match_reason:
                st.write("**Why this influencer matched:**")
                st.write(match_reason)
            else:
                st.write("**Why this influencer matched:** Not available")

            # =========================
            # Add to CRM
            # =========================

            if st.button(
                "➕ Add to CRM",
                key=f"crm_{index}",
                width="stretch"
            ):
                crm_data = {
                    key: value
                    for key, value in influencer.items()
                    if key in {"name", "platform", "username", "followers", "category", "location", "profile_url", "email", "description"}
                }
                add_influencer(crm_data)
                st.success(f"{name} added to CRM!")




st.divider()

st.subheader("📋 Influencer CRM")

rows = get_influencers()

if rows:

    columns = [
        "ID",
        "Name",
        "Platform",
        "Username",
        "Followers",
        "Category",
        "Location",
        "Profile URL",
        "Email",
        "Description"
    ]

    crm_df = pd.DataFrame(
        rows,
        columns=columns
    )

    st.dataframe(
        crm_df,
        width="stretch",
        hide_index=True,
        column_config={
            "Profile URL": st.column_config.LinkColumn(
                "Profile",
                display_text="🔗 Open"
            )
        }
    )

else:

    st.info("CRM is empty.")




if not influencers and not st.session_state.search_error:

    st.info(
        "Enter a category and location, then click "
        "Find Influencers."
    )