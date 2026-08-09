# Build checklist
<!-- One slice = one feature working end-to-end (never all-database-then-all-frontend).
     Cap: 1 screen. This file is the resume point — builds span sessions without re-explaining.
     [you] = a task only the operator can do (create account, paste key, set spend cap, point DNS),
     written as a plain-language walkthrough; the agent verifies it before the dependent step. -->

## Slice 1: <name>
Sources: plan.md §<sections> · decisions #<ids>
Check (runnable): <command or concrete action + what a good result looks like>
Status: [ ] not started
Steps:
- [ ] checkpoint (commit — a point we can rewind to)
- [ ] <build step>
- [ ] [you] <operator setup task — then the agent verifies>
- [ ] run the check above
- [ ] tick + checkpoint
