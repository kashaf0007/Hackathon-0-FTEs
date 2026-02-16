# Testing Production Mode

## Current State
- DRY_RUN=true (safe simulation mode)
- Files detected: ✓
- Tasks created: ✓
- Files moved: ✗ (simulated only)

## To Enable Real File Movement

1. **Stop the watcher:**
   - Press Ctrl+C in the terminal running the watcher

2. **Edit .env file:**
   ```bash
   # Change this line:
   DRY_RUN=true
   
   # To this:
   DRY_RUN=false
   ```

3. **Restart the watcher:**
   ```bash
   python main.py
   ```

4. **Test with a new file:**
   ```bash
   echo "Production test" > monitored/prod-test.txt
   ```

5. **Watch the folders:**
   - Low/Medium risk tasks → Execute → Move to Done/
   - High risk tasks → Move to Pending_Approval/

## Expected Behavior

### Low/Medium Risk Tasks (draft_email, organize_files)
- Detected in monitored/
- Task created in Needs_Action/
- Task executed
- Task moved to Done/

### High Risk Tasks (delete_file, send_email)
- Detected in monitored/
- Task created in Needs_Action/
- Approval request created in Pending_Approval/
- Task moved to Pending_Approval/
- Waits for manual approval

### Briefings
- Generate weekly report:
  ```python
  from src.orchestrator.task_processor import TaskProcessor
  processor.generate_weekly_briefing()
  ```
- Report saved to Briefings/

## Safety Notes
- DRY_RUN=true is recommended for testing
- DRY_RUN=false will actually move/modify files
- All operations are logged in Logs/
