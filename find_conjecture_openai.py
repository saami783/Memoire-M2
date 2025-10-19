from openai import OpenAI
client = OpenAI()

# todo : migrer vers openai plutôt que mistral car la limite de documents est plus grande (80 toutes les 3h)

pdf = client.files.create(file=open("mon_doc.pdf", "rb"), purpose="assistants")

resp = client.responses.create(
  model="gpt-5-thinking",
  input=[
    {"role":"user","content":[
      {"type":"input_text","text":"Résume le document."},
      {"type":"input_file","file_id": pdf.id}
    ]}
  ]
)

print(resp.output_text)
