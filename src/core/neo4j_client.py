import os
from neo4j import GraphDatabase

class Neo4jClient:

    def __init__(self):
        uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
        user = os.getenv('NEO4J_USER', 'neo4j')
        password = os.getenv('NEO4J_PASSWORD', 'password')
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

        # Execute a simple query to make sure we are connected
        self.execute_query("MATCH (n) RETURN count(n)")

    def close(self):
        self.driver.close()

    def _transaction(self, tx, query, parameters=None):
        result = tx.run(query, parameters)
        return [record.data() for record in result]

    def execute_query(self, query, parameters=None):
        with self.driver.session() as session:
            result = session.execute_write(self._transaction, query, parameters)
            return result

