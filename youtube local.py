import os
import pickle
import google.auth.transport.requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Escopo necessário para acessar a API do YouTube
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
CLIENT_SECRETS_FILE = r"arquivo credencial.json"
TOKEN_PICKLE = "token.pickle"

def authenticate():
    """Autentica na API do YouTube e retorna o serviço."""
    creds = None
    
    # Tenta carregar credenciais salvas
    if os.path.exists(TOKEN_PICKLE):
        with open(TOKEN_PICKLE, "rb") as token:
            creds = pickle.load(token)
    
    # Se não houver credenciais válidas, faz login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(google.auth.transport.requests.Request()) 
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)  # Alteração para rodar localmente
        
        # Salva as credenciais para reutilização
        with open(TOKEN_PICKLE, "wb") as token:
            pickle.dump(creds, token)
    
    return build("youtube", "v3", credentials=creds)

def upload_video(youtube, video_path, title, description, tags, category_id="22", privacy_status="public"):
    """
    Faz o upload de um vídeo para o YouTube.

    Args:
        youtube: Objeto de serviço autenticado.
        video_path: Caminho do arquivo de vídeo.
        title: Título do vídeo.
        description: Descrição do vídeo.
        tags: Lista de tags.
        category_id: ID da categoria do YouTube (22 = "People & Blogs").
        privacy_status: Status do vídeo (public, private, unlisted).
    """
    
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": category_id,
            },
            "status": {
                "privacyStatus": privacy_status,
            },
        },
        media_body=MediaFileUpload(video_path, chunksize=-1, resumable=True),
    )
    
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Progresso do upload: {int(status.progress() * 100)}%")
    
    print("Upload concluído!")
    print(f"Vídeo disponível em: https://www.youtube.com/watch?v={response['id']}")

if __name__ == "__main__":
    youtube_service = authenticate()
    upload_video(
        youtube_service,
        video_path=r"arquivo de video.mp4",
        title="Meu Vídeo Teste",
        description="Descrição do meu vídeo",
        tags=["teste", "upload", "YouTube API"],
        privacy_status="public"
    )
