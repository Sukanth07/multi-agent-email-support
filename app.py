"""Streamlit UI for the agentic customer support system.

UI only: it streams the workflow and renders the shared state. All logic lives in
the `support_agent` package.
"""

import streamlit as st

from support_agent.config import get_settings
from support_agent.models.state import WorkflowState
from support_agent.workflow.graph import stream_workflow

# Sample emails covering the full range of workflow behaviors:
#   - Easy:     first-pass success (good retrieval, approved on first draft)
#   - Moderate: triggers the retrieval retry loop or partial coverage
#   - Complex:  outside the knowledge base, likely escalated to human review
#   - Tricky:   vague / multi-topic, exercises the refiner
SAMPLE_EMAILS: dict[str, str] = {
    "Easy · Lost MFA / locked out": (
        "Hi support,\n\n"
        "I lost my phone over the weekend and the authenticator app with all my 2FA "
        "codes was on it. I never wrote down the recovery codes. Can someone please "
        "help me reset MFA on my account? I have a client meeting tomorrow and I "
        "really need to get back in.\n\n"
        "Thanks,\n"
        "Marcus"
    ),
    "Easy · SSO on the Pro plan": (
        "Hi team,\n\n"
        "We're currently on the Pro plan with around 40 active users. Our IT team "
        "just told us we need to enforce SSO via our Okta tenant. Is SSO available "
        "on Pro, or do we need to upgrade? If so, what plan should we move to, and "
        "what does the setup look like?\n\n"
        "Best,\n"
        "Priya Anand"
    ),
    "Easy · API rate limit on Business": (
        "Hi,\n\n"
        "We're integrating against your API and keep getting 429 errors. We're on "
        "the Business plan and the docs mention 300 requests per minute, but we seem "
        "to be hitting limits much earlier than that. Can you confirm the exact "
        "rate limit, and whether there are per-endpoint limits we should know about?\n\n"
        "Thanks,\n"
        "Sam"
    ),
    "Moderate · Cancel + data export": (
        "Hello,\n\n"
        "We're planning to wind down our subscription at the end of next month. "
        "Before we cancel, what's the best way to export everything we have — "
        "projects, documents, and our member list — so we keep an archive? We have "
        "almost two years of work in there and we'd hate to lose any of it.\n\n"
        "Best,\n"
        "Nora"
    ),
    "Moderate · Slow + sign-in issues": (
        "Hi,\n\n"
        "Half my team is reporting that the app is really slow today, and two "
        "people keep getting 'session expired' right after they enter their "
        "password. Everything was fine yesterday. Is there an outage going on, or "
        "is this something on our side?\n\n"
        "- Jen"
    ),
    "Complex · HIPAA / BAA (likely escalation)": (
        "Hi,\n\n"
        "We're a healthcare provider evaluating your platform for use with patient "
        "information. Could you confirm whether Nimbus is HIPAA-eligible, and "
        "whether you're willing to sign a Business Associate Agreement (BAA) for "
        "our deployment? We also need to understand whether PHI can be stored "
        "within your environment under your existing controls.\n\n"
        "Regards,\n"
        "Daniel Ortega\n"
        "Compliance Officer"
    ),
    "Complex · On-prem deployment (likely escalation)": (
        "Hello,\n\n"
        "Our security team restricts cloud-hosted SaaS for certain workloads. Do "
        "you offer an on-premise or self-hosted option of Nimbus? If not, would "
        "you be able to provision a dedicated, isolated environment for us with "
        "our own KMS keys?\n\n"
        "Thanks,\n"
        "Vikram"
    ),
    "Tricky · Vague multi-topic": (
        "Hey,\n\n"
        "A few things going on — sign-in has been weird lately, we're thinking "
        "about adding SSO eventually, and honestly I'm not 100% sure what our "
        "current plan covers. Could someone walk us through our setup and what "
        "we'd need to change to support the whole company?\n\n"
        "Cheers,\n"
        "Ryan"
    ),
}


def _load_sample() -> None:
    """Populate the email text area with the selected sample."""
    chosen = st.session_state.get("sample_choice")
    if chosen in SAMPLE_EMAILS:
        st.session_state["email_text"] = SAMPLE_EMAILS[chosen]

st.set_page_config(page_title="Agentic Support", layout="wide")
st.title("Agentic Customer Support")
st.caption(
    "Intent → Retrieval → Validation → Planner → Writer → Reviewer, "
    "orchestrated over shared state."
)


def _preflight() -> bool:
    """Check configuration before running; show clear guidance if not ready."""
    settings = get_settings()
    ready = True
    if settings.groq_api_key is None:
        st.error("GROQ_API_KEY is not set. Add it to your `.env` file.")
        ready = False
    if not settings.faiss_index_dir.exists():
        st.warning("Vector index not found. Run `python scripts/build_index.py` first.")
        ready = False
    return ready


def _render_trace(state: WorkflowState) -> None:
    for entry in state.trace:
        st.markdown(f"**`{entry.node}`** — {entry.detail}")


def _render_results(state: WorkflowState) -> None:
    if state.error:
        st.error(f"Workflow ended with an error: {state.error}")

    if state.needs_human_review:
        st.warning(
            "Escalated to human review — the draft was not approved after the maximum "
            "rewrites, so it was not sent. The draft is shown in the Writer tab."
        )

    st.subheader("Final response")
    if state.final_response:
        st.success(state.final_response)
    else:
        st.info("No final response produced.")

    tabs = st.tabs(
        ["State", "Retrieved docs", "Planner", "Writer", "Reviewer", "Trace"]
    )

    with tabs[0]:
        col1, col2, col3 = st.columns(3)
        col1.metric("Intent", state.intent.value if state.intent else "-")
        col1.metric("Confidence", f"{state.intent_confidence:.2f}")
        col2.metric("Retrieval score", f"{state.retrieval_score:.2f}")
        col2.metric("Retrieval attempts", state.retrieval_attempts)
        col3.metric("Rewrite attempts", state.rewrite_attempts)
        col3.metric("Docs retrieved", len(state.retrieved_docs))
        st.markdown(f"**Summary:** {state.summary or '-'}")
        st.markdown(f"**Entities:** {', '.join(state.entities) or '-'}")
        st.markdown(f"**Queries:** {', '.join(state.queries) or '-'}")

    with tabs[1]:
        if not state.retrieved_docs:
            st.info("No documents retrieved.")
        for doc in state.retrieved_docs:
            with st.expander(f"[{doc.score:.3f}] {doc.source} — {doc.title}"):
                st.write(doc.content)

    with tabs[2]:
        if state.plan:
            st.markdown(f"**Goal:** {state.plan.goal}")
            st.markdown("**Must include:**")
            st.write(state.plan.must_include or "-")
            st.markdown("**Key facts:**")
            st.write(state.plan.key_facts or "-")
        else:
            st.info("No plan produced.")

    with tabs[3]:
        st.markdown("**Draft response:**")
        st.write(state.draft_response or "-")
        st.markdown("**Citations:**")
        st.write(state.citations or "-")

    with tabs[4]:
        if state.review_result:
            st.markdown(f"**Approved:** {state.review_result.approved}")
            st.markdown(f"**Confidence:** {state.review_result.confidence:.2f}")
            st.markdown("**Feedback:**")
            st.write(state.review_result.feedback or "-")
        else:
            st.info("No review produced.")

    with tabs[5]:
        _render_trace(state)


if "email_text" not in st.session_state:
    first_label = next(iter(SAMPLE_EMAILS))
    st.session_state["email_text"] = SAMPLE_EMAILS[first_label]

st.selectbox(
    "Load a sample email",
    list(SAMPLE_EMAILS.keys()),
    key="sample_choice",
    on_change=_load_sample,
    help="Pick a scenario to load. You can still edit the email below before running.",
)

email = st.text_area("Customer email", key="email_text", height=200)
run = st.button("Run workflow", type="primary")

if run:
    if not email.strip():
        st.warning("Enter a customer email first.")
    elif _preflight():
        st.subheader("Workflow trace")
        live = st.empty()
        final_state: WorkflowState | None = None

        for state in stream_workflow(email):
            final_state = state
            with live.container():
                _render_trace(state)

        st.divider()
        if final_state is not None:
            _render_results(final_state)
