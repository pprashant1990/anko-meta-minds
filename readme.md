This is a smaple repo, will be used only for the demo relate to anko idea forge event.

gcloud auth application-default login

gcloud auth application-default set-quota-project meta-minds-267

run the agent in cli = adk run folder_name

run the agent in web = adk web

command to deply agent in agent engine - 

adk deploy agent_engine . \
  --project meta-minds-267 \
  --region us-central1 \
  --display_name "Master_Manager_Service" \
  --env_file .env
