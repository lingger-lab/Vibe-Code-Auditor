# ⚡ 빠른 시작 가이드

## 5분 안에 시작하기

### 1단계: 의존성 설치 (1분)

```bash
cd "C:\Users\USER\Desktop\Vibe-Code Auditor"
pip install -r requirements.txt
```

### 2단계: API 키 설정 (1분)

```bash
# .env 파일 생성
copy .env.example .env

# .env 파일을 열어서 API 키 입력
# ANTHROPIC_API_KEY=your_api_key_here
```

**API 키 발급:**
- https://console.anthropic.com/ 방문
- 계정 생성/로그인
- API Keys 메뉴에서 새 키 생성

### 3단계: 테스트 실행 (1분)

```bash
# 예제 프로젝트로 테스트
python -m src.cli.main --path examples/sample-project --mode deployment
```

### 4단계: 실제 프로젝트 분석 (2분)

```bash
# 자신의 프로젝트 분석
python -m src.cli.main --path /path/to/your/project --mode deployment
```

## 📋 기본 명령어

### 배포 관점 (보안, 성능 중심)
```bash
python -m src.cli.main --path <프로젝트경로> --mode deployment
```

### 자가 사용 관점 (가독성, 유지보수 중심)
```bash
python -m src.cli.main --path <프로젝트경로> --mode personal
```

### AI 분석 건너뛰기 (빠른 검증)
```bash
python -m src.cli.main --path <프로젝트경로> --mode deployment --skip-ai
```

## 🎯 사용 예시

### Python 프로젝트
```bash
python -m src.cli.main --path ~/my-django-app --mode deployment
```

### JavaScript 프로젝트
```bash
python -m src.cli.main --path ~/my-react-app --mode deployment
```

### 개인 스크립트 개선
```bash
python -m src.cli.main --path ~/scripts --mode personal
```

## 📊 결과 해석

- 🔴 **Critical**: 즉시 수정 필요 (보안 취약점, 치명적 버그)
- 🟡 **Warning**: 배포 전 검토 권장 (성능, 중복 코드)
- 🟢 **Info**: 개선 제안 (가독성, 스타일)

## 🆘 문제 해결

### API 키 오류
```
❌ 오류: ANTHROPIC_API_KEY가 설정되지 않았습니다.
```
→ `.env` 파일에 API 키 확인

### 모듈 없음 오류
```
ModuleNotFoundError: No module named 'click'
```
→ `pip install -r requirements.txt` 재실행

### 분석 도구 미설치
```
⚠ Pylint is not installed
```
→ 제안된 명령어로 설치: `pip install pylint==3.3.2`

## 📚 다음 단계

1. ✅ [전체 설치 가이드](INSTALL.md) 확인
2. ✅ [상세 사용법](USAGE.md) 학습
3. ✅ [프로젝트 구조](PROJECT_STRUCTURE.md) 이해
4. ✅ CI/CD 통합 (USAGE.md 참고)

## 💡 팁

- **처음 사용**: 예제 프로젝트로 먼저 테스트
- **빠른 검증**: `--skip-ai` 플래그 사용
- **정기 분석**: 주 1회 실행 권장
- **배포 전**: 항상 deployment 모드로 확인

---

문제가 있으시면 [README.md](README.md)를 참고하세요!
