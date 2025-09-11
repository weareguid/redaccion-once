# 🚀 Streamlit Cloud Deployment Guide

## 📋 Prerequisites

1. **GitHub Repository**: Your code should be in a GitHub repository
2. **OpenAI API Key**: Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys)
3. **Streamlit Cloud Account**: Sign up at [share.streamlit.io](https://share.streamlit.io)

## 🔧 Setup Steps

### 1. Prepare Your Repository

Make sure your repository has these files:
- `app_cloud.py` (main app file)
- `requirements_cloud.txt` (dependencies)
- `.streamlit/config.toml` (Streamlit configuration)
- `training_data.jsonl` (optional, for examples)

### 2. Deploy to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Connect your GitHub repository
4. Select the repository and branch
5. Set the main file path to `app_cloud.py`
6. Click "Deploy!"

### 3. Configure Secrets

In the Streamlit Cloud dashboard:

1. Go to your app's settings
2. Click "Secrets"
3. Add the following secrets:

```toml
[OPENAI]
api_key = "your-actual-openai-api-key-here"
```

### 4. Environment Variables (Alternative)

You can also set environment variables in the Streamlit Cloud settings:
- `OPENAI_API_KEY`: Your OpenAI API key

## 📁 File Structure

```
your-repo/
├── app_cloud.py              # Main application
├── requirements_cloud.txt    # Dependencies
├── .streamlit/
│   ├── config.toml          # Streamlit configuration
│   └── secrets.toml         # Local secrets (not used in cloud)
├── training_data.jsonl      # Training examples (optional)
└── README_DEPLOYMENT.md     # This file
```

## 🔑 Required Secrets

### For Streamlit Cloud:
- `OPENAI_API_KEY`: Your OpenAI API key

### For Local Development:
Update `.streamlit/secrets.toml` with your actual API key.

## 🚀 Features

- ✅ Content generation with OpenAI GPT-4
- ✅ Multiple text types and categories
- ✅ Word and PDF export
- ✅ Feedback system with SQLite storage
- ✅ Responsive design
- ✅ Error handling and validation

## 🐛 Troubleshooting

### Common Issues:

1. **"No secrets files found"**
   - Make sure you've added secrets in Streamlit Cloud dashboard
   - Check that the secret names match exactly

2. **"OpenAI API key not configured"**
   - Verify your API key is correct
   - Check that it has sufficient credits

3. **Import errors**
   - Make sure all dependencies are in `requirements_cloud.txt`
   - Check that package versions are compatible

### Local Testing:

To test locally before deploying:

```bash
# Install dependencies
pip install -r requirements_cloud.txt

# Update secrets.toml with your API key
# Then run:
streamlit run app_cloud.py
```

## 📞 Support

If you encounter issues:
1. Check the Streamlit Cloud logs
2. Verify your API key and secrets
3. Test locally first
4. Check the [Streamlit documentation](https://docs.streamlit.io)

## 🔄 Updates

To update your deployed app:
1. Push changes to your GitHub repository
2. Streamlit Cloud will automatically redeploy
3. Check the deployment status in the dashboard
