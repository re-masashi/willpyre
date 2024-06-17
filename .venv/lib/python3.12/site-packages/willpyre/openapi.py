from .structure import HTMLResponse
import json

# TODO: Clean up the HTML part. Too messy.


def get_swagger_ui_html(  # pragma: no cover
    openapi_url: str,
    title: str,
    swagger_js_url: str = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@4/swagger-ui-bundle.js",
    swagger_css_url: str = "https://cdn.jsdelivr.net/npm/swagger-ui-dist@4/swagger-ui.css",
    swagger_favicon_url: str = "/favicon.ico",
    oauth2_redirect_url=None,
    init_oauth=None,
    swagger_params=None,
    swagger_presets: list = [],
) -> HTMLResponse:  # pragma: no cover
    current_swagger_ui_parameters = {
        "dom_id": "#swagger-ui",
        "layout": "BaseLayout",
        "deepLinking": True,
        "showExtensions": True,
        "showCommonExtensions": True,
    }

    if swagger_params:
        current_swagger_ui_parameters.update(swagger_params)

    html = f"""
    <!DOCTYPE html>
    <html>
        <head>
            <link type="text/css" rel="stylesheet" href="{swagger_css_url}">
            <link rel="shortcut icon" href="{swagger_favicon_url}">
            <title>{title}</title>
        </head>
        <body>
            <div id="swagger-ui">
            </div>
            <script src="{swagger_js_url}"></script>
    <script>
    // Local modifications from here
    const ui = SwaggerUIBundle({{
        url: '{openapi_url}',
    """

    for key, value in current_swagger_ui_parameters.items():
        html += f"{json.dumps(key)}: {json.dumps(value)},\n"

    if oauth2_redirect_url:
        html += f"oauth2RedirectUrl: window.location.origin + '{oauth2_redirect_url}',"

    html += """
    presets: [
        SwaggerUIBundle.presets.apis,
        SwaggerUIBundle.SwaggerUIStandalonePreset,
    """
    for preset in swagger_presets:
        html += preset + ",\n"

    html += """]
    })
    </script>
    </body>
    </html>
    """

    if init_oauth:
        html += f"""
        ui.initOAuth({json.dumps(init_oauth)})
        """

    html += """
    </script>
    </body>
    </html>
    """
    return HTMLResponse(html)


def get_swagger_ui_oauth2_redirect_html() -> HTMLResponse:  # pragma: no cover
    # https://github.com/swagger-api/swagger-ui/blob/v4.18.0/dist/oauth2-redirect.html
    html = """
    <!doctype html>
    <html lang="en-US">
    <head>
        <title>Swagger UI: OAuth2 Redirect</title>
    </head>
    <body>
    <script>
        'use strict';
        function run () {
            var oauth2 = window.opener.swaggerUIRedirectOauth2;
            var sentState = oauth2.state;
            var redirectUrl = oauth2.redirectUrl;
            var isValid, qp, arr;

            if (/code|token|error/.test(window.location.hash)) {
                qp = window.location.hash.substring(1).replace('?', '&');
            } else {
                qp = location.search.substring(1);
            }

            arr = qp.split("&");
            arr.forEach(function (v,i,_arr) { _arr[i] = '"' + v.replace('=', '":"') + '"';});
            qp = qp ? JSON.parse('{' + arr.join() + '}',
                    function (key, value) {
                        return key === "" ? value : decodeURIComponent(value);
                    }
            ) : {};

            isValid = qp.state === sentState;

            if ((
              oauth2.auth.schema.get("flow") === "accessCode" ||
              oauth2.auth.schema.get("flow") === "authorizationCode" ||
              oauth2.auth.schema.get("flow") === "authorization_code"
            ) && !oauth2.auth.code) {
                if (!isValid) {
                    oauth2.errCb({
                        authId: oauth2.auth.name,
                        source: "auth",
                        level: "warning",
                        message: "Authorization may be unsafe, passed state was changed in server. The passed state wasn't returned from auth server."
                    });
                }

                if (qp.code) {
                    delete oauth2.state;
                    oauth2.auth.code = qp.code;
                    oauth2.callback({auth: oauth2.auth, redirectUrl: redirectUrl});
                } else {
                    let oauthErrorMsg;
                    if (qp.error) {
                        oauthErrorMsg = "["+qp.error+"]: " +
                            (qp.error_description ? qp.error_description+ ". " : "no accessCode received from the server. ") +
                            (qp.error_uri ? "More info: "+qp.error_uri : "");
                    }

                    oauth2.errCb({
                        authId: oauth2.auth.name,
                        source: "auth",
                        level: "error",
                        message: oauthErrorMsg || "[Authorization failed]: no accessCode received from the server."
                    });
                }
            } else {
                oauth2.callback({auth: oauth2.auth, token: qp, isValid: isValid, redirectUrl: redirectUrl});
            }
            window.close();
        }

        if (document.readyState !== 'loading') {
            run();
        } else {
            document.addEventListener('DOMContentLoaded', function () {
                run();
            });
        }
    </script>
    </body>
    </html>
    """
    return HTMLResponse(data=html)


def gen_openapi_schema(  # pragma: no cover
    title,
    version,
    openapi_version,
    description,
    terms_of_service,
    contact,
    license,
    routes,
    tags,
    host,
    paths,
    definitions,
    **kwargs,
) -> dict:  # pragma: no cover
    schema = {}
    info = {
        "title": title,
        "version": version,
    }
    if description:
        info["description"] = description
    if terms_of_service:
        info["termsOfService"] = terms_of_service
    if contact:
        info["contact"] = contact
    if license:
        info["license"] = license

    if description:
        schema["description"] = description
    if host:
        schema["host"] = host

    schema["swagger"] = "2.0"

    schema["paths"] = paths
    schema["info"] = info
    schema["version"] = version
    if openapi_version == "2.0":
        schema["definitions"] = definitions
    else:
        schema["components"] = {"schemas": definitions}

    return schema


def schema(cls):  # pragma: no cover
    """
    Intended to be used as a decorator.
    @schema
    class Item:
        itemid: int
        name: str
        seller: Seller # another schema
    """
    pass
