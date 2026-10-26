
import streamlit as st

from gmail_agent import (
    authenticate_gmail,
    get_emails,
    create_reply_draft
)

from ai_agents import (
    analyzer_agent,
    reply_agent,
    quality_agent
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(

    page_title="Gmail AI Agent",

    page_icon="📧",

    layout="wide"
)


# ============================================================
# TITLE
# ============================================================

st.title(
    "📧 Gmail AI Automation Agent"
)

st.write(
    "Read → Analyze → Generate Reply → Quality Check → Draft"
)


# ============================================================
# SESSION STATE
# ============================================================

if "gmail_service" not in st.session_state:

    st.session_state.gmail_service = None


if "emails" not in st.session_state:

    st.session_state.emails = []


if "selected_email" not in st.session_state:

    st.session_state.selected_email = None


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header(
        "⚙️ Gmail"
    )


    # --------------------------------------------------------
    # CONNECT
    # --------------------------------------------------------

    if st.button(
        "🔐 Connect Gmail",
        use_container_width=True
    ):

        try:

            service = authenticate_gmail()

            st.session_state.gmail_service = service

            st.success(
                "Gmail connected!"
            )

        except Exception as error:

            st.error(
                f"Gmail connection failed: {error}"
            )


    st.divider()


    # --------------------------------------------------------
    # LOAD EMAILS
    # --------------------------------------------------------

    if st.button(
        "📥 Load Emails",
        use_container_width=True
    ):

        if not st.session_state.gmail_service:

            st.warning(
                "Connect Gmail first."
            )

        else:

            try:

                emails = get_emails(

                    st.session_state.gmail_service,

                    max_results=10

                )

                st.session_state.emails = emails

                st.success(
                    f"Loaded {len(emails)} emails."
                )

            except Exception as error:

                st.error(
                    f"Could not load emails: {error}"
                )


# ============================================================
# CHECK CONNECTION
# ============================================================

if not st.session_state.gmail_service:

    st.info(
        "👈 Connect your Gmail account from the sidebar."
    )

    st.stop()


# ============================================================
# EMAIL LIST
# ============================================================

st.header(
    "📬 Inbox"
)


emails = st.session_state.emails


if not emails:

    st.info(
        "Click 'Load Emails' to retrieve your inbox."
    )

    st.stop()


# ============================================================
# DISPLAY EMAILS
# ============================================================

for index, email in enumerate(
    emails
):

    with st.container(
        border=True
    ):

        col1, col2 = st.columns(
            [5, 1]
        )


        with col1:

            st.subheader(
                email["subject"]
                or "(No Subject)"
            )

            st.caption(
                f"From: {email['sender']}"
            )

            st.write(
                email["body"][:300]
                + "..."
            )


        with col2:

            if st.button(
                "🤖 Process",
                key=f"process_{index}"
            ):

                st.session_state.selected_email = (
                    email
                )


# ============================================================
# SELECTED EMAIL
# ============================================================

email = st.session_state.selected_email


if email:

    st.divider()

    st.header(
        "🤖 AI Email Agent"
    )


    # ========================================================
    # ORIGINAL EMAIL
    # ========================================================

    with st.expander(
        "📧 Original Email",
        expanded=True
    ):

        st.write(
            f"**From:** {email['sender']}"
        )

        st.write(
            f"**Subject:** {email['subject']}"
        )

        st.text_area(
            "Email",
            email["body"],
            height=250,
            disabled=True
        )


    # ========================================================
    # RUN AGENTS
    # ========================================================

    if st.button(
        "🚀 Run AI Agents",
        type="primary",
        use_container_width=True
    ):

        # ----------------------------------------------------
        # ANALYZER
        # ----------------------------------------------------

        with st.status(
            "Running AI agents...",
            expanded=True
        ):

            st.write(
                "🔍 Analyzer Agent..."
            )


            analysis = analyzer_agent(

                email["sender"],

                email["subject"],

                email["body"]

            )


            st.write(
                "✅ Email analyzed."
            )


            # ------------------------------------------------
            # REPLY AGENT
            # ------------------------------------------------

            st.write(
                "✍️ Reply Agent..."
            )


            reply = reply_agent(

                email["sender"],

                email["subject"],

                email["body"],

                analysis

            )


            st.write(
                "✅ Reply generated."
            )


            # ------------------------------------------------
            # QUALITY AGENT
            # ------------------------------------------------

            st.write(
                "🛡️ Quality Agent..."
            )


            quality = quality_agent(

                email["body"],

                reply

            )


            st.write(
                "✅ Quality check completed."
            )


        # ====================================================
        # RESULTS
        # ====================================================

        st.subheader(
            "🔍 Email Analysis"
        )


        col1, col2, col3 = st.columns(
            3
        )


        with col1:

            st.metric(
                "Category",
                analysis["category"]
            )


        with col2:

            st.metric(
                "Priority",
                analysis["priority"]
            )


        with col3:

            st.metric(
                "Reply Required",
                str(
                    analysis["requires_reply"]
                )
            )


        st.write(
            "**Summary:**"
        )

        st.write(
            analysis["summary"]
        )


        st.write(
            "**Key Points:**"
        )

        for point in analysis["key_points"]:

            st.write(
                f"• {point}"
            )


        # ====================================================
        # GENERATED REPLY
        # ====================================================

        st.subheader(
            "✍️ Generated Reply"
        )


        edited_reply = st.text_area(

            "Review and edit before creating draft",

            value=reply,

            height=250
        )


        # ====================================================
        # QUALITY RESULT
        # ====================================================

        st.subheader(
            "🛡️ Quality Check"
        )


        if quality["approved"]:

            st.success(
                f"Approved — Score: "
                f"{quality['score']}/10"
            )

        else:

            st.warning(
                f"Needs review — Score: "
                f"{quality['score']}/10"
            )


        st.write(
            quality["reason"]
        )


        # ====================================================
        # CREATE DRAFT
        # ====================================================

        if st.button(
            "📨 Create Gmail Draft",
            type="primary",
            use_container_width=True
        ):

            try:

                draft = create_reply_draft(

                    st.session_state.gmail_service,

                    email,

                    edited_reply

                )


                st.success(
                    "✅ Reply draft created in Gmail!"
                )


                st.info(
                    f"Draft ID: {draft['id']}"
                )


            except Exception as error:

                st.error(
                    f"Could not create draft: {error}"
                )
