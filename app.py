import os
import yt_dlp
import google.generativeai as genai
from dotenv import load_dotenv
import time
import re
from datetime import datetime
import requests

# Load environment variables from .env file
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Get Notion credentials
NOTION_API_KEY = os.getenv('NOTION_API_KEY')
NOTION_DATABASE_ID = os.getenv('NOTION_DATABASE_ID')

# Define Notion database URL
notion_url = 'https://api.notion.com/v1/pages'

# Headers for Notion request
headers = {
    'Authorization': f'Bearer {NOTION_API_KEY}',
    'Content-Type': 'application/json',
    'Notion-Version': '2022-06-28'
}

def download_video(url):
    """Download YouTube video using yt-dlp."""
    video_id = url.split("v=")[-1]  # Extract video ID from URL
    output_path = f"videos/{video_id}.mp4"  # Define output path
    ydl_opts = {
        'format': 'best',
        'outtmpl': output_path,  # Output file name
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return output_path, url  # Return downloaded video path and original URL

def clean_filename(filename):
    """Remove invalid characters from filename."""
    # Remove non-alphanumeric characters (except underscore and hyphen)
    cleaned = re.sub(r'[^\w\-_\. ]', '', filename)
    # Replace spaces with underscores
    cleaned = cleaned.replace(' ', '_')
    # Limit filename length to 255 characters
    return cleaned[:255]

def rename_video_file(original_path, new_title):
    """Rename video file."""
    new_title = clean_filename(new_title)
    new_path = os.path.join(os.path.dirname(original_path), f"{new_title}.mp4")
    os.rename(original_path, new_path)
    return new_path

def upload_to_gemini(path, mime_type=None):
    """Upload file to Gemini API."""
    file = genai.upload_file(path, mime_type=mime_type)
    print(f"Uploaded file '{file.display_name}' as: {file.uri}")
    return file

def wait_for_files_active(files):
    """Wait for files to be active in the API."""
    print("Waiting for file processing...")
    for name in (file.name for file in files):
        file = genai.get_file(name)
        while file.state.name == "PROCESSING":
            print(".", end="", flush=True)
            time.sleep(10)
            file = genai.get_file(name)
        if file.state.name != "ACTIVE":
            raise Exception(f"File {file.name} failed to process")
    print("...all files ready\n")

def describe_video(file_path, original_url):
    """Describe video using Gemini API."""
    files = [upload_to_gemini(file_path, mime_type="video/mp4")]
    wait_for_files_active(files)

    # Create chat session
    chat_session = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config={
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
            "response_mime_type": "text/plain",
        }
    ).start_chat(
        history=[
            {"role": "user", "parts": [files[0]]},
            {"role": "user", "parts": ["Please describe this video, organized in bullet points and other structures. Keep the description concise, within 1500 characters."]},
        ]
    )

    response = chat_session.send_message("INSERT_INPUT_HERE")
    description = response.text
    
    # Ensure description doesn't exceed 2000 characters
    if len(description) > 2000:
        description = description[:1997] + "..."
    
    print(description)

    # Generate short title from description
    title_response = chat_session.send_message(
        "Please generate a title based on the description you created for the video, without special characters, only numbers and letters, with a maximum of 3 words. Use '_' between the words instead of spaces."
    )
    generated_title = title_response.text.strip()
    print(f"Generated Title: {generated_title}")

    # Rename video file
    new_video_path = rename_video_file(file_path, generated_title)

    # Ask if user wants to keep the video
    keep_video = input("Would you like to keep the video? (y/n): ").strip().lower()

    # Determine if video was saved locally
    local_saved = "yes" if keep_video == 'y' else "no"

    # If user chooses not to keep the video, delete it
    if keep_video != 'y':
        os.remove(new_video_path)  # Delete renamed video
        print("Video has been deleted.")
    else:
        print("Video will be saved locally.")

    # Add video and information to Notion
    date_suffix = datetime.now().strftime("%d_%m_%y")

    # Data to be inserted into Notion table
    data = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "URL": {
                "title": [
                    {
                        "text": {
                            "content": original_url
                        }
                    }
                ]
            },
            "Title": {
                "rich_text": [
                    {
                        "text": {
                            "content": generated_title,
                        },
                    },
                ],
            },
            "Published": {
                "date": {
                    "start": datetime.now().isoformat()
                }
            },
            "Description": {
                "rich_text": [
                    {
                        "text": {
                            "content": description,
                        },
                    },
                ],
            },
            "Local Saved": {
                "rich_text": [
                    {
                        "text": {
                            "content": local_saved
                        }
                    }
                ]
            }
        }
    }

    # Send request to add new page to database
    response = requests.post(notion_url, headers=headers, json=data)

    # Check Notion response
    if response.status_code == 200:
        print("Data successfully inserted into Notion!")
    else:
        print(f"Error inserting data into Notion: {response.status_code} - {response.text}")

if __name__ == "__main__":
    video_url = input("Enter the YouTube video URL: ")
    video_path, original_url = download_video(video_url)
    describe_video(video_path, original_url)
