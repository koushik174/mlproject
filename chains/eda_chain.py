from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from typing import Dict, Any, Optional
from utils.llm_utils import LLMUtils
import json

class EDAChain:
    def __init__(self, llm_utils: LLMUtils):
        """Initialize EDA Chain"""
        self.llm = llm_utils
        self.setup_chains()

    def setup_chains(self):
        """Setup different chains for various analysis tasks"""
        # SQL Generation Chain
        self.sql_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                input_variables=["question", "schema"],
                template="""
                Given the following SQL schema:
                {schema}
                
                Generate a SQL query to answer this question:
                {question}
                
                The query should be optimized and include proper joins if needed.
                """
            )
        )

        # Visualization Chain
        self.viz_chain = LLMChain(
            llm=self.llm,
            prompt=PromptTemplate(
                input_variables=["data_description", "question"],
                template="""
                Based on this data:
                {data_description}
                
                What's the best visualization to answer:
                {question}
                
                Return a JSON with:
                {
                    "viz_type": "type of visualization",
                    "parameters": {"param1": "value1", ...}
                }
                """
            )
        )

    def process_query(self, query: str, db_manager) -> Dict[str, Any]:
        """Process natural language query"""
        try:
            # Analyze query
            analysis = self.llm.analyze_maritime_query(query)
            
            # Generate SQL
            sql_query = self.generate_sql_query(query, db_manager)
            
            # Execute query
            data = db_manager.execute_query(sql_query)
            
            # Determine visualization
            viz_params = self.recommend_visualization(data, query)
            
            # Generate response
            response = self.generate_response(data, analysis, viz_params)
            
            return response
            
        except Exception as e:
            return {
                "text": f"I encountered an error: {str(e)}",
                "error": True
            }

    def generate_sql_query(self, question: str, db_manager) -> str:
        """Generate SQL query from natural language"""
        schema = self._get_schema_description(db_manager)
        response = self.sql_chain.run(question=question, schema=schema)
        return self._clean_sql_query(response)

    def recommend_visualization(self, data, question) -> Dict[str, Any]:
        """Recommend visualization type"""
        data_description = data.describe().to_dict()
        response = self.viz_chain.run(
            data_description=json.dumps(data_description),
            question=question
        )
        return json.loads(response)

    def generate_response(self, data, analysis, viz_params) -> Dict[str, Any]:
        """Generate final response"""
        return {
            "text": self._generate_natural_response(data, analysis),
            "data": data,
            "viz_type": viz_params["viz_type"],
            "viz_params": viz_params["parameters"],
            "needs_visualization": True
        }

    @staticmethod
    def _clean_sql_query(query: str) -> str:
        """Clean and validate SQL query"""
        # Add query cleaning logic
        return query.strip()

    @staticmethod
    def _get_schema_description(db_manager) -> str:
        """Get database schema description"""
        # Add schema extraction logic
        return """
        Tables:
        - vessels (mmsi, vessel_name, vessel_type, length, width, flag)
        - ais_positions (mmsi, timestamp, latitude, longitude, speed, course)
        """
