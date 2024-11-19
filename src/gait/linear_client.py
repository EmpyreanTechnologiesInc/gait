from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from gql.transport.exceptions import TransportQueryError
from dotenv import load_dotenv
import os

class LinearClient:
    def __init__(self, test_mode: bool = False):
        self.test_mode = test_mode
        if not test_mode:
            load_dotenv(override=True)
            self._init_client()
            
    def _init_client(self):
        """Initialize Linear GraphQL client"""
        self.api_key = os.getenv("LINEAR_API_KEY")
        self.team_id = os.getenv("LINEAR_TEAM_ID")
        self.project_id = os.getenv("LINEAR_PROJECT_ID")
        
        if not all([self.api_key, self.team_id, self.project_id]):
            raise ValueError("Missing required Linear environment variables")
            
        transport = RequestsHTTPTransport(
            url='https://api.linear.app/graphql',
            headers={'Authorization': self.api_key}
        )
        self.client = Client(transport=transport, fetch_schema_from_transport=True)
    
    def create_issue(self, title: str) -> str:
        """Create a Linear issue and return its identifier"""
        if self.test_mode:
            return f"ENG-{abs(hash(title)) % 1000}"
            
        mutation = gql("""
            mutation CreateIssue($title: String!, $teamId: String!, $projectId: String!) {
                issueCreate(input: {
                    title: $title,
                    teamId: $teamId,
                    projectId: $projectId
                }) {
                    success
                    issue {
                        identifier
                    }
                }
            }
        """)
        
        try:
            result = self.client.execute(mutation, variable_values={
                'title': title,
                'teamId': self.team_id,
                'projectId': self.project_id
            })
            return result['issueCreate']['issue']['identifier']
            
        except TransportQueryError as e:
            print(f"Error creating Linear issue: {str(e)}")
            self._debug_available_teams()
            return None
            
    def _debug_available_teams(self):
        """Debug helper to list available teams and projects"""
        try:
            query = gql("""
                query {
                    teams {
                        nodes {
                            id
                            name
                            projects {
                                nodes {
                                    id
                                    name
                                }
                            }
                        }
                    }
                }
            """)
            result = self.client.execute(query)
            print("Available teams:")
            for team in result['teams']['nodes']:
                print(f"Team ID: {team['id']}, Name: {team['name']}")
                print("Projects:")
                for project in team['projects']['nodes']:
                    print(f"Project ID: {project['id']}, Name: {project['name']}")
            
        except TransportQueryError as e:
            print(f"Error listing teams and projects: {str(e)}")