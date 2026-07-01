import os

import requests
from dotenv import load_dotenv

load_dotenv()

facebook_auth_token = os.environ["FACEBOOK_AUTH_TOKEN"]
facebook_page_id = os.environ["FACEBOOK_PAGE_ID"]

facebook_api_url = "https://graph.facebook.com/v25.0"

wordpress_username = os.environ["WORDPRESS_USERNAME"]
wordpress_password = os.environ["WORDPRESS_PASSWORD"]
wordpress_base_url = os.environ["WORDPRESS_URL"]

post_min_date = os.environ.get("POST_MIN_DATE", None) # YYYY-MM-DD

def publish_wordpress_post(title, text, date: str, featured_image_id=None):
    date = date.split("+")[0]
    r = requests.post(f"{wordpress_base_url}wp-json/wp/v2/posts",
                      json={
                          "date": date,
                          "status": "draft",
                          "title": title,
                          "content": text,
                          "featured_media": featured_image_id
                      }, auth=(wordpress_username, wordpress_password),
                      headers={
                        "Content-Type": "application/json",
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.3"
                      })
    print(f"Published post {title} with status code {r.status_code}")

def upload_media_to_wordpress(media_url: str):
    media_response = requests.get(media_url)
    media_filename = media_url.split("/")[-1].split("?")[0]
    media_upload_response = requests.post(f"{wordpress_base_url}wp-json/wp/v2/media",
                                          headers={
                                              "Content-Disposition": f'attachment; filename="{media_filename}"',
                                              "Content-Type": media_response.headers["Content-Type"],
                                              "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.3"
                                          },
                                          data=media_response.content,
                                          auth=(wordpress_username, wordpress_password)
                                          )
    media_upload_response_json = media_upload_response.json()
    if "id" in media_upload_response_json:
        media_id = media_upload_response_json["id"]
        media_url = media_upload_response_json["guid"]["rendered"]

        return {
            "id": media_id,
            "url": media_url,
            "filename": media_filename
        }
    else:
        print(f"Failed to upload media: {media_upload_response.text}")
        return None

# Get page access token

r = requests.get(f"{facebook_api_url}/me/accounts?access_token={facebook_auth_token}")
page_access_token = r.json()["data"][0]["access_token"]

print("Received page access token")


# Get page posts
r = requests.get(f"{facebook_api_url}/{facebook_page_id}/feed?fields=attachments,created_time,id,message&access_token={page_access_token}")
posts = r.json()["data"]

published_posts = []

with open("published_posts.txt") as f:
    for line in f.readlines():
        published_posts.append(line.replace("\n", ""))

if not posts:
    print("No posts found")
    exit(-1)

for post in posts:
    post_id: str = post["id"]
    post_date_str: str = post["created_time"]

    if post_id in published_posts:
        continue

    if post_min_date and post_date_str.split("T")[0] < post_min_date:
        with open("published_posts.txt", "a") as f:
            f.writelines(post_id + "\n")
        print(f"Post {post_id} is older than min date, skipping")
        continue

    if not "message" in post:
        with open("published_posts.txt", "a") as f:
            f.writelines(post["id"] + "\n")
        print(f"Post {post['id']} has no message, skipping")
        continue

    post_text: str = post["message"]

    bpost_title = bpost_text = None

    print(post_text)

    post_text_parts = post_text.split("+++")
    if not len(post_text_parts) >= 3:
        post_text_parts = post_text.split("\n")
        print(post_text_parts)
        if len(post_text_parts) >= 2:
            bpost_title=post_text_parts[0]
            bpost_text="\n".join(post_text_parts[1:]).lstrip('\r\n')
    else:
        bpost_title = post_text_parts[1]
        bpost_text = post_text_parts[2].lstrip('\r\n')

    if not bpost_title or not bpost_text:
        with open("published_posts.txt", "a") as f:
            f.writelines(post_id + "\n")
        print(f"Post {post_id} is missing title or text, skipping")
        continue

    bpost_featured_image_id = None

    if "attachments" in post:
        attachments = post["attachments"]["data"]

        if "subattachments" in attachments[0]:
            attachments = attachments[0]["subattachments"]["data"]

        print(attachments)

        for attachment in attachments:
            if "media" in attachment:
                media_url = attachment["media"]["image"]["src"]
                if attachment["type"] == "video":
                    video_url = attachment["media"]["source"]

                    video_upload = upload_media_to_wordpress(video_url)
                    if not video_upload:
                        print(f"Failed to upload video: {video_url}")
                    else:
                        bpost_text += f'\n\n<video controls style="max-width:100%; height:auto;"><source src="{video_upload["url"]}" type="video/mp4"></video>'

                media_upload = upload_media_to_wordpress(media_url)

                if not media_upload:
                    print(f"Failed to upload media: {media_url}")
                    continue

                if not bpost_featured_image_id:
                    bpost_featured_image_id = media_upload["id"]

                bpost_text += f'\n\n<img src="{media_upload["url"]}" alt="{media_upload["filename"]}" />'

    publish_wordpress_post(bpost_title, bpost_text, post_date_str, bpost_featured_image_id)

    with open("published_posts.txt", "a") as f:
        f.writelines(post_id + "\n")
        print(f"Added {post_id} ({bpost_title}) to list")