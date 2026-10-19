# Incident: stale data after silent worker failure (July, AWS)

## Summary
The disk on the AWS box filled up. Redis refused writes (MISCONF), the
Celery worker exited while its container still showed "Up", and the API
served stale data from 17 July. Nothing alerted. It was found during
the migration audit.

## Root causes
1. No log size caps, so container logs filled the disk.
2. Redis could not persist, so it rejected writes.
3. The worker died but its container stayed "Up", so a status check
   was not enough to notice.
4. No monitoring of any kind, so nothing told me.

## What I changed
- Log caps and 2 GB swap on the new OCI boxes
- Weekly certificate renewal (plus nginx reload)
- Container healthchecks
- Alerting (added 19 Oct): uptime monitor on both APIs, a Celery Beat
  heartbeat per worker, an hourly disk check at 80%, and a renewal
  ping. Each alert was fired once on purpose to prove it works.

## Lessons
- "Up" does not mean working. Alert on the work being done, not the
  process existing.
- An alert I have never seen fire is not an alert.
- Scripts that are only described in notes can be missing in
  practice. On 19 Oct I found Football's renewal job was never
  installed, and the deploy script on Job Boards was skipping its last
  steps because of a stdin bug.
