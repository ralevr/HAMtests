import http.server
import socketserver
import json
import os
import subprocess
import sys
import webbrowser

PORT = 8000
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QUESTIONS_PATH = os.path.join(BASE_DIR, 'class2', 'questions.json')

class QuizRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/questions':
            if os.path.exists(QUESTIONS_PATH):
                self.send_response(200)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.end_headers()
                with open(QUESTIONS_PATH, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, 'class2/questions.json not found')
        else:
            super().do_GET()

def main():
    os.chdir(BASE_DIR)
    if not os.path.exists(QUESTIONS_PATH):
        print("Executing question extraction first...")
        subprocess.run([sys.executable, os.path.join(BASE_DIR, 'extract_questions.py')], cwd=BASE_DIR, check=True)

    print(f"Starting Local Web Server at http://localhost:{PORT}")
    webbrowser.open(f'http://localhost:{PORT}')

    with socketserver.TCPServer(("", PORT), QuizRequestHandler) as httpd:
        print("Server running... Press Ctrl+C to stop.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")

if __name__ == '__main__':
    main()
