# n8n Workflow: `edit-ai-process`

1. **Webhook** (`POST /webhook/edit-ai-process`)
   - Input: `{ job_id, source_path }`
2. **HTTP Request: mark processing**
   - POST `backend:8000/api/workflow/n8n/callback/{job_id}` with `status=processing`
3. **Execute Command: Whisper transcription**
   - `python workers/transcribe.py --input {{$json.source_path}}`
4. **HTTP Request: Director Agent**
   - POST `backend:8000/api/agents/director`
5. **HTTP Request: Cutter/Subtitle/Audio/Color Agents**
   - Parallel fan-out calls
6. **Execute Command: FFmpeg render**
   - Applies silence removal, loudness normalization, subtitle burn-in, and aspect correction
7. **HTTP Request: QC Agent**
8. **IF QC pass?**
   - true -> callback complete with `output_path`
   - false -> callback failed with QC notes
