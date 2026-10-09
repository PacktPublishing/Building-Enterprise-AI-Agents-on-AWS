import os
import requests
import streamlit as st

api_url = os.environ["VACATION_PLANNER_API_URL"]

st.set_page_config(page_title="Vacation Planner")
st.title("Vacation Planner")
st.caption("Powered by Amazon Bedrock AgentCore Runtime")

destination = st.text_input("Destination", placeholder="Kyoto, Paris, Mumbai...")

if st.button("Plan vacation"):
    if not destination.strip():
        st.warning("Enter a destination first.")
    else:
        with st.spinner("Planning..."):
            response = requests.post(
                api_url,
                json={"prompt": destination.strip()},
                timeout=120,
            )
            response.raise_for_status()
            payload = response.json()
            body = payload.get("body", payload)
            if isinstance(body, str):
                body = __import__("json").loads(body)
            result = body.get("result", body)
            if isinstance(result, dict):
                result = result.get("result", result)
            st.markdown(str(result))
