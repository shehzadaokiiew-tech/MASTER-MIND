# 🚀 Facebook Automation Tool

A powerful, fully functional Facebook automation tool with a VIP dark theme interface built using Streamlit and Selenium. This tool enables automated messaging to Facebook threads using cookie-based authentication.

## ✨ Features

### 🎨 VIP Dark Theme Interface
- **Dark console** with bright green terminal-style logs
- **Glowing input boxes** with red/blue border animations
- **Elegant animations** and smooth transitions
- **Real-time Pakistan time** display
- **Live task tracking** with unique task IDs
- **Scrollable console** with color-coded logs

### 🤖 Automation Capabilities
- **Cookie-based Facebook login** (no Graph API required)
- **Multiple cookie support** for session management
- **Automated message sending** to specific threads/chats
- **Custom message formatting** with prefix and suffix
- **Configurable time delays** between messages
- **Error handling and retry logic**
- **Real-time status updates** and message counting

### 🛠️ Technical Features
- **Modular architecture** with separate GUI and backend
- **Thread-safe operations** for responsive interface
- **Cross-platform compatibility** (Windows, Linux, Termux)
- **Browser automation** using Selenium + Chrome WebDriver
- **Live log streaming** with timestamps and task tracking

## 📋 Requirements

- Python 3.7 or higher
- Google Chrome browser
- Internet connection

## 🚀 Installation

### Option 1: Standard Installation (Windows/Linux/macOS)

1. **Clone or download the files**
   ```bash
   # Extract all files to a folder named "facebook-automation"
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   streamlit run facebook_automation.py
   ```

### Option 2: Termux Installation (Android)

1. **Install Termux from F-Droid** (not Play Store)

2. **Update and install required packages**
   ```bash
   pkg update && pkg upgrade
   pkg install python python-pip git
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download and setup Chrome**
   ```bash
   # For Termux, you may need to install chromium
   pkg install chromium
   export CHROME_BIN=/usr/bin/chromium
   ```

5. **Run the application**
   ```bash
   streamlit run facebook_automation.py
   ```

## 📖 Usage Guide

### 1. Getting Facebook Cookies

#### Method 1: Browser Developer Tools
1. Open Facebook in your browser
2. Press `F12` to open Developer Tools
3. Go to `Application` > `Cookies` > `https://www.facebook.com`
4. Copy all cookies (right-click > "Copy All")
5. Paste into the tool's cookies field

#### Method 2: Browser Extension
1. Install "Cookie Editor" extension
2. Go to Facebook
3. Open the extension and export cookies
4. Paste into the tool

### 2. Finding Thread/Chat UID

#### Method 1: From URL
1. Open the Facebook conversation
2. Look at the URL: `https://www.facebook.com/messages/t/UIDHERE`
3. Copy the UID part

#### Method 2: From Page Source
1. Open the conversation
2. Right-click > "View Page Source"
3. Search for `thread_id` or `user_id`
4. Extract the UID

### 3. Preparing Message File

Create a `.txt` file with one message per line:
```
Hello, this is message 1
This is the second message
Final message here
```

### 4. Running the Automation

1. **Paste cookies** in the cookies field
2. **Enter Thread UID** of target conversation
3. **Optional: Add prefix/suffix** for message formatting
4. **Set delay time** (seconds between messages)
5. **Upload message file** (.txt format)
6. **Click "START AUTOMATION"**
7. **Monitor console** for live updates
8. **Use "STOP"** to stop anytime

## 🎯 Configuration Options

### Cookie Input
- **Single cookie**: Works with one Facebook account
- **Multiple cookies**: Supports multiple accounts (separated by `c_user` parameter)
- **Auto-detection**: Tool automatically detects single vs multiple cookies

### Message Formatting
- **Prefix**: Text added before each message
- **Suffix**: Text added after each message
- **Example**: Prefix "👋 " + Message "Hello" + Suffix " 😊" = "👋 Hello 😊"

### Time Delay
- **Range**: 1-300 seconds
- **Purpose**: Prevents detection and spam filters
- **Recommendation**: 5-10 seconds for safe automation

## 🔧 Troubleshooting

### Common Issues

#### 1. "Login failed with cookies"
- **Solution**: Check if cookies are valid and not expired
- **Cause**: Cookies expire after certain time

#### 2. "Could not find message box"
- **Solution**: Verify Thread UID is correct
- **Cause**: Invalid or inaccessible conversation

#### 3. WebDriver errors
- **Solution**: Update Chrome browser and WebDriver
- **Command**: `pip install --upgrade webdriver-manager`

#### 4. "Access denied" in Termux
- **Solution**: Install proper Chrome/Chromium
- **Command**: `pkg install chromium`

### Debug Mode
- Check console logs for detailed error messages
- Each log shows: [Timestamp] [Task ID] [Message Count] [Message]

## 🌐 Hosting Platforms

This tool can be hosted on platforms that support:
- Python 3.7+
- Selenium
- Chrome WebDriver
- Streamlit

### Recommended Platforms
1. **Streamlit Community Cloud** (Free)
2. **Heroku** (with proper buildpacks)
3. **PythonAnywhere** (paid tiers)
4. **Railway** (with custom Dockerfile)

### Docker Deployment
```dockerfile
FROM python:3.9-slim

# Install Chrome
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "facebook_automation.py"]
```

## ⚠️ Important Notes

### Safety and Compliance
- **Use responsibly** and respect Facebook's Terms of Service
- **Don't spam** - use reasonable delays between messages
- **Test with small batches** first
- **Monitor your account** for any warnings

### Technical Considerations
- **Cookies expire** and need to be refreshed periodically
- **Facebook may change** their interface, requiring updates
- **Rate limiting** can trigger temporary restrictions
- **Multiple accounts** increases detection risk

### Legal Disclaimer
This tool is for educational purposes only. Users are responsible for complying with:
- Facebook's Terms of Service
- Local laws regarding automated messaging
- Privacy and data protection regulations

## 🔄 Updates and Maintenance

### Regular Updates
- **WebDriver**: Chrome updates may require WebDriver updates
- **Selenium**: Keep updated for latest browser compatibility
- **Facebook selectors**: UI changes may require selector updates

### Customization
The tool is designed with modular architecture:
- **GUI styling**: Modify `VIP_CSS` in the code
- **Backend logic**: Update automation functions independently
- **Error handling**: Add custom retry logic as needed

## 📞 Support

For issues and questions:
1. Check the console logs for detailed error messages
2. Verify all inputs are correct (cookies, UID, message file)
3. Ensure Chrome browser is updated
4. Test with small message batches first

---

**⚡ Powered by Selenium + Streamlit | 🎨 VIP Dark Theme Design**