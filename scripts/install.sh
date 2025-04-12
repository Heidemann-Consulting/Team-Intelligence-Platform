#!/bin/bash
# Team Intelligence Platform (TIP) - Phase 1 Installation Script
# Version: 1.0.0
# License: Apache 2.0

# Configuration variables
TIP_BASE_DIR="$HOME/tip"
TIP_DATA_DIR="$TIP_BASE_DIR/data"
TIP_CONFIG_DIR="$TIP_BASE_DIR/configs"
TIP_SCRIPTS_DIR="$TIP_BASE_DIR/scripts"
TIP_VAULT_DIR="$HOME/tip-vault"
OLLAMA_PORT=11434
OPENWEBUI_PORT=3000
HEDGEDOC_PORT=3001
LANGFLOW_PORT=7860

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print header
echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}Team Intelligence Platform (TIP) - Phase 1${NC}"
echo -e "${BLUE}Installation Script${NC}"
echo -e "${BLUE}============================================${NC}"
echo ""

# Check for required tools
echo -e "${YELLOW}Checking prerequisites...${NC}"

# Check for Git
if ! command -v git &> /dev/null; then
    echo -e "${RED}Git is required but not installed.${NC}"
    echo "Please install Git and run this script again."
    exit 1
else
    echo -e "${GREEN}Git is installed.${NC}"
fi

# Check for Docker if not skipping container deployment
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Docker is not installed. Installing Docker...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    sudo usermod -aG docker $USER
    echo -e "${GREEN}Docker installed. You may need to log out and back in for group changes to take effect.${NC}"
    echo "After logging back in, please run this script again."
    exit 0
else
    echo -e "${GREEN}Docker is installed.${NC}"
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${YELLOW}Docker Compose not found. Installing...${NC}"
        sudo curl -L "https://github.com/docker/compose/releases/download/v2.23.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
        echo -e "${GREEN}Docker Compose installed.${NC}"
    else
        echo -e "${GREEN}Docker Compose is installed.${NC}"
    fi
fi

# Create directories
echo -e "${YELLOW}Creating directories...${NC}"
mkdir -p "$TIP_DATA_DIR"/{ollama,openwebui,hedgedoc,langflow}
mkdir -p "$TIP_CONFIG_DIR"
mkdir -p "$TIP_SCRIPTS_DIR"
echo -e "${GREEN}Directories created.${NC}"

# Deploy Ollama
echo -e "${YELLOW}Deploying Ollama...${NC}"
curl -fsSL https://ollama.ai/install.sh | sh
echo -e "${GREEN}Ollama installed.${NC}"

# Pull initial models
echo -e "${YELLOW}Pulling initial LLM models (this may take some time)...${NC}"
ollama pull llama3 && echo -e "${GREEN}Llama3 model pulled.${NC}"
ollama pull mistral && echo -e "${GREEN}Mistral model pulled.${NC}"

# Create docker-compose.yml
echo -e "${YELLOW}Creating Docker Compose configuration...${NC}"
cat > "$TIP_CONFIG_DIR/docker-compose.yml" << EOL
version: '3'

services:
  openwebui:
    image: ghcr.io/open-webui/open-webui:main
    container_name: openwebui
    volumes:
      - ${TIP_DATA_DIR}/openwebui:/app/backend/data
    ports:
      - "${OPENWEBUI_PORT}:8080"
    extra_hosts:
      - "host.docker.internal:host-gateway"
    restart: unless-stopped

  hedgedoc:
    image: hedgedoc/hedgedoc:latest
    container_name: hedgedoc
    volumes:
      - ${TIP_DATA_DIR}/hedgedoc:/hedgedoc/public/uploads
    ports:
      - "${HEDGEDOC_PORT}:3000"
    environment:
      - CMD_DB_URL=sqlite:///data/hedgedoc.db
      - CMD_DOMAIN=localhost
      - CMD_URL_ADDPORT=true
      - CMD_URL_PROTOCOL=http
      - CMD_ALLOW_ANONYMOUS=true
    restart: unless-stopped

  langflow:
    image: logspace/langflow:latest
    container_name: langflow
    volumes:
      - ${TIP_DATA_DIR}/langflow:/root/.cache/langflow
    ports:
      - "${LANGFLOW_PORT}:7860"
    restart: unless-stopped
EOL
echo -e "${GREEN}Docker Compose configuration created.${NC}"

# Start Docker containers
echo -e "${YELLOW}Starting Docker containers...${NC}"
cd "$TIP_CONFIG_DIR"
docker-compose up -d
echo -e "${GREEN}Docker containers started.${NC}"

# Create knowledge repository
echo -e "${YELLOW}Setting up knowledge repository...${NC}"
mkdir -p "$TIP_VAULT_DIR"/{context/{domain,process,technical},decisions/{project,team},meetings/{daily,retro,planning,other},prompts/{context,meetings,templates},templates/{curation,decision,meeting}}

# Initialize Git repository
cd "$TIP_VAULT_DIR"
git init
echo "# Team Intelligence Platform Knowledge Repository" > README.md
cat > .gitignore << EOL
.obsidian/workspace*
.obsidian/cache
.DS_Store
EOL

# Create initial templates
echo -e "${YELLOW}Creating initial templates...${NC}"

# Daily curation template
cat > "$TIP_VAULT_DIR/templates/curation/daily-curation-template.md" << EOL
# Daily Context Curation - {{date:YYYY-MM-DD}}

## Participants
- [List of team members present]

## New Context Elements
- [Team Member 1]: [Context element]
- [Team Member 2]: [Context element]
- [Team Member 3]: [Context element]

## Decisions
- Accept/Reject: [Context element] - [Rationale]
- Accept with modification: [Context element] → [Modified version]

## Action Items
- [ ] [Action description] (@owner) (due: [date])
- [ ] [Action description] (@owner) (due: [date])

## Notes
[Any additional notes or observations]
EOL

# Weekly curation template
cat > "$TIP_VAULT_DIR/templates/curation/weekly-curation-template.md" << EOL
# Weekly Context Curation - {{date:YYYY-MM-DD}}

## Participants
- [List of team members present]

## Context Health Assessment
- Total knowledge items: [number]
- New items this week: [number]
- Accessed items this week: [number]
- Coverage areas: [list key areas]
- Identified gaps: [list gaps]

## Priority Improvement Areas
1. [Area 1] - [Specific improvements needed]
2. [Area 2] - [Specific improvements needed]
3. [Area 3] - [Specific improvements needed]

## Action Items
- [ ] [Action description] (@owner) (due: [date])
- [ ] [Action description] (@owner) (due: [date])

## Discussion Summary
[Summary of key discussion points]
EOL

# Meeting notes template
cat > "$TIP_VAULT_DIR/templates/meeting/meeting-notes-template.md" << EOL
# {{title}} - {{date:YYYY-MM-DD}}

## Participants
- [List of attendees]

## Agenda
1. [Agenda item 1]
2. [Agenda item 2]
3. [Agenda item 3]

## Discussion
### [Agenda item 1]
[Raw notes]
#decision [Any decisions made]
#action [Any actions identified]

### [Agenda item 2]
[Raw notes]
#decision [Any decisions made]
#action [Any actions identified]

### [Agenda item 3]
[Raw notes]
#decision [Any decisions made]
#action [Any actions identified]

## Next Steps
- [Next step 1]
- [Next step 2]
EOL

# Initial prompt templates
cat > "$TIP_VAULT_DIR/prompts/meetings/meeting-summary-prompt.md" << EOL
# Prompt: Meeting Summary

## Version
1.0 - {{date:YYYY-MM-DD}}

## Purpose
Generate a structured summary of meeting notes, extracting key decisions, action items, and discussion points.

## Prompt Text
\`\`\`
You are an AI assistant helping a software development team create structured summaries of their meetings. Your task is to analyze the raw meeting notes below and generate a clear, concise summary.

The summary should include:
1. A brief overview (1-2 sentences)
2. Key decisions made (formatted as bullet points)
3. Action items with owners (formatted as tasks with @mentions)
4. A concise summary of key discussion points by topic
5. References to any related documentation or context

Format the summary using Markdown with clear headings and structure. Be comprehensive but concise, focusing on the most important information. Maintain technical accuracy and use the team's terminology.

Raw meeting notes:
[NOTES]
\`\`\`

## Expected Output
A well-structured meeting summary with overview, decisions, actions, and discussion points.

## Example Input/Output
### Input
Raw meeting notes from a sprint planning session.

### Output
A structured summary with decisions, action items with assignees, and key discussion points.
EOL

# Commit initial repository
git add .
git commit -m "Initial knowledge repository structure"
echo -e "${GREEN}Knowledge repository initialized.${NC}"

# Create startup script
echo -e "${YELLOW}Creating startup script...${NC}"
cat > "$TIP_SCRIPTS_DIR/start-tip.sh" << EOL
#!/bin/bash
# TIP Environment Startup Script

# Start Ollama server if not running
if ! pgrep -x "ollama" > /dev/null; then
    echo "Starting Ollama server..."
    ollama serve &
    # Wait for server to start
    sleep 3
fi

# Start Docker containers if not running
cd "${TIP_CONFIG_DIR}"
docker-compose up -d

echo "TIP environment started. Access points:"
echo "- Ollama API: http://localhost:${OLLAMA_PORT}"
echo "- Open-webui: http://localhost:${OPENWEBUI_PORT}"
echo "- HedgeDoc: http://localhost:${HEDGEDOC_PORT}"
echo "- LangFlow: http://localhost:${LANGFLOW_PORT}"
echo ""
echo "Knowledge repository: ${TIP_VAULT_DIR}"
EOL

chmod +x "$TIP_SCRIPTS_DIR/start-tip.sh"
echo -e "${GREEN}Startup script created.${NC}"

# Print success message
echo ""
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}Installation Complete!${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""
echo "TIP environment has been set up with the following components:"
echo "- Ollama (LLM runtime): http://localhost:${OLLAMA_PORT}"
echo "- Open-webui (AI interface): http://localhost:${OPENWEBUI_PORT}"
echo "- HedgeDoc (Collaborative editing): http://localhost:${HEDGEDOC_PORT}"
echo "- LangFlow (Optional workflow builder): http://localhost:${LANGFLOW_PORT}"
echo ""
echo "Knowledge repository: ${TIP_VAULT_DIR}"
echo ""
echo "Next steps:"
echo "1. Open Obsidian and create a vault pointing to: ${TIP_VAULT_DIR}"
echo "2. Connect the Git repository to a remote (GitHub, GitLab, etc.)"
echo "3. Follow the First-Time Setup Guide in the documentation"
echo ""
echo "To start the TIP environment in the future, run:"
echo "${TIP_SCRIPTS_DIR}/start-tip.sh"
echo ""