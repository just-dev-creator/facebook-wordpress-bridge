# facebook-wordpress-bridge

A small Python script that reads posts from a Facebook Page and publishes them as WordPress posts. If a Facebook post contains images, they are uploaded to the WordPress media library first and can optionally be set as the featured image.


## Requirements

- Python 3.10+ recommended
- Access to the Facebook Graph API
- A WordPress installation with the REST API enabled
- A WordPress user with permission to create posts and upload media

## Installation

In the project directory:

```bash
python -m venv .venv
source .venv/bin/activate
pip install requests python-dotenv
```

## Configuration

Create a `.env` file in the project directory:

```env
FACEBOOK_AUTH_TOKEN=your_facebook_token
FACEBOOK_PAGE_ID=your_page_id
WORDPRESS_USERNAME=your_wp_username
WORDPRESS_PASSWORD=your_wp_password_or_app_password
WORDPRESS_URL=https://your-wordpress-domain.tld/
```

## Facebook post format

The script expects post text in this format:

```text
+++Title+++
Post content
```

If a post does not match this format, the script will skip it. 

## Running the script

```bash
python main.py
```


