# grape-docker-service



# How To Run

python docker api 를 사용하므로, 서버를 실행하는 유저는 docker group 에 속해있어야 합니다.
아래 명령어로 유저가 docker 그룹에 속해있는지 확인하세요.
```
groups | grep docker
```
만일 그룹에 없다면, 아래 명령어로 추가하세요
```
sudo usermod -aG docker <user>
newgrp docker
```

venv 환경을 활성화 한 후, requirements.txt 를 이용하여 종속성을 모두 설치한 후
실행하면 됩니다.

```
python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
python3 run.py
```

