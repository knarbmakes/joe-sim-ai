import os
from neo4j import GraphDatabase

class Neo4jClient:

    def __init__(self):
        uri = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
        user = os.getenv('NEO4J_USER', 'neo4j')
        password = os.getenv('NEO4J_PASSWORD', 'password')
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def execute_query(self, query, parameters=None):
        with self.driver.session() as session:
            result = session.execute_write(lambda tx: tx.run(query, parameters))
            return [record for record in result]

if __name__ == "__main__":
    client = Neo4jClient()
    result = client.execute_query("CREATE (a:Greeting {message: $message}) RETURN a", {'message': 'Hello, World!'})
    print(result)
    client.close()
