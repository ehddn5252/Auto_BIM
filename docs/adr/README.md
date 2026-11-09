# ADR (Architecture Decision Records)

- 파일: `ADR-<3자리 번호>-<주제-kebab>.md`
- 작성: 개발 계열 에이전트(`cad-parser`, `quantity-takeoff`, `cost-estimator`)가 초안 → `bim-ceo` 판정(Gate 2) → 결과를 `docs/decisions.md`에 기록하고 ADR 상태 갱신.

## 템플릿

```markdown
# ADR-000 <제목>
- 상태: 제안 | 승인(D-n) | 반려(D-n) | 대체됨(ADR-m)
- 날짜:
## 맥락 (왜 결정이 필요한가, 관련 F-ID)
## 선택지 (각각 장단점, 라이선스·비용, 근거 docs/research/...)
## 제안
## 결과 (승인 시 무엇이 바뀌나, 되돌리기 비용)
```
