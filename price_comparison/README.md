# Medicine Price Comparison Tool

A web application that compares medicine prices across different pharmacies (Walmart, Costco, and RiteAid).

## Features

- Real-time price comparison
- Stock status checking
- Clean and responsive UI
- Support for multiple pharmacies

## Deployment Instructions

### Deploy to Render.com

1. Create a new account on [Render.com](https://render.com)
2. Click "New +" and select "Web Service"
3. Connect your GitHub repository
4. Configure the service:
   - Name: medicine-price-comparison
   - Environment: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Click "Create Web Service"

### Deploy to Heroku

1. Create a new account on [Heroku](https://heroku.com)
2. Install the Heroku CLI
3. Run these commands:
   ```bash
   heroku login
   heroku create medicine-price-comparison
   git push heroku main
   ```

## Local Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python main.py
   ```

3. Open http://localhost:8080 in your browser

## Environment Variables

No environment variables are required for basic functionality.

## License

MIT License 