"""
WSGI config for backend project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

application = get_wsgi_application()

# Self-pinger to keep Render free-tier instance awake when a SELF_PING_URL is provided.
# Configure with env vars: SELF_PING_URL (full URL) and SELF_PING_INTERVAL (seconds, default 300).
try:
	import threading
	import time
	import requests
	import os as _os

	def _start_self_pinger():
		url = _os.environ.get('SELF_PING_URL')
		if not url:
			return
		try:
			interval = int(_os.environ.get('SELF_PING_INTERVAL', '300'))
		except Exception:
			interval = 300

		def _pinger_loop():
			# initial delay to allow app to finish starting
			time.sleep(5)
			while True:
				try:
					print(f"[self-pinger] pinging {url}")
					requests.get(url, timeout=10)
				except Exception as e:
					print(f"[self-pinger] ping failed: {e}")
				time.sleep(interval)

		t = threading.Thread(target=_pinger_loop, name='self-pinger', daemon=True)
		t.start()

	_start_self_pinger()
except Exception:
	# If anything goes wrong importing or starting the pinger, don't crash the WSGI app.
	pass
