
import streamlit as st
import os
import pandas as pd
from storage import upload_receipt,download_receipt
from database import (
    get_user_id,
    get_user_club_role,
    add_programme,
    get_programmes,
    add_programme_participant,
    get_programme_participants,
    update_participant_payment_status,
    update_participant_payment_proof,
    update_programme,
    update_participant_details,
    delete_participant_payment_proof,
    delete_programme
)

from navigation import (
    show_finance_sidebar,
    show_custom_style
)

st.set_page_config(
    page_title="Programme Deposit",
    page_icon="💳",
    layout="wide"
)

show_custom_style()
show_finance_sidebar()
#login and club selection check
if not st.session_state.get("logged_in", False):
    st.warning("Please log in first.")
    st.switch_page("pages/0_Account.py")
    st.stop()

club_id = st.session_state.get("selected_club_id")

if club_id is None:
    st.warning("Please select a club first.")
    if st.button("Select Club"):
        st.switch_page("pages/5_Club_Navigation.py")
    st.stop()

user_id = get_user_id(st.session_state.username)
role = get_user_club_role(user_id, club_id)

st.title("💳 Programme Deposit Management")

st.write("Create programmes and manage participant deposits.")
#create new programme
st.divider()

if role == "Treasurer":

    st.subheader("➕ Create New Programme")

    with st.form("create_programme_form"):

        programme_name = st.text_input(
            "Programme Name",
            placeholder="e.g. Engineering Workshop"
        )

        deposit_amount = st.number_input(
            "Deposit Amount (RM)",
            min_value=0.0,
            value=0.0,
            step=5.0
        )
        participant_limit = st.number_input(
            "Maximum Number of Participants",
            min_value=0,
            value=0,
            step=5
)
        submitted = st.form_submit_button(
            "Create Programme",
            use_container_width=True
        )

        if submitted:

            if not programme_name.strip():
                st.warning("Please enter a programme name.")

            elif participant_limit <= 0:
                st.warning("Please enter a valid participant limit.")
            elif deposit_amount <= 0:
                st.warning("Please enter a valid deposit amount.")

            else:
                success = add_programme(
                    club_id,
                    programme_name.strip(),
                    deposit_amount,
                    int(participant_limit)
                )

                if success:
                    st.session_state.programme_created = True
                    st.rerun()
                else:
                    st.error("Unable to create programme.")
if st.session_state.get("programme_created", False):
    st.success("Programme created successfully!")
    st.session_state.programme_created = False
#existing programmes
st.subheader("📋 Existing Programmes")

programmes = get_programmes(club_id)

if programmes:
    for programme in programmes:

        programme_id = programme[0]
        programme_name = programme[1]

        with st.container(border=True):

            st.write(f"**{programme_name}**")
            st.write(f"Deposit: RM {programme[2]:.2f}")

            # Show participant limit and current registration
            participant_limit = programme[4]
            participants = get_programme_participants(programme_id)

            st.metric(
                "Participants",
                f"{len(participants)}/{participant_limit}"
            )

            if len(participants) >= participant_limit:
                st.error("Registration Full")
            else:
                st.success("Registration Open")

            st.write(
                f"**Expected Total Deposit:** "
                f"RM {len(participants) * programme[2]:.2f}"
            )

            # Delete programme
            if role == "Treasurer":
                if st.button(
                    f"🗑️ Delete {programme_name}",
                    key=f"delete_programme_{programme_id}"
                ):
                    success = delete_programme(programme_id)

                    if success:
                        st.session_state.programme_deleted = True
                        st.rerun()
                    else:
                        st.error("Unable to delete programme.")

else:
    st.info("No programmes created yet.")
if st.session_state.get("programme_deleted", False):
    st.success("Programme deleted successfully!")
    st.session_state.programme_deleted = False
               



# PARTICIPANT REGISTRATION
st.divider()

st.subheader("👥 Participant Registration")

programmes = get_programmes(club_id)

if programmes:

    selected_programme = st.selectbox(
        "Select Programme",
        options=programmes,
        format_func=lambda p: p[1]
    )

    # 1. EDIT PROGRAMME
    if role == "Treasurer":

        st.subheader("✏️ Edit Programme")

        with st.form("edit_programme_form"):

            new_deposit = st.number_input(
                "Deposit Amount (RM)",
                min_value=0.01,
                value=float(selected_programme[2]),
                step=5.0
            )

            new_limit = st.number_input(
                "Participant Limit",
                min_value=1,
                value=int(selected_programme[4]),
                step=1
            )

            submitted = st.form_submit_button("Update Programme")

            if submitted:

                current_count = len(
                    get_programme_participants(selected_programme[0])
                )

                if new_limit < current_count:
                    st.error(
                        "Participant limit cannot be lower than current registrations."
                    )

                else:
                    updated = update_programme(
                        selected_programme[0],
                        new_deposit,
                        new_limit
                    )

                    if updated:
                        st.success("Programme updated successfully!")
                        st.rerun()
                    else:
                        st.error("Unable to update programme.")

    # 2. REGISTER PARTICIPANT
    if role == "Treasurer":

        st.subheader("➕ Register Participant")

        with st.form("participant_registration"):

            participant_name = st.text_input("Participant Name")
            participant_email = st.text_input("Participant Email")

            submitted = st.form_submit_button("Register Participant")

            if submitted:

                if not participant_name.strip():
                    st.warning("Please enter the participant's name.")

                elif not participant_email.strip():
                    st.warning("Please enter the participant's email.")

                else:
                    current_participants = get_programme_participants(
                        selected_programme[0]
                    )

                    participant_limit = selected_programme[4]

                    if len(current_participants) >= participant_limit:
                        st.error(
                            "This programme has reached its participant limit."
                        )

                    else:
                        existing_emails = [
                            p[2].lower()
                            for p in current_participants
                            if p[2]
                        ]

                        if participant_email.strip().lower() in existing_emails:
                            st.error("This email is already registered.")

                        else:
                            add_programme_participant(
                                selected_programme[0],
                                participant_name.strip(),
                                participant_email.strip()
                            )

                            st.success("Participant registered successfully!")

    else:
        st.info("Only the Treasurer can register participants.")

    # 3. DISPLAY PARTICIPANTS
    st.divider()
    st.subheader("👥 Registered Participants")

    participants = get_programme_participants(selected_programme[0])

    if participants:

        for participant in participants:

            st.write(f"**Name:** {participant[1]}")
            st.write(f"**Email:** {participant[2] or 'Not provided'}")

            # 4. EDIT PARTICIPANT DETAILS
            if role == "Treasurer":

                with st.expander("✏️ Edit Participant Details"):

                    with st.form(f"edit_participant_{participant[0]}"):

                        new_name = st.text_input(
                            "Participant Name",
                            value=participant[1]
                        )

                        new_email = st.text_input(
                            "Participant Email",
                            value=participant[2] or ""
                        )

                        submitted = st.form_submit_button("Save Changes")

                        if submitted:

                            if not new_name.strip() or not new_email.strip():
                                st.error("Please fill in all fields.")

                            else:
                                updated = update_participant_details(
                                    participant[0],
                                    selected_programme[0],
                                    new_name.strip(),
                                    new_email.strip()
                                )

                                if updated:
                                    st.success("Participant details updated!")
                                    st.rerun()

                                else:
                                    st.error(
                                        "Unable to update participant details."
                                    )

            st.divider()

    else:
        st.info("No participants registered yet.")

else:
    st.info("Create a programme before registering participants.")

# PARTICIPANT PAYMENT RECORDS

st.divider()

st.subheader("📋 Participant Payment Records")

if programmes:

    participants = get_programme_participants(
        selected_programme[0]
    )

    # PAYMENT SUMMARY

    total_participants = len(participants)
    if total_participants >= selected_programme[4]:
        st.warning("⚠️ This programme has reached its participant limit.")
    elif total_participants >= selected_programme[4] * 0.8:
        st.info("⚠️ This programme is almost full!")

    paid_count = sum(
        1 for p in participants if p[3] == "Paid"
    )

    unpaid_count = total_participants - paid_count

    total_collected = paid_count * selected_programme[2]
    total_outstanding = unpaid_count * selected_programme[2]
    total_expected = total_participants * selected_programme[2]

    if total_expected > 0:
        collection_rate = (total_collected / total_expected) * 100
    else:
        collection_rate = 0

    st.metric(
        "Deposit Collection Rate",
        f"{collection_rate:.1f}%"
    )

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Participants", total_participants)
    col2.metric("Paid", paid_count)
    col3.metric("Unpaid", unpaid_count)

    col4, col5 = st.columns(2)

    col4.metric(
            "Total Deposit Collected",
            f"RM {total_collected:.2f}"
        )

    col5.metric(
            "Outstanding Deposit",
            f"RM {total_outstanding:.2f}"
        )
    # PAYMENT COMPLETION PROGRESS

    if total_participants > 0:

        payment_progress = paid_count / total_participants

    else:

        payment_progress = 0

    st.write("**Payment Completion Progress**")

    st.progress(payment_progress)

    st.caption(
        f"{paid_count} out of {total_participants} participants have paid "
        f"({payment_progress * 100:.1f}%)"
    )

    st.divider()
    # EXPORT PARTICIPANT RECORDS (TREASURER ONLY)

    if participants and role == "Treasurer":

        export_data = []

        for p in participants:
            export_data.append({
                "Participant Name": p[1],
                "Email": p[2],
                "Payment Status": p[3],
                "Registered At": p[5]
            })

        df = pd.DataFrame(export_data)

        df["Registered At"] = (
            pd.to_datetime(
                df["Registered At"],
                errors="coerce",
                utc=True,
                format="mixed"
            )
            .dt.tz_convert("Asia/Kuala_Lumpur")
            .dt.strftime("%d/%m/%Y %H:%M")
        )
        csv_data = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="📥 Export Participant Records",
            data=csv_data,
            file_name="participant_payment_records.csv",
            mime="text/csv"
        )
    # INDIVIDUAL PARTICIPANT RECORDS

    if participants:

        search_name = st.text_input(
            "🔍 Search Participant",
            placeholder="Enter participant name or email"
        )
        payment_filter = st.selectbox(
            "Filter Payment Status",
            ["All", "Paid", "Unpaid"]
            )

        filtered_participants = [
            p for p in participants
            if (
                search_name.lower() in p[1].lower()
                or search_name.lower() in (p[2] or "").lower()
            )
            and (
                payment_filter == "All"
                or p[3] == payment_filter
            )
        ]
        for participant in filtered_participants:

            participant_id = participant[0]
            participant_name = participant[1]
            participant_email = participant[2]
            payment_status = participant[3]
            payment_proof = participant[4]
            registered_at = participant[5]

            with st.container(border=True):

                col1, col2 = st.columns([3, 1])

                with col1:

                    st.write(f"**{participant_name}**")
                    st.caption(participant_email)
                    st.caption(f"Registered: {registered_at}")

                    
                    # UPLOAD RECEIPT

                    if role == "Treasurer":

                        uploaded_file = st.file_uploader(
                            "Upload Payment Receipt",
                            type=["png", "jpg", "jpeg", "pdf"],
                            key=f"payment_proof_{participant_id}"
                        )

                        if uploaded_file is not None and payment_proof is None:

                            try:
                                file_path = upload_receipt(
                                    uploaded_file,
                                    selected_programme[0]
                                )

                                updated = update_participant_payment_proof(
                                    participant_id,
                                    selected_programme[0],
                                    file_path
                                )

                                if updated:
                                    st.success("Payment receipt uploaded!")
                                    st.rerun()
                                else:
                                    st.error("Unable to save payment receipt path.")

                            except Exception as e:
                                st.error(f"Receipt upload failed: {e}")


                    # DISPLAY RECEIPT

                    if payment_proof:

                        st.write("**Uploaded Payment Proof:**")

                        try:
                            receipt_data = download_receipt(payment_proof)

                            file_extension = payment_proof.split(".")[-1].lower()

                            if file_extension in ["png", "jpg", "jpeg"]:

                                st.image(receipt_data, width=250)

                                mime_type = (
                                    "image/jpeg" if file_extension in ["jpg", "jpeg"]
                                    else "image/png"
                                )

                            elif file_extension == "pdf":

                                st.write("PDF receipt uploaded.")
                                mime_type = "application/pdf"

                            else:
                                mime_type = "application/octet-stream"

                            st.download_button(
                                label="📥 Download Receipt",
                                data=receipt_data,
                                file_name=os.path.basename(payment_proof),
                                mime=mime_type,
                                key=f"download_receipt_{participant_id}"
                            )

                        except Exception as e:
                            st.warning(f"Unable to retrieve payment receipt: {e}")
                        if role == "Treasurer":

                            if st.button(
                                "Delete Receipt",
                                key=f"delete_receipt_{participant_id}"
                            ):

                                deleted = delete_participant_payment_proof(
                                    participant_id,
                                    selected_programme[0]
                                )

                                if deleted:
                                    st.success("Receipt removed successfully!")
                                    st.rerun()
                                else:
                                    st.error("Unable to remove receipt.")

                    else:

                        st.info("No payment receipt uploaded yet.")

                with col2:

                    if payment_status == "Paid":

                        st.success("Paid")

                        if role == "Treasurer":

                            if st.button(
                                "Undo Payment",
                                key=f"undo_payment_{participant_id}"
                            ):

                                updated = update_participant_payment_status(
                                    participant_id,
                                    selected_programme[0],
                                    "Unpaid"
                                )

                                if updated:
                                    st.success("Payment changed to Unpaid.")
                                    st.rerun()
                                else:
                                    st.error("Unable to update payment status.")

                    else:

                        st.warning("Unpaid")

                        if role == "Treasurer":

                            if st.button(
                                "Confirm Payment",
                                key=f"confirm_payment_{participant_id}"
                            ):

                                if not payment_proof:
                                    st.warning("Please upload the receipt first.")

                                else:
                                    updated = update_participant_payment_status(
                                        participant_id,
                                        selected_programme[0],
                                        "Paid"
                                    )

                                    if updated:
                                        st.success("Payment confirmed!")
                                        st.rerun()
                                    else:
                                        st.error("Unable to update payment status.")
    else:

        st.info("No participants registered for this programme.")

else:

    st.info("Create a programme first.")



    