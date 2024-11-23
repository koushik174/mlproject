
import streamlit as st
from database.db_manager import DatabaseManager
from utils.visualization import VisualizationManager
from utils.llm_utils import load_llm_model
from chains.eda_chain import EDAChain
import yaml

# Load configuration
with open('config/config.yaml', 'r') as file:
    config = yaml.safe_load(file)

def initialize_components():
    
    db_manager = DatabaseManager(config['database']['connection_string'])
    viz_manager = VisualizationManager()
    llm_model = load_llm_model(config['model'])
    eda_chain = EDAChain(llm_model)
    return db_manager, viz_manager, eda_chain

def main():
    st.set_page_config(
        page_title="Maritime Data Analysis Chatbot",
        page_icon="🚢",
        layout="wide"
    )

    st.title("🚢 Maritime Data Analysis Assistant")
    st.subheader("Ask questions about your AIS data")

    # Initialize components
    db_manager, viz_manager, eda_chain = initialize_components()

    # Sidebar for data loading and settings
    with st.sidebar:
        st.header("Settings")
        if st.button("Load Sample Data"):
            with st.spinner("Loading sample data..."):
                db_manager.load_sample_data()
                st.success("Sample data loaded!")

    # Chat interface
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            if "visualization" in message:
                st.plotly_chart(message["visualization"])

    # Chat input
    if prompt := st.chat_input("Ask about your maritime data..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing..."):
                # Process query through EDA chain
                response = eda_chain.process_query(prompt, db_manager)
                
                # Create visualization if needed
                if response.get("needs_visualization"):
                    fig = viz_manager.create_visualization(
                        response["data"],
                        response["viz_type"]
                    )
                    response["visualization"] = fig

                # Display response
                st.write(response["text"])
                if "visualization" in response:
                    st.plotly_chart(response["visualization"])

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response["text"],
                    "visualization": response.get("visualization")
                })

if __name__ == "__main__":
    main()
