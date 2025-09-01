# Unified Upload Endpoint Examples

This document shows how to use the unified upload endpoint for both files and URLs.

## Endpoint
```
POST /api/v1/data/Upload/{Project_id}
```

## File Upload Examples

### 1. Upload a PDF File
```bash
curl -X POST "http://localhost:8000/api/v1/data/Upload/myproject" \
  -F "file=@document.pdf"
```

### 2. Upload a Text File
```bash
curl -X POST "http://localhost:8000/api/v1/data/Upload/myproject" \
  -F "file=@notes.txt"
```

### 3. Upload an Excel File
```bash
curl -X POST "http://localhost:8000/api/v1/data/Upload/myproject" \
  -F "file=@data.xlsx"
```

## URL Upload Examples

### 1. Upload a Simple URL
```bash
curl -X POST "http://localhost:8000/api/v1/data/Upload/myproject" \
  -F "url=https://example.com"
```

### 2. Upload URL with Custom Chunking
```bash
curl -X POST "http://localhost:8000/api/v1/data/Upload/myproject" \
  -F "url=https://example.com" \
  -F "chunk_size=200" \
  -F "chunk_overlap=50"
```

### 3. Upload Multiple URLs (separate requests)
```bash
# First URL
curl -X POST "http://localhost:8000/api/v1/data/Upload/myproject" \
  -F "url=https://docs.example.com/api"

# Second URL  
curl -X POST "http://localhost:8000/api/v1/data/Upload/myproject" \
  -F "url=https://blog.example.com/tutorial"
```

## Python Examples

### File Upload with Python
```python
import requests

url = "http://localhost:8000/api/v1/data/Upload/myproject"

# Upload a file
with open("document.pdf", "rb") as f:
    files = {"file": f}
    response = requests.post(url, files=files)
    print(response.json())
```

### URL Upload with Python
```python
import requests

url = "http://localhost:8000/api/v1/data/Upload/myproject"

# Upload a URL
data = {
    "url": "https://example.com",
    "chunk_size": 150,
    "chunk_overlap": 30
}

response = requests.post(url, data=data)
print(response.json())
```

### Combined Upload Function
```python
import requests
from typing import Optional

def upload_to_project(project_id: str, file_path: Optional[str] = None, 
                     url: Optional[str] = None, chunk_size: int = 100, 
                     chunk_overlap: int = 20):
    """
    Unified upload function that handles both files and URLs
    """
    base_url = f"http://localhost:8000/api/v1/data/Upload/{project_id}"
    
    if file_path:
        # File upload
        with open(file_path, "rb") as f:
            files = {"file": f}
            response = requests.post(base_url, files=files)
    elif url:
        # URL upload
        data = {
            "url": url,
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap
        }
        response = requests.post(base_url, data=data)
    else:
        raise ValueError("Either file_path or url must be provided")
    
    return response.json()

# Usage examples
if __name__ == "__main__":
    # Upload a file
    result = upload_to_project("myproject", file_path="document.pdf")
    print("File upload result:", result)
    
    # Upload a URL
    result = upload_to_project("myproject", url="https://example.com")
    print("URL upload result:", result)
```

## JavaScript/Node.js Examples

### File Upload
```javascript
const FormData = require('form-data');
const fs = require('fs');
const axios = require('axios');

async function uploadFile(projectId, filePath) {
    const form = new FormData();
    form.append('file', fs.createReadStream(filePath));
    
    const response = await axios.post(
        `http://localhost:8000/api/v1/data/Upload/${projectId}`,
        form,
        {
            headers: form.getHeaders()
        }
    );
    
    return response.data;
}

// Usage
uploadFile('myproject', './document.pdf')
    .then(result => console.log('Upload successful:', result))
    .catch(error => console.error('Upload failed:', error));
```

### URL Upload
```javascript
const axios = require('axios');

async function uploadUrl(projectId, url, chunkSize = 100, chunkOverlap = 20) {
    const formData = new FormData();
    formData.append('url', url);
    formData.append('chunk_size', chunkSize);
    formData.append('chunk_overlap', chunkOverlap);
    
    const response = await axios.post(
        `http://localhost:8000/api/v1/data/Upload/${projectId}`,
        formData,
        {
            headers: formData.getHeaders()
        }
    );
    
    return response.data;
}

// Usage
uploadUrl('myproject', 'https://example.com')
    .then(result => console.log('URL upload successful:', result))
    .catch(error => console.error('URL upload failed:', error));
```

## Response Format

### File Upload Response
```json
{
    "Result": "File uploaded successfully",
    "File ID": "507f1f77bcf86cd799439011",
    "Type": "file",
    "Filename": "document.pdf"
}
```

### URL Upload Response
```json
{
    "Result": "URL processed successfully",
    "URL ID": "507f1f77bcf86cd799439012",
    "Chunks Created": 15,
    "URL": "https://example.com",
    "Type": "url"
}
```

## Error Responses

### Missing Input
```json
{
    "error": "Either a file or URL must be provided"
}
```

### Invalid URL
```json
{
    "error": "Invalid URL format"
}
```

### File Too Large
```json
{
    "error": "File size limit exceeded"
}
```

## Notes

- **File uploads**: Files are saved locally and need to be processed separately using the `/process` endpoint
- **URL uploads**: Content is processed immediately and chunks are stored directly in the database
- **Chunking parameters**: Only apply to URL uploads; file uploads use default processing parameters
- **Project creation**: Projects are created automatically if they don't exist
- **Asset tracking**: Both files and URLs are tracked as assets in the system
