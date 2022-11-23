# YT_transcript_summarizer_chrome_extension

Steps to run summarizer from strach:
```sh
git clone https://github.com/Yashwants19/YT_transcript_summarizer_chrome_extension.git
cd YT_transcript_summarizer_chrome_extension
cd Chrome_extension
npm install
cd ..
pip install -r requirements.txt
pyhton3 app.py
Go to Setting of your browser > Extensions > Enable developer mode (if not enabled) > Load unpacked > 
  Select dist folder from YT_transcript_summarizer_chrome_extension/Chrome_extension
Go any youtube video > Click on extension > Youtube Video Analyzer > Submit
There you Go! -- This will open a tab with summarization and channel stats. 
```
