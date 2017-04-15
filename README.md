# Video search engine

Flask-based application using MySQL, MongoDB and Neo4j for storing video data and provides interface to search video and show related videos and recommendations.

## Setup

* Install python3, pip, mongodb, python-virtualenv
  ```sudo apt-get install python3 python3-pip mongodb```  
  ```pip3 install virtualenv```  
* Clone repository and setup virtualenv inside folder  
  ```git clone https://github.com/nitish6174/video-search-engine```  
  ```cd <downloaded project path>```  
  ```virtualenv -p python3 venv_py3```  
* Install pip dependencies inside virtualenv  
  ```source venv_py3/bin/activate```  
  ```pip3 install -r requirements.txt```  
* Running :
  - ```python app.py```  
  - Project will be avaiable at ```localhost:5000```
  - Use ```Ctrl-C``` to stop flask server
  - Use ```deactivate``` to exi virtualenv
