import os
from openai import OpenAI
from core.logger import logger

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_summary(content: str, model: str = 'gpt-3.5-turbo', max_token: int = 512):
    logger.info(f"Generating summary using {model}...")

    try:
        response = openai_client.chat.completions.create(
            model=model,
            max_tokens=max_token,
            messages=[
                {"role": "system", "content": "You are a financial news summarizer."},
                {"role": "user", "content":  f"Summarize the following article in concise financial terms:\n\n{content}"}
            ]
        )

        summary = response.choices[0].message.content.strip()
        logger.info("Summary generated")
        return summary
    except Exception as e:
        logger.error(f"Error generating summary: {str(e)}")
        return ""
    
if __name__ == '__main__':
    summary = generate_summary("""
Manually Install the Required Chromium Version:

If Playwright is attempting to download a specific Chromium build that is unavailable, you can manually download and install the required version:

Identify the Required Chromium Version: Check the Playwright version you're using and identify the corresponding Chromium version it requires. This information can be found in the Playwright documentation or release notes.

Download the Chromium Build: Navigate to the official Chromium builds repository and download the appropriate build for your operating system.

Configure Playwright to Use the Manually Installed Chromium: Set the PLAYWRIGHT_BROWSERS_PATH environment variable to the path where you've installed Chromium. This directs Playwright to use the specified browser instead of attempting to download it.

Check for Proxy or Firewall Restrictions:

If you're behind a proxy or firewall, it might be blocking Playwright's download requests. Configure the necessary proxy settings or consult with your network administrator to ensure that the required URLs are accessible.

Ensure Sufficient Disk Space and Permissions:

Verify that your system has adequate disk space and that you have the necessary permissions to download and install software. Insufficient space or permissions can cause download failures.
""")
    print(summary)