# 인텔 인공지능 앱 크리에이터 양성과정 - 리액트+DB 실습 프로젝트

이 프로젝트는 인텔 AI 앱 크리에이터 양성과정의 실습을 위해 제작된 **FastAPI 백엔드 + React 프론트엔드 + MySQL 데이터베이스** 연동 예제입니다.

## 🚀 프로젝트 개요 (Project Overview)

이 프로젝트는 수강생들이 웹 애플리케이션의 전체적인 흐름을 이해하고 실습할 수 있도록 구성되었습니다.

### 주요 기능 (Features)
- **사용자 인증 (Authentication)**: JWT 기반 로그인, 회원가입, 비밀번호 암호화 (PBKDF2)
- **권한 관리 (RBAC)**: 일반 사용자(USER)와 관리자(ADMIN) 권한 분리
- **쇼핑몰 시스템**: 아이템 구매, 판매, 인벤토리 관리
- **수강신청 시스템**: 강좌 목록 조회, 수강신청, 수강취소(관리자용)
- **이의신청 시스템**: 비밀글 기능이 포함된 Q&A 게시판

## 🛠️ 기술 스택 (Tech Stack)
- **Backend**: Python FastAPI, Pydantic, SQLAlchemy/MySQL Connector
- **Frontend**: React, TypeScript, Vite
- **Database**: MySQL (MariaDB)

## 🏃‍♂️ 실행 방법 (How to Run)

### 1. 백엔드 (Backend)
```bash
# 가상환경 활성화 (Windows)
.venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 서버 실행
uvicorn main:app --reload
```

### 2. 프론트엔드 (Frontend)
```bash
cd 리액트실습/리액트실습
npm install
npm run dev
```

## 🔑 테스트 계정 (Test Accounts)
- **관리자 (Admin)**
  - ID: `ideabong`
  - PW: `1234`
- **일반 사용자 (User)**
  - ID: (회원가입한 계정)
  - PW: `1234` (기존 더미 데이터 계정도 동일)

## 📂 프로젝트 구조 (Structure)
- `main.py`: FastAPI 메인 애플리케이션 진입점
- `routers/`: API 엔드포인트 정의 (auth, shop, courses 등)
- `services/`: 비즈니스 로직 처리
- `scripts/`: DB 초기화 및 관리용 유틸리티 스크립트 모음
- `리액트실습/`: React 프론트엔드 소스 코드
