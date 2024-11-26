from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from gql.transport.exceptions import TransportQueryError
from dotenv import load_dotenv
import os

class LinearClient:
    def __init__(self):
        load_dotenv(override=True)
        self._init_client()
            
    def _init_client(self):
        """Initialize Linear GraphQL client"""
        self.api_key = os.getenv("LINEAR_API_KEY")
        self.team_id = os.getenv("LINEAR_TEAM_ID")
        self.project_id = os.getenv("LINEAR_PROJECT_ID")

        if not self.api_key:
            raise ValueError("Missing required Linear API key")
        
        if not self.team_id:
            raise ValueError("Missing required Linear team ID")
            
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
        # include file path and context in description to provide more context for the ticket
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

    def complete_issue(self, issue_id: str) -> bool:
        """
        Mark a Linear issue as completed.
        
        Args:
            issue_id: The Linear issue ID (e.g., 'ENG-123')
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            query = gql("""
                query GetIssue($id: String!) {
                    issue(id: $id) {
                        id
                        team {
                            id
                        }
                    }
                }
            """)
            
            result = self.client.execute(query, variable_values={'id': issue_id})
            if not result.get('issue'):
                print(f"Issue {issue_id} not found")
                return False
                        
            query = gql("""
                query {
                    workflowStates {
                        nodes {
                            id
                            name
                        }
                    }
                }
            """)
            
            # search for the 'Done' state ID because different teams may have different workflow states
            result = self.client.execute(query)
            states = result['workflowStates']['nodes']
            done_state = next((state for state in states if state['name'].lower() == 'done'), None)
            
            if not done_state:
                print(f"Could not find 'Done' state")
                return False
            
            mutation = gql("""
                mutation UpdateIssue($issueId: String!, $stateId: String!) {
                    issueUpdate(
                        id: $issueId,
                        input: { stateId: $stateId }
                    ) {
                        success
                        issue {
                            id
                            title
                        }
                    }
                }
            """)
            
            result = self.client.execute(mutation, variable_values={
                'issueId': issue_id,
                'stateId': done_state['id']
            })
            
            if result['issueUpdate']['success']:
                print(f"✅ Marked Linear issue {issue_id} as done")
                return True
            return False
            
        except Exception as e:
            print(f"Error completing issue {issue_id}: {str(e)}")
            return False