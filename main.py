from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def home():
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome Fadi</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .card {
            background: white;
            border-radius: 20px;
            padding: 60px;
            text-align: center;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 600px;
            width: 90%;
        }

        .emoji { font-size: 80px; margin-bottom: 20px; }

        h1 {
            font-size: 2.5em;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }

        .subtitle {
            font-size: 1.2em;
            color: #666;
            margin-bottom: 40px;
        }

        .badges {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            justify-content: center;
            margin-bottom: 40px;
        }

        .badge {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            padding: 8px 20px;
            border-radius: 50px;
            font-size: 0.9em;
            font-weight: 600;
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin-bottom: 40px;
        }

        .stat {
            background: #f8f9ff;
            border-radius: 15px;
            padding: 20px;
        }

        .stat-number {
            font-size: 2em;
            font-weight: 700;
            color: #667eea;
        }

        .stat-label {
            font-size: 0.8em;
            color: #999;
            margin-top: 5px;
        }

        .footer {
            color: #999;
            font-size: 0.85em;
        }

        .pulse {
            display: inline-block;
            width: 10px;
            height: 10px;
            background: #4CAF50;
            border-radius: 50%;
            margin-right: 8px;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0% { box-shadow: 0 0 0 0 rgba(76,175,80,0.4); }
            70% { box-shadow: 0 0 0 10px rgba(76,175,80,0); }
            100% { box-shadow: 0 0 0 0 rgba(76,175,80,0); }
        }
    </style>
</head>
<body>
    <div class="card">
        <div class="emoji">🚀</div>
        <h1>Welcome Fadi!</h1>
        <p class="subtitle">Mastering CI/CD Flow with GCP</p>

        <div class="badges">
            <span class="badge">✅ GitHub Actions</span>
            <span class="badge">✅ Terraform</span>
            <span class="badge">✅ App Engine</span>
            <span class="badge">✅ Workload Identity</span>
            <span class="badge">✅ CI/CD Pipeline</span>
        </div>

        <div class="stats">
            <div class="stat">
                <div class="stat-number">100%</div>
                <div class="stat-label">Automated Deploy</div>
            </div>
            <div class="stat">
                <div class="stat-number">0</div>
                <div class="stat-label">Manual Steps</div>
            </div>
            <div class="stat">
                <div class="stat-number">∞</div>
                <div class="stat-label">Possibilities</div>
            </div>
        </div>

        <div class="footer">
            <span class="pulse"></span>
            Live on Google Cloud App Engine • Production
        </div>
    </div>
</body>
</html>
'''

@app.route('/health')
def health():
    return {'status': 'healthy'}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=True)