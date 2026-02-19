import os
from dotenv import load_dotenv
from jira import JIRA
from atlassian import Confluence
from google.adk.agents import Agent
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPServerParams

# Load secrets from your .env file
load_dotenv()

# --- 1. SET UP GITHUB TOOLSET (Remote MCP) ---
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
github_tools = McpToolset(
    connection_params=StreamableHTTPServerParams(
        url="https://api.githubcopilot.com/mcp/",
        headers={
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "X-MCP-Toolsets": "repos,pull_requests",
            "X-MCP-Readonly": "false"
        }
    )
)

# --- 2. SET UP CONNECTIONS (Stable Python Libraries) ---

# Jira Connection
jira_conn = JIRA(
    server=os.getenv("JIRA_URL"),
    basic_auth=(os.getenv("ATLASSIAN_EMAIL"), os.getenv("ATLASSIAN_TOKEN"))
)

# Confluence Connection
confluence_conn = Confluence(
    url=os.getenv("CONFLUENCE_URL"),
    username=os.getenv("ATLASSIAN_EMAIL"),
    password=os.getenv("ATLASSIAN_TOKEN"),
    cloud=True
)

# --- 3. JIRA STABLE TOOLS ---

def search_jira(jql_query: str):
    """Search for Jira tickets using JQL. Example: assignee = 'user@email.com'"""
    try:
        issues = jira_conn.search_issues(jql_query)
        results = [f"{i.key}: {i.fields.summary} ({i.fields.status})" for i in issues]
        return "\n".join(results) if results else "No tickets found."
    except Exception as e:
        return f"Error: {str(e)}"

def comment_on_ticket(issue_key: str, comment: str):
    """Adds a comment to a Jira ticket."""
    try:
        jira_conn.add_comment(issue_key, comment)
        return f"✅ Comment added to {issue_key}."
    except Exception as e:
        return f"❌ Error: {str(e)}"

def update_ticket_status(issue_key: str, status_name: str):
    """Moves a ticket to a new status. Use 'get_transitions' first to see valid names."""
    try:
        jira_conn.transition_issue(issue_key, transition=status_name)
        return f"✅ {issue_key} moved to {status_name}."
    except Exception as e:
        return f"❌ Error: {str(e)}"

def get_transitions(issue_key: str):
    """Lists the available status changes (transitions) for a specific ticket."""
    try:
        transitions = jira_conn.transitions(issue_key)
        return "\n".join([f"ID: {t['id']} - Name: {t['name']}" for t in transitions])
    except Exception as e:
        return f"Error: {str(e)}"

def create_issue(project: str, summary: str, description: str, issuetype: str = 'Story'):
    """Creates a new Jira issue. Default type is 'Story'."""
    try:
        new_issue = jira_conn.create_issue(
            project=project,
            summary=summary,
            description=description,
            issuetype={'name': issuetype}
        )
        return f"✅ Issue created: {new_issue.key}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

def get_issue_details(issue_key: str):
    """Fetches full details of a specific issue including description, assignee, and priority."""
    try:
        issue = jira_conn.issue(issue_key)
        details = (
            f"Key: {issue.key}\nSummary: {issue.fields.summary}\n"
            f"Status: {issue.fields.status.name}\nAssignee: {issue.fields.assignee}\n"
            f"Description: {issue.fields.description}"
        )
        return details
    except Exception as e:
        return f"Error: {str(e)}"

def assign_issue(issue_key: str, account_id: str):
    """Assigns an issue to a specific user using their Account ID."""
    try:
        jira_conn.assign_issue(issue_key, account_id)
        return f"✅ {issue_key} assigned to {account_id}."
    except Exception as e:
        return f"❌ Error: {str(e)}"

def add_attachment(issue_key: str, file_path: str):
    """Attaches a file to a Jira ticket."""
    try:
        with open(file_path, 'rb') as f:
            jira_conn.add_attachment(issue=issue_key, attachment=f)
        return f"✅ File attached to {issue_key}."
    except Exception as e:
        return f"❌ Error: {str(e)}"

def get_issue_comments(issue_key: str):
    """Retrieves all comments for a specific issue."""
    try:
        issue = jira_conn.issue(issue_key)
        comments = [f"{c.author.displayName}: {c.body}" for c in issue.fields.comment.comments]
        return "\n---\n".join(comments) if comments else "No comments found."
    except Exception as e:
        return f"Error: {str(e)}"

def log_work(issue_key: str, time_spent: str):
    """Logs work on an issue. Format: '2h', '30m', '1d'."""
    try:
        jira_conn.add_worklog(issue_key, timeSpent=time_spent)
        return f"✅ Logged {time_spent} to {issue_key}."
    except Exception as e:
        return f"❌ Error: {str(e)}"

def list_projects():
    """Returns a list of all accessible Jira projects."""
    try:
        projects = jira_conn.projects()
        return "\n".join([f"{p.key}: {p.name}" for p in projects])
    except Exception as e:
        return f"Error: {str(e)}"

def get_sprint_issues(sprint_id: int):
    """Lists all issues within a specific sprint ID."""
    try:
        issues = jira_conn.search_issues(f'sprint = {sprint_id}')
        return "\n".join([f"{i.key}: {i.fields.summary}" for i in issues])
    except Exception as e:
        return f"Error: {str(e)}"

def update_issue_priority(issue_key: str, priority_name: str):
    """Updates the priority of an issue (e.g., 'Highest', 'High', 'Low')."""
    try:
        issue = jira_conn.issue(issue_key)
        issue.update(fields={'priority': {'name': priority_name}})
        return f"✅ Priority updated to {priority_name} for {issue_key}."
    except Exception as e:
        return f"❌ Error: {str(e)}"

def link_issues(inward_key: str, outward_key: str, link_type: str = "Relates"):
    """Links two issues together (e.g., 'Blocks', 'Relates', 'Duplicate')."""
    try:
        jira_conn.create_issue_link(type=link_type, inwardIssue=inward_key, outwardIssue=outward_key)
        return f"✅ Linked {inward_key} as {link_type} {outward_key}."
    except Exception as e:
        return f"❌ Error: {str(e)}"

def create_sprint(board_id: int, sprint_name: str, start_date: str = None, end_date: str = None):
    """
    Creates a new sprint within a specific board.
    board_id: The ID of the Scrum board (e.g., 1).
    sprint_name: Name of the sprint (e.g., 'Sprint 1').
    start_date: Optional. Format: 'YYYY-MM-DDTHH:MM:SS.000+0000'
    end_date: Optional. Same format as start_date.
    """
    try:
        # Create the sprint
        new_sprint = jira_conn.create_sprint(name=sprint_name, board_id=board_id, startDate=start_date, endDate=end_date)
        return f"✅ Sprint '{sprint_name}' created successfully! ID: {new_sprint.id}"
    except Exception as e:
        return f"❌ Error creating sprint: {str(e)}"

def update_issue_type(issue_key: str, new_type: str):
    """
    Changes the issue type of an existing ticket (e.g., from 'Bug' to 'Task').
    issue_key: The ticket ID (e.g., 'PROJ-123').
    new_type: The name of the new issue type (e.g., 'Story', 'Bug', 'Task', 'Epic').
    """
    try:
        issue = jira_conn.issue(issue_key)
        issue.update(fields={'issuetype': {'name': new_type}})
        return f"✅ {issue_key} has been successfully changed to a '{new_type}'."
    except Exception as e:
        return f"❌ Error: {str(e)}. (Note: Some type changes require a 'Move' operation if status workflows differ.)"

def add_issue_to_sprint(issue_key: str, sprint_id: int):
    """
    Moves an existing Jira ticket into a specific sprint.
    issue_key: The ticket ID (e.g., 'PROJ-123').
    sprint_id: The numerical ID of the sprint (e.g., 42).
    """
    try:
        issue = jira_conn.issue(issue_key)
        issue.update(fields={'sprint': sprint_id})
        return f"✅ {issue_key} has been added to sprint {sprint_id}."
    except Exception as e:
        return (f"❌ Error: {str(e)}. Hint: If 'sprint' field isn't recognized, "
                "ensure the ticket is in a project that has a Scrum board.")

def add_issue_to_sprint_by_name(issue_key: str, board_id: int, sprint_name: str):
    """
    Finds a sprint by name on a specific board and adds the ticket to it.
    issue_key: The ticket ID (e.g., 'PROJ-123').
    board_id: The ID of the board where the sprint exists.
    sprint_name: The case-sensitive name of the sprint.
    """
    try:
        # 1. Get all sprints for the board
        sprints = jira_conn.sprints(board_id)
        # 2. Find the sprint that matches the name
        target_sprint = next((s for s in sprints if s.name.lower() == sprint_name.lower()), None)
        if not target_sprint:
            return f"❌ Could not find a sprint named '{sprint_name}' on board {board_id}."
        # 3. Add the issue to the found sprint ID
        jira_conn.add_issues_to_sprint(target_sprint.id, [issue_key])
        return f"✅ {issue_key} successfully added to '{sprint_name}' (ID: {target_sprint.id})."
    except Exception as e:
        return f"❌ Error: {str(e)}"

def get_backlog_tickets(project_key: str):
    """
    Retrieves all tickets in the backlog for a specific project.
    Backlog tickets are issues not assigned to any sprint.
    """
    try:
        # JQL Explanation:
        # project = 'KEY' -> Filter by project
        # sprint is EMPTY -> Not in an active or future sprint
        # resolution is EMPTY -> Not closed/done
        jql_query = f"project = '{project_key}' AND sprint is EMPTY AND resolution is EMPTY"

        issues = jira_conn.search_issues(jql_query)
        results = [f"{i.key}: {i.fields.summary} [{i.fields.status}]" for i in issues]

        if not results:
            return f"No backlog tickets found for project {project_key}."

        return f"Backlog for {project_key}:\n" + "\n".join(results)
    except Exception as e:
        return f"❌ Error retrieving backlog: {str(e)}"

def get_sprint_id_by_name(board_id: int, sprint_name: str):
    """Finds the internal ID for a sprint based on its name."""
    try:
        sprints = jira_conn.sprints(board_id)
        for s in sprints:
            if s.name.lower() == sprint_name.lower():
                return s.id
        return None
    except Exception as e:
        return f"Error finding sprint: {str(e)}"

def check_sprint_health(board_id: int, sprint_name: str):
    """
    Analyzes the health of a sprint by checking the status of all its issues.
    Calculates completion percentage and lists blockers.
    """
    try:
        sprint_id = get_sprint_id_by_name(board_id, sprint_name)
        if not sprint_id:
            return f"❌ Sprint '{sprint_name}' not found on board {board_id}."

        issues = jira_conn.search_issues(f'sprint = {sprint_id}')
        if not issues:
            return f"Sprint '{sprint_name}' is empty."

        total = len(issues)
        done = len([i for i in issues if i.fields.status.name.lower() in ['done', 'closed', 'resolved']])
        in_progress = len([i for i in issues if i.fields.status.name.lower() in ['in progress', 'review']])
        to_do = total - (done + in_progress)

        # Calculate Percentage
        completion_rate = (done / total) * 100

        health_report = (
            f"📊 **Health Report for {sprint_name}**\n"
            f"- Completion: {completion_rate:.1f}%\n"
            f"- ✅ Done: {done}\n"
            f"- 🚧 In Progress: {in_progress}\n"
            f"- 📝 To Do: {to_do}\n"
            f"- 🚩 Total Issues: {total}"
        )
        return health_report
    except Exception as e:
        return f"❌ Error calculating health: {str(e)}"

# --- 4. CONFLUENCE STABLE TOOLS ---

def read_confluence_page(page_id: str):
    """Reads the content of a Confluence page by ID."""
    try:
        page = confluence_conn.get_page_by_id(page_id, expand='body.storage')
        return page['body']['storage']['value']
    except Exception as e:
        return f"Error: {str(e)}"

def search_confluence(query: str):
    """Searches Confluence pages using CQL siteSearch."""
    try:
        search_results = confluence_conn.cql(cql=f'siteSearch ~ "{query}"', limit=5)
        results = search_results.get('results', [])
        if not results:
            return f"No pages found matching '{query}'."
        # One-liner to extract IDs and Titles
        pages = [f"ID: {r['content']['id']} | Title: {r['content']['title']}" for r in results]
        return "\n".join(pages)
    except Exception as e:
        return f"❌ Search error: {str(e)}"

def create_confluence_page(space: str, title: str, body: str):
    """Creates a new page in a specific Confluence Space."""
    try:
        confluence_conn.create_page(space, title, body)
        return f"✅ Page '{title}' created in space {space}."
    except Exception as e:
        return f"Error: {str(e)}"
def create_confluence_space(space_key: str, space_name: str):
    """
    Creates a new Confluence Space.
    space_key: A short uppercase identifier (e.g., 'PROJ').
    space_name: The full display name (e.g., 'Project Forge').
    """
    try:
        # space_key must be unique and usually all uppercase
        confluence_conn.create_space(space_key.upper(), space_name)
        return f"✅ Space '{space_name}' ({space_key.upper()}) created successfully!"
    except Exception as e:
        return f"❌ Error creating space: {str(e)}"
def list_all_confluence_spaces():
    """Retrieves a list of all accessible spaces in the Confluence account."""
    try:
        # get_all_spaces returns a list of space objects
        spaces = confluence_conn.get_all_spaces(start=0, limit=50)
        results = spaces.get('results', [])

        if not results:
            return "No spaces found or you do not have permission to view them."

        space_list = [f"Key: {s['key']} | Name: {s['name']}" for s in results]
        return "Available Spaces:\n" + "\n".join(space_list)
    except Exception as e:
        return f"❌ Error listing spaces: {str(e)}"

def add_label_to_page(page_id: str, label: str):
    """Adds a specific label (tag) to a Confluence page for organization."""
    try:
        confluence_conn.set_page_label(page_id, label)
        return f"✅ Label '{label}' added to page {page_id}."
    except Exception as e:
        return f"❌ Error adding label: {str(e)}"

def get_page_labels(page_id: str):
    """Retrieves all labels currently attached to a page."""
    try:
        labels_data = confluence_conn.get_page_labels(page_id)
        labels = [l['name'] for l in labels_data.get('results', [])]
        return f"Labels for {page_id}: " + (", ".join(labels) if labels else "None")
    except Exception as e:
        return f"❌ Error getting labels: {str(e)}"

def add_comment_to_page(page_id: str, text: str):
    """Adds a comment to a Confluence page."""
    try:
        confluence_conn.attach_content(page_id, text)
        return f"✅ Comment added to page {page_id}."
    except Exception as e:
        return f"❌ Error adding comment: {str(e)}"

def list_page_attachments(page_id: str):
    """Lists all files attached to a specific page."""
    try:
        attachments = confluence_conn.get_attachments_from_content(page_id)
        files = [f['title'] for f in attachments.get('results', [])]
        return "Attachments: " + (", ".join(files) if files else "None")
    except Exception as e:
        return f"❌ Error listing attachments: {str(e)}"

def delete_confluence_page(page_id: str):
    """Deletes a page (moves it to trash)."""
    try:
        confluence_conn.remove_page(page_id)
        return f"✅ Page {page_id} moved to trash."
    except Exception as e:
        return f"❌ Error deleting page: {str(e)}"

def update_page_content(page_id: str, title: str, body: str):
    """Updates the title and content of an existing page."""
    try:
        confluence_conn.update_page(page_id, title, body)
        return f"✅ Page {page_id} updated successfully."
    except Exception as e:
        return f"❌ Error updating page: {str(e)}"

def get_all_pages_in_space(space_key: str):
    """Lists the titles and IDs of all pages within a space."""
    try:
        pages = confluence_conn.get_all_pages_from_space(space_key, start=0, limit=50)
        page_list = [f"ID: {p['id']} | Title: {p['title']}" for p in pages]
        return f"Pages in {space_key}:\n" + "\n".join(page_list)
    except Exception as e:
        return f"❌ Error: {str(e)}"

def move_confluence_page(page_id: str, target_parent_id: str):
    """Moves a page to a new parent page."""
    try:
        # This requires the target space and new parent ID
        page_details = confluence_conn.get_page_by_id(page_id)
        space = page_details['space']['key']
        title = page_details['title']
        confluence_conn.update_page(page_id, title, body=None, parent_id=target_parent_id)
        return f"✅ Page {page_id} moved under parent {target_parent_id}."
    except Exception as e:
        return f"❌ Error moving page: {str(e)}"

def search_by_label(label: str):
    """Finds all pages that share a specific label."""
    try:
        results = confluence_conn.get_all_pages_by_label(label)
        pages = [f"ID: {p['id']} | Title: {p['title']}" for p in results]
        return f"Pages with label '{label}':\n" + "\n".join(pages)
    except Exception as e:
        return f"❌ Error searching label: {str(e)}"

def get_confluence_user_details(username_or_email: str):
    """Gets details about a Confluence user (useful for mentions/permissions)."""
    try:
        user = confluence_conn.get_user_details_by_username(username_or_email)
        return f"User: {user.get('displayName')} | AccountID: {user.get('accountId')}"
    except Exception as e:
        return f"❌ User not found: {str(e)}"

# --- 5. THE SUB-AGENTS ---

github_agent = Agent(
    model="gemini-2.0-flash",
    name="Github_Expert",
    description="Specialist in GitHub. Can list repos and read Pull Requests.",
    instruction=(
        "You are a GitHub expert.Always answer the questions related to github if you can using the right tools. "
        "ALWAYS stick to the data you have found and give your response on the basis only."
    ),
    tools=[github_tools]
)

jira_agent = Agent(
    model="gemini-2.0-flash",
    name="Jira_Expert",
    description="Specialist in Jira. Can search, comment, and move tickets.",
    instruction=(
        "You are a Jira expert. Use JQL for searching. "
        "Before moving a ticket, check available transitions if you aren't sure of the name."
    ),
    tools=[
        search_jira, comment_on_ticket, update_ticket_status, get_transitions,
        create_issue, get_issue_details, assign_issue, add_attachment,
        get_issue_comments, log_work, list_projects, get_sprint_issues,
        update_issue_priority, link_issues, create_sprint, update_issue_type,
        add_issue_to_sprint, add_issue_to_sprint_by_name, get_backlog_tickets,
        get_sprint_id_by_name,check_sprint_health
    ]
)

confluence_agent = Agent(
    model="gemini-2.0-flash",
    name="Confluence_Expert",
    description="Specialist in Confluence. Can search, read, and create documentation.",
    instruction=(
        "You are a documentation expert. Use 'search_confluence' to find info,When searching, provide only the "
        "search keyword as a simple string to the search_confluence tool. "
        "and 'read_confluence_page' to get details. Format content clearly."
        "similarly you can check for other tools of confluence and use it as needed."
        "ALWAYS stick to the data you have found and give answere on that basis only"
    ),
    tools=[read_confluence_page, search_confluence, create_confluence_page,
           create_confluence_space, list_all_confluence_spaces,
           add_label_to_page, get_page_labels, add_comment_to_page,
           list_page_attachments, delete_confluence_page, update_page_content,
           get_all_pages_in_space, move_confluence_page, search_by_label,
           get_confluence_user_details]
)

# --- 6. THE MASTER AGENT ---

root_agent = Agent(
    model="gemini-2.0-flash",
    name="Master_Manager",
    instruction=(
        "You are the central coordinator and data courier. You MUST use your sub-agents to answer. "
        "When a task involves multiple systems (Jira + Confluence): "
        "1. Identify the flow: 'Source' -> 'Destination'. "
        "2. CALL the Source expert (e.g., Jira_Expert) to get the data. "
        "3. ONCE YOU HAVE THE DATA, call the Destination expert (e.g., Confluence_Expert) "
        "   and provide that specific data in your request to them. "
        "4. DO NOT ask the user to provide data that another agent has already retrieved. "
        "Example: If Jira_Expert gives you ticket details, tell Confluence_Expert: "
        "'Create a page with this content: [Paste details here]'"
    ),
    sub_agents=[github_agent, jira_agent, confluence_agent]
)

