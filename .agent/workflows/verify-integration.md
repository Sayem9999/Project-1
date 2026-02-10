---
description: Verify the full integration of backend agents and frontend dashboard.
---

1. Start the Backend API
```powershell
# In backend directory
python -m uvicorn app.main:app --reload --port 8000
```

2. Start the Frontend Dev Server
```powershell
# In frontend directory
npm run dev
```

// turbo
3. Run E2E Integration Tests
```powershell
# In frontend directory
npx playwright test
```

4. Check Specialist Agent logs
```powershell
# Search for agent_validation_failed in backend output
Get-Content -Path logs/backend.log | Select-String "agent_validation_failed"
```
