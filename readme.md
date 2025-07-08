### 가상환경 설정

- 가상환경 생성

```
python -m venv venv
```

- 가상환경 활성화

```
(mac) source venv/bin/activate
(win) venv\Scripts\activate.bat
```

- 필요 패키지 설치

```
pip install -r requirements.txt
```

### 페이지 확장 예제

- jinja template 상속 (base.html)

```
{% extends "base.html" %}
{% block content %}
<div>새 화면</div>
{% endblock %}
```

### 비고

`tailwind.config.js` (빈파일): vsc extension 활성용
