import requests
from bs4 import BeautifulSoup

class WPDoesntUse(Exception):
    """Target site doesn't use wp error"""

class WPScanner:

    def __init__(self, site_url: str):
        self.vulnerability_path = ["wp-includes/uploads", "wp-includes/rest-api", "wp-includes", "wp-admin", "wp-upload", "wordpress/wp-content/uploads/"]
        self.session = requests.Session()
        self.site_url = site_url
        source = self.get_page_source()
        if not "wp-content" in source and not "wp-includes" in source and not "wp-includes" in source:
            raise WPDoesntUse("Maybe this site doesn't use WordPress.")

    def get_page_source(self):
        response = self.session.get(self.site_url).text
        self.soup = BeautifulSoup(response, 'html.parser')
        return response

    def get_wordpress_version(self):
        source = self.get_page_source()
        generator_tags = self.soup.find_all("meta", attrs={"name": "generator"})
        for generator in generator_tags:
            content = str(generator).split('"')[1]
            if "WordPress" in content:
                return content

    def get_all_plugins(self):
        plugin_list = []
        source = self.get_page_source()
        css_tags = self.soup.find_all("link")

        for tag in css_tags:
            tag = str(tag)
            if "wp-content/plugins/" in tag:
                name, version = tag.split("href=")[1].split('"')[1].split("/css/")[-1].split('.css?ver=')
                plugin_list.append({"name": name, "version": version})

        return plugin_list

    def get_all_themes(self):
        theme_list = []
        source = self.get_page_source()
        css_tags = self.soup.find_all("link")

        for tag in css_tags:
            tag = str(tag)
            if "theme" in tag:
                name = tag.split("href=")[1].split('"')[1].split("/css/")[-1]
                name, version = name.split('?ver=') if "?ver=" in name else [name, None]
                theme_list.append({"name": name, "version": version})

        return theme_list

    def get_vulnerability_page(self):
        vulnerability_page_list = []
        http = "https://" if "https://" in self.site_url else "http://"
        site_origin = http + self.site_url.replace(http, "").split("/")[0] + "/"
        for path in self.vulnerability_path:
            url = site_origin + path
            status = self.session.get(url).status_code
            if status == 302 or "20" in str(status):
                vulnerability_page_list.append(url)

        return vulnerability_page_list

    def get_all_users(self):
        user_list = []
        http = "https://" if "https://" in self.site_url else "http://"
        site_origin = http + self.site_url.replace(http, "").split("/")[0] + "/"
        url = site_origin + "wp-json/wp/v2/users"
        response = self.session.get(url)
        try:
            response_json = response.json()
            response.raise_for_status()
            for response in response_json:
                user_list.append(response["name"])
        except requests.HTTPError:
            return None

        return user_list
