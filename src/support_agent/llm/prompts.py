"""Centralized prompt templates.

Every agent prompt lives here so prompt text is defined once. Output formatting is
handled by `with_structured_output`, so prompts describe the task, not the JSON shape.
"""

from langchain_core.prompts import ChatPromptTemplate

# Shared category list for classification, used by the intent and refiner prompts.
INTENT_CATEGORIES = (
    "- authentication: login, passwords, password reset, MFA/2FA, account lockout\n"
    "- sso: single sign-on, SAML, OIDC, identity providers (Okta, Azure AD), SCIM\n"
    "- billing: plans, pricing, invoices, payments, refunds, proration\n"
    "- user_management: roles, permissions, inviting/removing/deactivating members\n"
    "- api: API keys, endpoints, rate limits, webhooks, programmatic access\n"
    "- integrations: connecting third-party apps (Slack, Jira, Drive, Zapier)\n"
    "- security: encryption, compliance (SOC 2, GDPR), data residency, audit logs\n"
    "- troubleshooting: a general error or 'not working' with no clearer category\n"
    "- product_features: what the product does or how a feature works\n"
    "- enterprise_support: SLAs, priority support, dedicated CSM, support tiers\n"
    "- other: none of the above\n\n"
    "Prefer the specific topic over a broad one: an SSO/SAML/Okta question is 'sso', "
    "not 'authentication'; an API rate-limit question is 'api', not 'troubleshooting'."
)

# Shared confidence calibration for classification, used by intent and refiner.
INTENT_CONFIDENCE_GUIDANCE = (
    "Set confidence to reflect genuine certainty, not a default value: use 0.9-1.0 only "
    "when the email clearly and unambiguously fits one category; 0.6-0.85 when it is "
    "plausible but vague or could also fit another category; below 0.6 when the email is "
    "unclear or spans multiple topics."
)

INTENT_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an intent classifier for a customer support team. Choose the single "
            "MOST SPECIFIC category for the email from this list:\n" + INTENT_CATEGORIES + "\n\n"
            + INTENT_CONFIDENCE_GUIDANCE + "\n"
            "Also produce a one-sentence summary, the key entities, and 2-4 focused search "
            "queries to retrieve the documents needed to answer it. Base everything only on "
            "the email.",
        ),
        ("human", "Customer email:\n{email}"),
    ]
)

# ---------------------------------------------------------------------------------------------

RETRIEVAL_VALIDATOR_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You judge whether the retrieved documents are sufficient to fully answer the "
            "customer email. Consider how well the documents cover what the email asks and "
            "each search query.\n"
            "Score retrieval_score from 0 to 1 using this scale:\n"
            "- 0.8-1.0: documents directly and completely cover what is needed\n"
            "- 0.5-0.7: partial coverage; some needed facts are missing\n"
            "- 0.0-0.4: largely irrelevant or off-topic\n"
            "Set needs_retry to true only when the score is low AND a different search "
            "(rephrased queries or a corrected topic) could plausibly retrieve better "
            "documents. If the documents are already adequate, set needs_retry to false. "
            "Give a brief reason explaining the gap, to guide the next search.",
        ),
        (
            "human",
            "Customer email:\n{email}\n\n"
            "Search queries used:\n{queries}\n\n"
            "Retrieved documents:\n{documents}",
        ),
    ]
)

# ---------------------------------------------------------------------------------------------

REFINE_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "A first attempt to retrieve support documents for this email was judged "
            "insufficient. Re-examine the email from scratch. The previous intent may have "
            "been WRONG: if so, correct it. Choose the single MOST SPECIFIC category from "
            "this list:\n" + INTENT_CATEGORIES + "\n\n"
            "Then produce new search queries that are meaningfully different from the "
            "previous ones and more likely to retrieve the right documents. "
            + INTENT_CONFIDENCE_GUIDANCE + " Also produce a one-sentence summary and key "
            "entities. Base everything only on the email.",
        ),
        (
            "human",
            "Customer email:\n{email}\n\n"
            "Previous intent: {intent}\n"
            "Previous queries: {queries}\n"
            "Why retrieval was insufficient: {reason}",
        ),
    ]
)

# ---------------------------------------------------------------------------------------------

PLANNER_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You plan a support reply. Using the customer email and the retrieved "
            "documents, define the goal of the reply, the points it must include, and "
            "the specific key facts to use. Use only facts present in the documents. "
            "Do not write the reply itself.",
        ),
        (
            "human",
            "Customer email:\n{email}\n\n"
            "Intent: {intent}\n"
            "Summary: {summary}\n\n"
            "Retrieved documents:\n{documents}",
        ),
    ]
)

# ---------------------------------------------------------------------------------------------

WRITER_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You write the customer-facing support reply. Follow the plan and use only "
            "facts supported by the documents; make no claims the documents do not "
            "support. If revision feedback is provided, address every point.\n\n"
            "Format draft_response as a complete support email with this exact structure:\n\n"
            "1. Greeting line. Use the customer's first name if it appears in their "
            "signature ('Hi <Name>,'); otherwise use 'Hello,'.\n"
            "2. Acknowledgement (one short sentence) of what they asked or are "
            "experiencing — shows you read their email.\n"
            "3. Body that directly answers the request, grounded in the documents. "
            "When the answer involves a procedure, present it as a numbered list "
            "(1., 2., 3., ...). Keep paragraphs short.\n"
            "4. Closing line offering further help, e.g. 'Let us know if you have any "
            "other questions.'\n"
            "5. Sign-off on two lines:\n"
            "       Best regards,\n(next line)"
            "       Nimbus Support\n"
            "Use blank lines between sections for readability. Write draft_response as "
            "clean text the customer can read and send as-is. Do NOT put citations, "
            "source names, or reference markers inside draft_response. List the document "
            "sources you relied on separately in the citations field.",
        ),
        (
            "human",
            "Plan:\n{plan}\n\n"
            "Retrieved documents:\n{documents}\n\n"
            "Revision feedback (if any):\n{feedback}",
        ),
    ]
)

# ---------------------------------------------------------------------------------------------

REVIEWER_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You review a draft support reply before it reaches the customer. Evaluate "
            "grounding (every claim supported by the documents), completeness (it "
            "addresses the email), consistency, and helpfulness. Approve only if it "
            "meets all four. When not approved, give specific, actionable feedback.\n"
            "Set confidence to how certain you are of your verdict, not a default value: "
            "use 0.9-1.0 only when the draft is clearly fully grounded and complete (to "
            "approve) or clearly deficient (to reject); 0.6-0.85 when it is borderline.",
        ),
        (
            "human",
            "Customer email:\n{email}\n\n"
            "Plan:\n{plan}\n\n"
            "Draft reply:\n{draft}\n\n"
            "Retrieved documents:\n{documents}",
        ),
    ]
)
