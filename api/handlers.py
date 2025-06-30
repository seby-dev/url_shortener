from datetime import datetime
from zoneinfo import ZoneInfo
from flask import Flask, request, jsonify, redirect

from service.url_generator import URLGeneratorService, AliasConflictError, InvalidURLError
from service.redirector import RedirectorService, NotFoundError, GoneError

app = Flask(__name__)

url_generator = URLGeneratorService()
redirector = RedirectorService()

@app.route('/shorten', methods=['POST'])
def shorten():
    """
      Request JSON:
        {
          "long_url": "https://example.com/very/long/path",
          "alias": "customAlias",          # optional
          "expires_at": "2025-07-01T12:00:00+00:00"  # optional ISO-8601 string
        }

      Responses:
        200: { "short_url": "http://your-domain/abc123" }
        400: { "error": "Invalid URL" }
        409: { "error": "Alias 'foo' already in use" }
        500: { "error": "Internal Server Error" }
    """

    data = request.get_json()
    if not data or 'long_url' not in data:
        return jsonify({'error': 'Missing required field: long_url'}), 400

    long_url = data['long_url']
    alias = data.get('alias')

    #parse expires_at if provided
    expires_dt = None
    expires_at = data.get('expires_at')
    if expires_at:
        try:
            expires_dt = datetime.fromisoformat(expires_at)
            if expires_dt.tzinfo is None:
                #enforce timezone awares
                return jsonify({'error': 'expires_at must include a timezone offset'}), 400
        except ValueError:
            return jsonify({'error': 'Invalid expires_at format; use ISO-8601 with offset'}),400


    try:
        short_url = url_generator.generate(
            long_url=long_url,
            custom_alias=alias,
            expires_at=expires_dt
        )
        return jsonify({'short_url': short_url}), 200

    except InvalidURLError as e:
        return jsonify({'error': str(e)}), 400

    except AliasConflictError as e:
        return jsonify({'error': str(e)}), 409

    except ValueError as e:
        return jsonify({'error': str(e)}), 400

    except Exception:
        return jsonify({'error': 'Internal Server Error'}), 500


@app.route('/<string:short_key>', methods=['GET'])
def redirect_short(short_key):
    """
      Redirects the client to the original URL.

      Responses:
        302 redirect → long_url
        404: { "error": "Not Found" }
        410: { "error": "Gone" }
        500: { "error": "Internal Server Error" }
      """
    try:
        long_url = redirector.redirect(short_key)
        return redirect(long_url, code=302)

    except NotFoundError:
        return jsonify({'error': 'Not Found'}), 404

    except GoneError:
        return jsonify({'error': 'Gone'}), 410

    except Exception:
        return jsonify({'error': 'Internal Server Error'}), 500







if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)











