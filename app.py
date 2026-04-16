"""Streamlit bootstrap shell for toganoxie-split."""

import streamlit as st


def main() -> None:
    st.set_page_config(page_title="toganoxie-split", layout="wide")
    st.title("toganoxie-split")
    mode = st.sidebar.radio("Mode", ["Simple", "Advanced"], index=0)
    st.sidebar.caption("Bootstrap shell: adapters pending feature-branch implementation.")

    tabs = st.tabs(["Radar", "Models", "Point Forecast", "Alerts", "Stations"])
    for tab, name in zip(tabs, ["Radar", "Models", "Point Forecast", "Alerts", "Stations"]):
        with tab:
            st.subheader(name)
            st.info(
                f"{name} is scaffolded in bootstrap. Implement on feature branches with validated live sources only."
            )

    st.success(f"App startup OK. Current mode: {mode}")


if __name__ == "__main__":
    main()
