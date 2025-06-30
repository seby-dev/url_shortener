# URL Shortener

A simple, efficient URL shortening service built with Python and Flask. This service allows you to create shortened URLs from long ones, with optional custom aliases and expiration dates.

## Features

- Shorten long URLs to concise, easy-to-share links
- Create custom aliases for your shortened URLs
- Set expiration dates for temporary links
- RESTful API for programmatic access
- Comprehensive error handling
- Detailed API documentation

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/url_shortener.git
   cd url_shortener
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Starting the Server

Run the Flask application:

```bash
python -m api.handlers
```

The server will start on `http://localhost:5000` by default.

### API Endpoints

#### Shorten a URL

```bash
curl -X POST http://localhost:5000/shorten \
  -H "Content-Type: application/json" \
  -d '{
    "long_url": "https://example.com/very/long/path",
    "alias": "example",
    "expires_at": "2025-07-01T12:00:00+00:00"
  }'
```

Response:
```json
{
  "short_url": "http://localhost:5000/example"
}
```

#### Access a Shortened URL

Simply visit the shortened URL in your browser, or use:

```bash
curl -i http://localhost:5000/example
```

This will redirect to the original URL.

#### View API Documentation

Access the full API documentation by visiting:

```
http://localhost:5000/docs
```

## Project Structure

```
url_shortener/
├── api/                  # API layer
│   ├── __init__.py
│   └── handlers.py       # Flask routes and request handling
├── model/                # Data models
│   ├── __init__.py
│   └── url_mapping.py    # URL mapping model
├── repository/           # Data access layer
│   ├── __init__.py
│   └── db_repo.py        # Database operations
├── service/              # Business logic
│   ├── __init__.py
│   ├── redirector.py     # URL redirection service
│   └── url_generator.py  # URL generation service
├── tests/                # Test suite
│   ├── __init__.py
│   ├── test_db_repo.py
│   ├── test_handlers.py
│   ├── test_redirector.py
│   ├── test_url_generator.py
│   └── test_url_mapping.py
├── util/                 # Utilities
│   ├── __init__.py
│   ├── base62.py         # Base62 encoding for short URLs
│   └── config.py         # Configuration settings
├── API.md                # API documentation
└── README.md             # Project documentation
```

## Testing

Run the test suite with pytest:

```bash
pytest
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.