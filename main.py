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

def publish_wordpress_post(title, text, date: str, featured_image_id=None):
    date = date.split("+")[0]
    r = requests.post(f"{wordpress_base_url}wp-json/wp/v2/posts",
                      {
                          "date": date,
                          "status": "publish",
                          "title": title,
                          "content": text,
                          "featured_media": featured_image_id
                      }, auth=(wordpress_username, wordpress_password))
    print(r.text)

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
    post_text: str = post["message"]
    post_id: str = post["id"]
    post_date_str: str = post["created_time"]

    if post_id in published_posts:
        continue

    post_text_parts = post_text.split("+++")
    bpost_title = post_text_parts[1]
    bpost_text = post_text_parts[2]

    bpost_featured_image_id = None

    if "attachments" in post:
        attachments = post["attachments"]["data"]

        if "subattachments" in attachments[0]:
            attachments = attachments[0]["subattachments"]["data"]

        for attachment in attachments:
            print("im here")
            if "media" in attachment:
                media_url = attachment["media"]["image"]["src"]

                # Download the image and upload it to WordPress
                media_response = requests.get(media_url)


                media_filename = media_url.split("/")[-1].split("?")[0]

                media_upload_response = requests.post(f"{wordpress_base_url}wp-json/wp/v2/media",
                    headers={
                        "Content-Disposition": f'attachment; filename="{media_filename}"',
                        "Content-Type": media_response.headers["Content-Type"]
                    },
                    data=media_response.content,
                    auth=(wordpress_username, wordpress_password)
                )
                media_upload_response_json = media_upload_response.json()

                print(media_upload_response_json)

                if "id" in media_upload_response_json:
                    media_id = media_upload_response_json["id"]
                    # Add WordPress media url to post text
                    bpost_text += f'\n\n<img src="{media_upload_response_json["guid"]["rendered"]}" alt="{media_filename}" />'
                    if not bpost_featured_image_id:
                        bpost_featured_image_id = media_id
                else:
                    print(f"Failed to upload media: {media_upload_response.text}")

    publish_wordpress_post(bpost_title, bpost_text, post_date_str, bpost_featured_image_id)

    with open("published_posts.txt", "a") as f:
        f.writelines(post_id + "\n")
        print(f"Added {post_id} ({bpost_title}) to list")