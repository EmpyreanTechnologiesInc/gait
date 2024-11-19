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
        # Check API key and team ID first
        if not self.api_key:
            raise ValueError("Missing required Linear API key")
        
        if not self.team_id:
            raise ValueError("Missing required Linear team ID")
            
        # Special handling for missing project ID
        if not self.project_id:
            print("LINEAR_PROJECT_ID not found in environment variables")
            transport = RequestsHTTPTransport(
                url='https://api.linear.app/graphql',
                headers={'Authorization': self.api_key}
            )
            self.client = Client(transport=transport, fetch_schema_from_transport=True)
            self.list_available_teams()
            raise ValueError("Please set LINEAR_PROJECT_ID to one of the above project IDs")
            
        transport = RequestsHTTPTransport(
            url='https://api.linear.app/graphql',
            headers={'Authorization': self.api_key}
        )
        self.client = Client(transport=transport, fetch_schema_from_transport=True)
    
    def create_issue(self, title: str, file_path: str = None, line_content: str = None, context: str = None) -> str:
        """Create a Linear issue and return its identifier"""
        if self.test_mode:
            # Generate a deterministic test ticket ID
            return f"TEST-{abs(hash(title)) % 1000}"
            
        # Create description with context information
        description = []
        if file_path:
            description.append(f"**File:** `{file_path}`")
        if context:
            description.append(f"**Context:** {context}")
            
        description = "\n\n".join(description)
            
        mutation = gql("""
            mutation CreateIssue($title: String!, $teamId: String!, $projectId: String!, $description: String) {
                issueCreate(input: {
                    title: $title,
                    teamId: $teamId,
                    projectId: $projectId,
                    description: $description
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
                'projectId': self.project_id,
                'description': description
            })
            return result['issueCreate']['issue']['identifier']
            
        except TransportQueryError as e:
            error_data = e.errors[0].get('extensions', {})
            error_type = error_data.get('type', 'Unknown error')
            error_message = error_data.get('userPresentableMessage', str(e))
            print(f"❌ Error creating Linear issue: {error_type} - {error_message}")
            print(" Please check your Linear API key and team ID")
            self.list_available_teams()
            return None
            
    def list_available_teams(self):
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
            error_data = e.errors[0].get('extensions', {})
            error_type = error_data.get('type', 'Unknown error')
            error_message = error_data.get('userPresentableMessage', str(e))
            print(f"❌ Error listing teams and projects: {error_type} - {error_message}")
            print(" Please check your Linear API key and team ID")