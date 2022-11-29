# Parasitoscope 
Data collection application for AI Assisted Microscopy for automated detection of Diarrhea Parasites

Link to site: [Parasitoscope Application](https://sitoscope.naamii.org.np)

## How to run the application?
### **Create virtual environment**

`python3 -m venv .venv`
`source .venv/bin/activate`

### **Install dependencies**

`pip install -r requirements.txt`

### **Database migration**

Run database migrations.

`python manage.py migrate`

### **Run server**

`sh runserver.sh`

## WARNING
This application uses `django-pwa` as a dependency which has issues running in `Django v.4.0`, so we need to change the `urls.py` file inside the `.venv/lib/python3.10/site-packages/pwa/` folder by replacing the file contents of `urls.py` with the code below.

```python
from django.urls import path

from .views import manifest, offline, service_worker

# Serve up serviceworker.js and manifest.json at the root
urlpatterns = [
    path("serviceworker.js", service_worker, name="serviceworker"),
    path("manifest.json", manifest, name="manifest"),
    path("offline/", offline, name="offline"),
]
```