# Sprint 1 Report
Video Link: https://youtu.be/KBIcYqCa1zg?si=DnRzfa-1ZDQNZN4d
## What's New (User Facing)
* Users can register a new account and log in with their credentials.
* A dashboard page is available after login, showing a placeholder financial overview.
* Integration with Plaid API allows users to link a sandbox bank account.
* An Accounts tab displays linked bank account details.
## Work Summary (Developer Facing)
During Sprint 1, our team focused on building the core foundation of the AI-Finance Tracker app. We set up the Next.js + FastAPI project structure, configured Docker for consistent environments, and implemented user authentication. We then integrated Plaid’s sandbox environment to support bank account linking, and connected the flow so linked accounts display both on the Accounts tab and the Dashboard. Along the way, we learned how to securely handle Plaid tokens and structure API calls between the frontend and backend. The biggest barrier was understanding Plaid’s Link token flow, but after testing with sandbox credentials, we achieved a working integration.
## Unfinished Work
No major unfinished items from Sprint 1. All planned MVP features (auth, dashboard, Plaid linking) were completed.
## Completed Issues/User Stories
Here are links to the issues that we completed in this sprint:
* [URL of issue 1](https://github.com/NoSmoke00/AI-Finance-Tracker---CptS-322-Fall-2025-/issues/13)
* [URL of issue 2](https://github.com/NoSmoke00/AI-Finance-Tracker---CptS-322-Fall-2025-/issues/10)
* [URL of issue n](https://github.com/NoSmoke00/AI-Finance-Tracker---CptS-322-Fall-2025-/issues/9)
## Incomplete Issues/User Stories
N/A
## Code Files for Review
Please review the following code files, which were actively developed during this
sprint, for quality:
N/A
## Retrospective Summary
Here's what went well:
* Team successfully set up full-stack environment (Next.js + FastAPI + Docker).
* Authentication and Plaid integration worked end to end in sandbox.
* Collaboration with Git/GitHub was smooth.
Here's what we'd like to improve:
* More time for error handling (invalid credentials, Plaid failures).
* Better planning for database migrations and schemas.
* Clearer task breakdowns in the sprint backlog.
Here are changes we plan to implement in the next sprint:
* Store and surface account balances in more detail
* Begin designing AI insight module (using OpenAI SDK + pgvector).
Annotations
