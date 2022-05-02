SWAGGER_CDN_URLS = {
    "cdnjs": "https://cdnjs.cloudflare.com/ajax/libs/swagger-ui/<VERSION>/<FILENAME>",
    "unpkg": "https://unpkg.com/swagger-ui@<VERSION>/<FILENAME>",
    "staticfile": "https://cdn.jsdelivr.net/npm/swagger-ui@<VERSION>/dist/<FILENAME>",
}


def add_swagger_ui_cdn(name: str, url_with_placeholders: str):
    SWAGGER_CDN_URLS[name] = url_with_placeholders


def get_swagger_cdn_url(cdn_name: str, filename: str, version: str):
    url = SWAGGER_CDN_URLS.get(cdn_name)
    if url:
        url = url.replace("<VERSION>", version)
        url = url.replace("<FILENAME>", filename)
    return url


def apply_cdn_to_swagger_ui(page: str, swagger_cdn_name: str, version: str):
    page = page.replace(
        "__SWAGGER_CDN_URL__/swagger-ui.css",
        get_swagger_cdn_url(swagger_cdn_name, "swagger-ui.css", version),
    )
    page = page.replace(
        "__SWAGGER_CDN_URL__/swagger-ui-bundle.js",
        get_swagger_cdn_url(swagger_cdn_name, "swagger-ui-bundle.js", version),
    )
    page = page.replace(
        "__SWAGGER_CDN_URL__/swagger-ui-standalone-preset.js",
        get_swagger_cdn_url(
            swagger_cdn_name,
            "swagger-ui-standalone-preset.js",
            version,
        ),
    )
    return page
