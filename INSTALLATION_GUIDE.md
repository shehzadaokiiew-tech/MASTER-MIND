# 📋 Quick Installation Guide

## 🚀 Windows Users

1. **Download and extract** all files to a folder
2. **Double-click `run.bat`** - it will automatically:
   - Check Python installation
   - Install all dependencies
   - Start the application

## 🐧 Linux Users

1. **Extract all files** to a folder
2. **Open terminal** in that folder
3. **Run the script:**
   ```bash
   ./run.sh
   ```

## 📱 Termux (Android) Users

1. **Install Termux** from F-Droid
2. **Extract files** to Termux home directory
3. **Install packages:**
   ```bash
   pkg update && pkg upgrade
   pkg install python python-pip chromium git
   ```
4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
5. **Set Chrome path:**
   ```bash
   export CHROME_BIN=/usr/bin/chromium
   ```
6. **Run the app:**
   ```bash
   streamlit run facebook_automation.py
   ```

## 🐳 Docker Users

1. **Extract files** to a folder
2. **Run with Docker:**
   ```bash
   docker-compose up --build
   ```
3. **Access at:** http://localhost:8501

## 📋 Prerequisites

- **Python 3.7+** (except Docker)
- **Google Chrome** (except Docker)
- **Internet connection**

## ⚡ Quick Start

1. Open the tool in your browser (usually http://localhost:8501)
2. Get Facebook cookies (see README.md)
3. Find thread UID
4. Upload message file
5. Start automation!

## 🆘 Need Help?

- Check **README.md** for detailed instructions
- View console logs for error messages
- Ensure all inputs are correct

---

**🎯 Ready in 2 minutes! 🚀**