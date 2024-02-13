
class Search():
    engine = "search_engine_placeholder" # This is a placeholder for the search engine to be used
    history = []
    
    @staticmethod
    def search(query: str):
        """Search for a query using the search engine available.

        Args:
            query (str): input query to search for

        Returns:
            _type_: _description_
        """
        result = f"Placeholder results for {query} using {Search.engine}"
        Search.history.append(query)
        return query + " " + result
    
    @staticmethod
    def get_history():
        return Search.history
    
    @staticmethod
    def clear_history():
        Search.history = []
    
    @staticmethod
    def add_to_history(query: str, result):
        Search.history.append([query, result])
    
    @staticmethod
    def set_engine(engine: str):
        Search.engine = engine
        return f"Search engine set to {engine}"

