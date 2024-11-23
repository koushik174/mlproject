class EDAPrompts:
    @staticmethod
    def get_sql_generation_prompt() -> str:
        return """
        Given the following maritime database schema:
        {schema}
        
        Generate a SQL query to answer this question:
        {question}
        
        Consider:
        1. Use appropriate JOINs for related tables
        2. Apply relevant filters
        3. Include proper aggregations if needed
        4. Order results meaningfully
        5. Limit results if returning large datasets
        
        Return only the SQL query.
        """

    @staticmethod
    def get_visualization_prompt() -> str:
        return """
        Based on this maritime data:
        {data_description}
        
        Recommend the best visualization to answer:
        {question}
        
        Consider:
        1. Data types involved
        2. Spatial components (coordinates)
        3. Time series aspects
        4. Number of variables
        5. Type of analysis needed
        
        Return a JSON with visualization specifications.
        """

    @staticmethod
    def get_analysis_prompt() -> str:
        return """
        Analyze this maritime data:
        {data}
        
        And provide:
        1. Key patterns or trends
        2. Notable anomalies
        3. Operational insights
        4. Safety considerations
        5. Recommendations
        
        Format the response in clear, concise points.
        """

    @staticmethod
    def get_query_analysis_prompt() -> str:
        return """
        Analyze this maritime query:
        {query}
        
        Extract:
        1. Query intent (tracking, analysis, safety, etc.)
        2. Time range mentioned
        3. Geographic scope
        4. Vessel types involved
        5. Required metrics
        
        Return structured analysis in JSON format.
        """
